# !/usr/bin/python
# -*-coding:utf-8 -*-
import os
import sys
import urllib2, urllib, requests
import bs4;
import re, json
import simplejson
from datetime import datetime, timedelta
import MySQLdb
import threading
from stockInfo import StockUtils
from send_email import sendMail

import sys

reload(sys)
sys.setdefaultencoding('utf8')

conn = MySQLdb.connect(host='localhost',
                       port=3306,
                       user='root',
                       passwd='123456',
                       db='stockDB',
                       charset='utf8'
                       )

shurl = 'http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTongHoldingRatioList?callback=sina_15618815495718682370855167358&page=%s&num=40&type=sh&start=%s&end=%s'
szurl = 'http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTongHoldingRatioList?callback=sina_15618815495718682370855167358&page=%s&num=40&type=sz&start=%s&end=%s'

incomeBaseIncrease = 25
profitBaseIncrease = 25

sylLimit = 250
shizhiLimit = 20
jllLimit = 15

def mysql_init():
    cur = conn.cursor()
    if cur:
        return cur
    else:
        return cur.cursor()


def executeSQL(sql):
    if sql:
        cusor = mysql_init()
        cusor.execute(sql)
        return cusor
    else:
        return


def savePercent(code, name, total, percent, hold_date):
    if code and name and total and percent and hold_date:
        sql = 'insert into %s(code,name,total,percent,date) value (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % \
              ('stock', code, name, total, percent, hold_date)
        print sql
        executeSQL(sql)


def stripString(res):
    if not res:
        return None
    par = re.compile('\(.*?\)')
    li = re.findall(par, res)
    if li:
        return li[0]
    else:
        return None


def sendReq(startDate, endDate):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

    page = 1
    while True:  # 日期不受限制
        shReqUrl = shurl % (page, startDate, endDate)
        szReqUrl = szurl % (page, startDate, endDate)

        shres = stripString(getHtmlFromUrl(shReqUrl))
        szres = stripString(getHtmlFromUrl(szReqUrl))

        print 'page:%d, shres:%s, szres:%s' % (page, shres, szres)
        if shres and szres:
            page = page + 1
            shret = simplejson.loads(shres[1: -1])
            szret = simplejson.loads(szres[1: -1])

            if len(shret['result']['data']) == 0 and len(szret['result']['data']) == 0:
                print '获取数据完毕～'
                break
            if shret:
                saveValueFromJson(shret)
            if szret:
                saveValueFromJson(szret)

            if not shret and not szret:
                break
        else:
            break


def saveValueFromJson(json):
    if json and json['result']:
        data = json['result']['data']
        if isinstance(data, dict):
            datalist = data['s_list']
            if datalist and isinstance(datalist, list) and len(datalist) > 0:
                for item in datalist:
                    name = str(item['name'])
                    code = str(item['symbol'])
                    hold_num = str(item['hold_num'])
                    hold_percent = str(item['hold_ratio'])
                    hold_date = str(item['hold_date'])

                    savePercent(code, name, hold_num, hold_percent, hold_date)
        conn.commit()  # 提交数据库
    else:
        return


def getHtmlFromUrl(url, utf8coding=False):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        req = urllib2.Request(url, headers=headers)
        ret = urllib2.urlopen(req, timeout=10)
        res = None
        if utf8coding:
            res = ret.read().decode('gbk', 'ignore').encode('utf-8')
        else:
            res = ret.read()
    except Exception, e:
        print 'exception  occur', url
        return None
    return res


def returnPercent(tu):
    if len(tu) == 5:
        return tu[3]
    else:
        return 0


def getSortedValue():
    sql = 'select code, name, total, percent, date from stock order by name, date asc'
    cusor = executeSQL(sql)
    result = cusor.fetchall()
    ret = []
    codeNum = None
    codeData = []
    for i in result:
        code = i[0]
        if codeNum and codeNum != code:
            ret.append(codeData)
            codeData = []
        else:
            codeData.append(i)
        codeNum = code
    return filterGood(ret)


def filterGood(ret):
    outArray = []
    for item in ret:
        if item and len(item) > 0:
            code = item[0][0]
            lastDataItem = item[-1]
            allCountArray = [int(x[2]) for x in item]
            averageCount = sum(allCountArray) / len(allCountArray)
            startCount = allCountArray[0]
            endCount = allCountArray[-1]
            maxCount = max(allCountArray)
            isOk = endCount >= maxCount * 0.80 > startCount
            # 不再根据外资投资比例筛选股票
            if isOk:
                outArray.append(lastDataItem)

    return outArray

def descForCode(ret):
    code = ret[0]
    percent = ret[1]
    if code == 1:
        return '研发占比高%.5s' % percent
    elif code == 2:
        return '研发占比较高%.5s' % percent
    elif code == 3:
        return '研发占比很高%.5s' % percent
    return ''


ranks = {}
cachedThreads = []
# 最多同时发50个线程
pool_sema = threading.BoundedSemaphore(value=10)
def multiThradExector(code, lock):
    su = StockUtils()
    syl = su.getHslAndSylForCode(code)
    if syl < 0 or syl > sylLimit:
        lock.release()
        return
    holdings = su.getAverageHolding(code)
    name = su.getStockNameFromCode(code)
    sdPercent = su.sdgdTotalPercent(code)
    commentCount = su.getCommentNumberIn3MonthsForCode(code)
    fundInfo = su.fundInfoOfStock(code)
    developPercentHigh = su.getDevelopPercentOfCost(code)
    prepareIncrease = su.prepareToIncreaseLastWeek(code)
    cashIncrease = su.getCashDetail(code)
    prepareJieJinPercent = su.PrePareToJieJin(code)
    bill = su.getCompanyBill(code)[1]
    # 净利率
    roe = su.roeStringForCode(code, returnData=True)
    jll = 0
    try:
        if roe:
            # 最近的季报
            recent = roe[0]
            jll = float(recent.jinglilv if recent.jinglilv != '--' else '0')
            incodeIncremnt = float(recent.incomeRate if recent.incomeRate != '--' else 0)
            profitIncrment = float(recent.profitRate if recent.profitRate != '--' else 0)
            income = recent.income
            profit = recent.profit

        if code and name and holdings and len(holdings) > 0:
            billPercent = getNumFromStr(bill) * 1.0 / getNumFromStr(income)
            ranks[code] = {
                'code': code,
                'name': name,
                'syl': syl,
                'sdPercent': sdPercent,  # 十大股东占比,
                'commentCount': commentCount,  # 券商评级数量,
                'percentOfFund': fundInfo[0],  # 基金流通股占比
                'countOfFund': fundInfo[1],  # 机构数量
                'count': holdings[0],  # 最近的持股金额
                'je': holdings[1],  # 人均总额
                'counts': holdings[2],  # 人均持股数据,
                'holdingsCount': holdings[3],  # 股东人数

                'jll': jll,
                'income': income,
                'profit': profit,
                'incodeIncremnt': incodeIncremnt,
                'profitIncrment': profitIncrment,
                'bill': bill,
                'billPercent': billPercent,  # 应收款占比

                'devPercent': developPercentHigh[1],
                'devHigh': developPercentHigh[0] >= 1,
                'increaseHight': 1 if developPercentHigh[2] else 0,

                'prepareIncrease': prepareIncrease,
                'cashIncrease': cashIncrease,
                'prepareJieJinPercent': prepareJieJinPercent
            }
    except Exception, e:
        print 'holing rank:', code
    finally:
        lock.release()

def holdingRank(code):
    if code not in ranks:
        # 如果能拿到锁就启动线程，在线程结束后释放锁
        pool_sema.acquire(blocking=True)
        thread = threading.Thread(target=multiThradExector, args=(code, pool_sema))
        cachedThreads.append(thread)
        thread.start()


def prepareIncreaseFunc(prepareIncrease):
    if prepareIncrease and prepareIncrease[0]:
        return '连续3天上涨[%s]' %  prepareIncrease[1]
    else:
        return ''

def getNumFromStr(income):
    if income:
        if isinstance(income, float):
            return income
        elif u'万' in income:
            return float(income[0: -1]) * 10000
        elif u'亿' in income:
            return float(income[0: -1]) * 10000 * 10000
        else:
            return float(income)
    return 0

def incomeIs2Small(income):
    return getNumFromStr(income) < 15000 * 10000

def itemIsGood(item):
    code = item['code']
    name = item['name']
    syl = item['syl']
    holdingsCount = item['holdingsCount']  # 股东数
    sdPercent = item['sdPercent']
    commentCount = item['commentCount']
    percentOfFund = item['percentOfFund']
    countOfFund = item['countOfFund']
    je = item['je']
    counts = item['counts']  # 人均持股数
    jll = item['jll']
    devPercent = item['devPercent']
    increaseHight = item['increaseHight']

    income = item['income']
    profit = item['profit']

    incodeIncremnt = item['incodeIncremnt']
    profitIncrment = item['profitIncrment']
    prepareIncrease = item['prepareIncrease']
    cashIncrease = item['cashIncrease']

    # 如果单个季度收入低于1.5亿，直接忽略，规模小，等待成长太艰难了
    if incomeIs2Small(income):
        return False

    # 一般是地产、银行等不能告诉成长的企业
    if syl <= 10:
        return False

    # 如果证券公司都不关注，而且过去业绩不咋地，那当前高增长都是暂时的
    if commentCount <= 0:
        return False

    #如果筹码太散，股价不容易拉升(无论过去是否告诉成长)
    if sdPercent < 50:
        return False

    # 如果净利率太低，肯定是苦逼行业，或者经营不咋地的公司，伟大的企业都是能赚钱的
    if jll < jllLimit:
        return False

    #  还没有资金进入
    if len(je) >= 1 and je[0] < shizhiLimit:
        return False

    # 针对近两年不是高速成长的企业，需要这么过滤下
    # 针对人均持股较少的股，如果净利率低也就不再关注了,肯定是垃圾股
    # 针对人均持股较少的股，如果不是资金连续聚集，也不再关注了

    # 当季度业绩至少要达到 incomeBaseIncrease profitBaseIncrease的要求
    # 或者 资金连续3次递增       x3 >= x2 and x3 >= x1
    # 或者 人均持股连续3次递增    x3 >= x2 and x3 >= x1
    # 或者 股东数连续3次递减     x3 <= x2 and x3 <= x1
    # 或者 过去连续两年业绩很好   increaseHight
    # 或者 当前季度季度业绩很好   incodeIncremnt >= 30 and profitIncrment >= 30
    # 或者 人均持股金额 大于100w

    # 筛选财务指标：企业增长不能太差, >= 20 && >= 10,但是茅台，海天不可能增速那么快，所以也需要特殊处理下,或者最近两年高速成长
    isOK = False
    if not increaseHight:
        if not (incodeIncremnt >= 40 and profitIncrment >= 40):
            return False
        isOK = True
    else:
        isOK = incodeIncremnt >= 5 and profitIncrment >= 5

    # 资金聚集筛选条件
    # 准备牛逼 /  过去2年牛逼  / 当前牛逼  / 努力牛逼  / 已经很牛逼
    isCollect = (len(je) >= 3 and je[0] > je[1] > je[2]) or \
                increaseHight or \
                (incodeIncremnt >= 40 and profitIncrment >= 40) or \
                (len(je) >= 1 and je[0] >= 100)

    if isOK and isCollect:
        return True
    return False

def printInfo(item):
    code = item['code']
    name = item['name']
    syl = item['syl']
    holdingsCount = item['holdingsCount']  # 股东数
    sdPercent = item['sdPercent']
    commentCount = item['commentCount']
    percentOfFund = item['percentOfFund']
    countOfFund = item['countOfFund']
    je = item['je']
    counts = item['counts']  # 人均持股数
    jll = item['jll']
    devPercent = item['devPercent']
    devHigh = item['devHigh']
    increaseHight = item['increaseHight']

    income = item['income']
    profit = item['profit']
    incodeIncremnt = item['incodeIncremnt']
    profitIncrment = item['profitIncrment']
    bill = item['bill']
    billPercent = item['billPercent']

    prepareIncrease = item['prepareIncrease']
    cashIncrease = item['cashIncrease']
    prepareJieJinPercent = item['prepareJieJinPercent']

    devDesc = '研发占比%.2f' % devPercent
    increaseHight = '近两年高速成长' if increaseHight else ''
    cashDesc = '经营现金流增长' if cashIncrease else ''
    currentIncreaseHight = '当季超高增长:[%s/%s]' % (
        incodeIncremnt, profitIncrment) if incodeIncremnt >= 40 and profitIncrment >= 40 else \
        ('当季高增长' if incodeIncremnt >= 30 and profitIncrment >= 30 else '')
    currentHodingCount = holdingsCount[0] if holdingsCount and len(holdingsCount) > 0 else 0
    sdPercentDesc = '十大股东总计:' + str(sdPercent)
    fundPercentDesc = '基金流通股占比:' + str(percentOfFund) if percentOfFund > 5 else ''
    fundCountDesc = '机构数量:%d' % countOfFund
    prepareIncreaseDesc = prepareIncreaseFunc(prepareIncrease)
    prepareJieJinDesc = '>=0.5倍数准备解禁' if prepareJieJinPercent >= 0.5 else ''
    billDesc = '应收款:%.fW|%%%.f' % (float(bill)/10000, billPercent * 100)

    print code, name, '市盈率:', syl, '评级数:', commentCount, je, counts, '利润:%s/%s' % (
    income, profit), devDesc, increaseHight, currentIncreaseHight, cashDesc, sdPercentDesc, \
        fundPercentDesc, fundCountDesc, '股东数:' + str(currentHodingCount), prepareIncreaseDesc, prepareJieJinDesc, billDesc


def formatStock(arr):
    for item in arr:
        if itemIsGood(item):
          printInfo(item)

def princleple():
    print '''
    买入类型
    
    0、市场空间必须是巨大的
    1、产品净利率 >= 15 %
    2、年资产收益率 >= 15 %
    3、研发占比 >= 5 % 越高越好
    4、负债率 <= 50 （可选）
    5、连续三年营收、利润高增长
    6、市场空间足够大
    
    7、必须是行业龙头,根据竞争对手对比来确认，只买龙头、龙头【市占率>= 15】
    8、收入增长率 >= 20 %
    9、利润增长率 >= 20 %，业务利润需要是90%以上,不能存在很高投资收益
    
    10、换手率 <= 3.0 % 越低越好，人均持股金额高，筹码趋于集中
    11、没有大规模的高管减持行为，可以小量减持
    
    12、在建工程较多 >= 5500，说明扩张速度较快
    13、现金流增长 >= 3000，说明现金流增长稳健
    14、产能利用率 >= 80%，说明订单较多
    
    
    14、外资持股比例持续增长或者大比例持股 (可选)
    
     ==============================================
        "市场空间巨大的"
        "连续三年高增长"
        "市占率"
        "资金聚集的行业龙头"
        "券商调研 >= 10 & 预期高"
        "换手率下降"
        "当前热点或者有政策利好"
        "净利率 >= 10%"
     ==============================================

    买入时机：
    1、【W】形缩量上涨，可以准备建仓
    卖出时机：
    1、上涨阶段：天量卖出，表示所有的上扬力量已经出尽，后期上扬没有资金跟进
    '''

def mainMethod():
    princleple()
    currentTimeStamp = datetime.now()
    su = StockUtils()
    currentDate = datetime.strftime(currentTimeStamp, "%Y-%m-%d")
    fourMonthAgoTimeStamp = currentTimeStamp - timedelta(days=120)
    fourMonthAgoDate = datetime.strftime(fourMonthAgoTimeStamp, "%Y-%m-%d")
    #
    #sendReq(fourMonthAgoDate, currentDate)
    codes = su.getAllStockList()
    #codes = ['603218', '300408', '603466']
    for code in codes:
        holdingRank(code)

    # 等待所有线程结束
    for thread in cachedThreads:
        thread.join()

    print '\n外资持股增长+业绩高速增长+净利率高如下:'
    outArray = getSortedValue()
    codeArray = [x[0] for x in outArray]
    if outArray:
        outArray = sorted(outArray, key=lambda x: float(x[3]), reverse=True)
        for item in outArray:
            code = item[0]
            value = ranks[code] if code in ranks else None
            if value and itemIsGood(value):
                printInfo(value)

    # 直接结果
    values = ranks.values()
    print '\n人均持股金额排行：'
    ret = sorted(values, key=lambda x: x['count'], reverse=True)
    formatStock(ret)

    print '\n基金占比排行：'
    ret = sorted(values, key=lambda x: float(x['percentOfFund']), reverse=True)
    formatStock(ret)

    print '\n基金数量排行：'
    ret = sorted(values, key=lambda x: x['countOfFund'], reverse=True)
    formatStock(ret)

    print '\n券商推荐排行：'
    ret = sorted(values, key=lambda x: x['commentCount'], reverse=True)
    formatStock(ret)

    print '\n利润增速排行：'
    ret = sorted(values, key=lambda x: x['profitIncrment'], reverse=True)
    formatStock(ret)

    print '\n研发占比排行：'
    ret = sorted(values, key=lambda x: x['devPercent'], reverse=True)
    formatStock(ret)

    print '\n股东人数排行：'
    ret = sorted(values, key=lambda x: x['holdingsCount'], reverse=False)
    formatStock(ret)

    print '\n公司应收款占比排行：'
    ret = sorted(values, key=lambda x: float(x['billPercent']), reverse=False)
    formatStock(ret)

    print '\n解禁占比占比排行：'
    ret = sorted(values, key=lambda x: x['prepareJieJinPercent'], reverse=True)
    formatStock(ret)

    def filter_increase(n):
        return n['prepareIncrease'] and n['prepareIncrease'][0];
    increaseList = filter(filter_increase, values)
    s = ''
    for item in increaseList:
        if itemIsGood(item):
            s = s + item['code'] + ' ' + item['name'] + ' ' + str(item['je']) + ' ' + str(item['incodeIncremnt']) + '/' + str(item['profitIncrment']) + '\n'
    sendMail('筛选列表【W】缩量买入', s)

if __name__ == '__main__':
    mainMethod()
