# !/usr/bin/python
#-*-coding:utf-8 -*-
import  os
import  sys
import urllib2, urllib, requests
import bs4;
import re
import simplejson
from datetime import datetime, timedelta
import MySQLdb
from stockInfo import StockUtils

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

incomeBaseIncrease = 20
profitBaseIncrease = 10

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
    while True: # 日期不受限制
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


def getHtmlFromUrl(url,utf8coding=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
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
            averageCount = sum(allCountArray)/len(allCountArray)
            endCount = allCountArray[-1]
            maxCount = max(allCountArray)
            isOk = endCount >= maxCount * 0.80 or \
                   endCount >= averageCount
            # 不再根据外资投资比例筛选股票
            if True:
                outArray.append(lastDataItem)

    return outArray

def isGoodStock(code):
    # 获取的是单个季度的数据  例如6.30的财报只是3个月的，而不是6个月的 这里分析单个季度的数据
    li = StockUtils().roeStringForCode(code, returnData=True)
    if li:
        # 最近的季报
        recent = li[0]
        roe = str(recent.roe if recent.roe != '--' else 0)
        incodeIncremnt = recent.incomeRate if recent.incomeRate != '--' else '0'
        profitIncrment = recent.profitRate if recent.profitRate != '--' else '0'
        jll = recent.jinglilv if recent.jinglilv != '--' else '0'

        # roe 在4个季度有周期性，这里取偏低的中间值
        if float(roe) >= 2:
            if (float(incodeIncremnt) >= incomeBaseIncrease and float(profitIncrment) >= profitBaseIncrease and float(jll) >= 15):
                return True
            else:
                return False
        else:
            return False

def printInfo(item, onlyCode=False):
    su = StockUtils()
    if onlyCode:
        syl = su.getHslAndSylForCode(item)
        developPercent = su.getDevelopPercentOfCost(item)
        if not developPercent[0] >= 1 or syl <= 0 or syl > 100:
            return
        name = su.getStockNameFromCode(item)
        holdings = su.getAverageHolding(item)
        increaseHigh = '近两年高速成长' if developPercent[2] else ''
        developDesc = descForCode(developPercent)

        commentCount = su.getCommentNumberIn3MonthsForCode(item)
        ggzc = su.getGGZCStock(item)
        inProgressProject = '在建工程较多' if su.inprogressProject(item) else ''
        # cashIncrease = '现金流增长较多' if su.cashIncrease(item) else ''
        prepareIncrease = '连续3天上涨' if su.prepareToIncreaseLastWeek(item) else ''
        cashDetail = '经营现金流增长' if su.getCashDetail(item) else ''



        print item, name, '市盈率:', syl, ' 评级数:', commentCount, \
            developDesc,  increaseHigh, cashDetail, '高管增持/不变' if ggzc else '',  ' ', \
            inProgressProject, '人均持股:' + str(holdings[1]) + 'W' if holdings[0] else '', prepareIncrease
    else:
        developPercent = su.getDevelopPercentOfCost(item[0])
        syl = su.getHslAndSylForCode(item[0])
        if not developPercent[0] >= 1 or syl <= 0 or syl > 100:
            return
        developDesc = descForCode(developPercent)
        increaseHigh = '近两年高速成长' if developPercent[2] else ''
        commentCount = su.getCommentNumberIn3MonthsForCode(item[0])
        holdings = su.getAverageHolding(item[0])
        ggzc = su.getGGZCStock(item[0])
        inProgressProject = '在建工程较多' if su.inprogressProject(item[0]) else ''
        # cashIncrease = '现金流增长较多' if su.cashIncrease(item[0]) else ''
        prepareIncrease = '连续3天上涨' if su.prepareToIncreaseLastWeek(item[0]) else ''
        cashDetail = '经营现金流增长' if su.getCashDetail(item[0]) else ''



        print item[0], item[1], item[3], '市盈率:', syl, ' 评级数:', commentCount, \
        developDesc,increaseHigh, cashDetail, '高管增持/不变' if ggzc else '', ' ', \
            inProgressProject, '人均持股:' + str(holdings[1]) + 'W' if holdings[0] else '', prepareIncrease

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

ranks = []
def holdingRank(code):
    if code:
        su = StockUtils()
        holdings = su.getAverageHolding(code)
        name = su.getStockNameFromCode(code)
        sdltPercent = su.sdltgdTotalPercent(code)
        commentCount = su.getCommentNumberIn3MonthsForCode(code)
        percentOfFund = su.stockPercentOfFund(code)
        developPercentHigh = su.getDevelopPercentOfCost(code)
        prepareIncrease = su.prepareToIncreaseLastWeek(code)
        syl = su.getHslAndSylForCode(code)
        cashIncrease = su.getCashDetail(code)

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

            if holdings and len(holdings) > 0:
                ranks.append({
                    'code': code,
                    'name': name,
                    'syl': syl,
                    'sdltPercent': sdltPercent, #十大流通股占比,
                    'commentCount': commentCount, #券商评级数量,
                    'percentOfFund': percentOfFund, #基金流通股占比
                    'count': holdings[0], #最近的持股金额
                    'je': holdings[1], #人均总额
                    'counts': holdings[2], #人均持股数据,
                    'holdingsCount': holdings[3], #股东人数

                    'jll': jll,
                    'incodeIncremnt': incodeIncremnt,
                    'profitIncrment': profitIncrment,

                    'devPercent': 1 if developPercentHigh[0] >= 1 else 0,
                    'increaseHight': 1 if developPercentHigh[2] else 0,

                    'prepareIncrease': prepareIncrease,

                    'cashIncrease': cashIncrease
                })
        except Exception,e:
            print 'holing rank:', code


def formatStock(arr):
    for item in arr:
        code = item['code']
        name = item['name']
        syl = item['syl']
        holdingsCount = item['holdingsCount'] #股东数
        sdltPercent = item['sdltPercent']
        commentCount = item['commentCount']
        percentOfFund = item['percentOfFund']
        je = item['je']
        counts = item['counts'] #人均持股数
        jll = item['jll']
        devPercent= item['devPercent']
        increaseHight = item['increaseHight']

        incodeIncremnt = item['incodeIncremnt']
        profitIncrment = item['profitIncrment']

        prepareIncrease = item['prepareIncrease']

        cashIncrease = item['cashIncrease']

        # 因为是人均持股金额或者调研数量，所以只要业绩不是特别差就可以
        isOk = not (incodeIncremnt <= incomeBaseIncrease and profitIncrment <= profitBaseIncrease)
        # 如果超过80w就不再过滤评级数量
        isCollect = (len(je) >= 1 and je[0] >= 20 and increaseHight and jll >= 8) or \
                    (len(je) >= 1 and je[0] >= 100 and jll >= 12) or \
                    (len(je) >= 3 and je[0] > je[1] and je[0] > je[2] and (jll >= 15 or (increaseHight and jll >= 8))) or \
                    (len(je) >= 1 and je[0] >= 10 and jll >= 15 and holdingsCount[0] <= 15000) or \
                    (len(je) >= 1 and je[0] >= 50 and jll >= 12 and holdingsCount[0] <= 20000) or \
                    (len(holdingsCount) >= 3 and holdingsCount[0] <= holdingsCount[1] and holdingsCount[0] <= holdingsCount[2] and jll >= 15) or \
                    (len(counts) >= 3 and counts[0] > counts[1] and counts[0] > counts[2] and jll >= 15) or \
                    (len(je) >= 3 and je[0] >= je[1] and je[0] >= je[2] and increaseHight and (jll >= 15 or jll == 0))# 有些新股没有数据所以这里就简单判断下


        # 资金集中，净利率大于10%，这样才算是龙头企业，否则量大，利润率低的很难成为龙头
        if isCollect and isOk and 100 > syl > 0:
            jllDesc = '净利率很高' if jll >= 20 else '净利率高' if jll >= 12 else ''
            devDesc = '研发占比很高' if devPercent else ''
            increaseHight = '近两年高速成长' if increaseHight else ''
            prepareIncreaseDesc = '连续3天上涨' if prepareIncrease else ''
            cashDesc = '经营现金流增长' if cashIncrease else ''
            currentIncreaseHight = '当前季度增长高速' if incodeIncremnt >= 30 and profitIncrment >= 30 else \
                ('当前季度增长超高速' if incodeIncremnt >= 40 and profitIncrment >= 40 else '')

            print code, name, '市盈率:', syl, ' 评级数:', commentCount, je, counts, devDesc, increaseHight, currentIncreaseHight, cashDesc, ' 十大流通股总计:', str(
                sdltPercent) if sdltPercent >= 20 else '', \
                '基金流通股占比:' + str(percentOfFund) if percentOfFund > 5 else '', jllDesc, '最新股东数:' + str(holdingsCount[0]), prepareIncreaseDesc
        else:
            pass


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
        "券商调研 >= 10"
        "换手率下降"
        "当前热点或者有政策利好"
        "净利率 >= 10%"
     ==============================================

    买入时机：
    1、下跌阶段：地量，说明卖盘已经没有，可以准备建仓
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
    outArray = getSortedValue()
    codeArray = [x[0] for x in outArray]
    if outArray:
        outArray = sorted(outArray, key=lambda x: float(x[3]), reverse=True)
        print '\n外资持股增长+业绩高速增长+净利率高如下:'
        for item in outArray:
            # 调试用
            if item[0] == '300726':
                print 'aa'
            isgood = isGoodStock(item[0])
            if isgood:
                printInfo(item, False)


    print '\n外资暂无持股，但是业绩很好的股票：'
    codes = su.getAllStockList()
    for code in codes:
        holdingRank(code)
        if code in codeArray:
            continue
        else:
            ret = isGoodStock(code)
            if ret:
                printInfo(code, True)

    print '\n人均持股金额排行：'
    ret = sorted(ranks, key=lambda x: x['count'], reverse=True)
    formatStock(ret)

    print '\n评级数量排行：'
    ret = sorted(ranks, key=lambda x: x['commentCount'], reverse=True)
    formatStock(ret)

    print '\n股东人数排行：'
    ret = sorted(ranks, key=lambda x: x['holdingsCount'], reverse=False)
    formatStock(ret)

    print '\n基金流通股占比排行：'
    ret = sorted(ranks, key=lambda x: x['percentOfFund'], reverse=True)
    formatStock(ret)

    print '\n净利率排行：'
    ret = sorted(ranks, key=lambda x: x['jll'], reverse=True)
    formatStock(ret)


if __name__ == '__main__':
    mainMethod()
