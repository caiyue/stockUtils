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
        sql = 'insert into %s(code,name,total,percent,date) value (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % ('stock', code, name, total, percent, hold_date)
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

    # print good stock
    return filterGood(ret)

def filterGood(ret):
    outArray = []
    for item in ret:
        if item and len(item) > 0:
            code = item[0][0]
            lastDataItem = item[-1]
            allCountArray = [int(x[2]) for x in item]
            averageCount = sum(allCountArray)/len(allCountArray)
            startCount = allCountArray[0]
            endCount = allCountArray[-1]
            maxCount = max(allCountArray)
            lastPercent = float(lastDataItem[3])
            isOk = (endCount >= maxCount * 0.85 and lastPercent >= 0.5) or (endCount >= averageCount and lastPercent >= 0.5) or (endCount < startCount and lastPercent > 1.0)
            if isOk:
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

        if float(roe) > 4 \
                and float(jll) >= 20 \
                and \
                (
                        (float(incodeIncremnt) >= 25 and float(profitIncrment) >= 15)
                        or (float(incodeIncremnt) >= 20 and float(profitIncrment) >= 28))\
                :
            return True
        else:
            return False

def printInfo(item, onlyCode=False):
    if onlyCode:
        averageHoliding = StockUtils().getAverageHolding(item)
        name = StockUtils().getStockNameFromCode(item)
        developPercent = descForCode(StockUtils().getDevelopPercentOfCost(item))
        ggzc = StockUtils().getGGZCStock(item)
        count = StockUtils().getQFIICount(item)
        countStr = '总:' + str(count[0]) +  ' 【社:' + str(count[1]) + ' Q:' + str(count[2]) + ' 保:' + str(count[3]) + ' 券:' + str(count[4]) + ' 信:' + str(count[5]) + '】' \
            if count[0] > 0 else ''
        print item, name, developPercent, countStr, '高管增持' if ggzc else '',  ' ', averageHoliding[1]
    else:
        averageHoliding = StockUtils().getAverageHolding(item[0])
        developPercent = descForCode(StockUtils().getDevelopPercentOfCost(item[0]))
        ggzc = StockUtils().getGGZCStock(item[0])
        count = StockUtils().getQFIICount(item[0])
        countStr = '总:' + str(count[0]) + ' 【社:' + str(count[1]) + ' Q:' + str(count[2]) + ' 保:' + str(count[3]) + ' 券:' + str(count[4]) + ' 信:' + str(count[5]) + '】'\
            if count[0] > 0 else ''
        print item[0], item[1], item[3], \
        str(int(item[2]) / 10000) + '万股', \
        '评级数:' + str(StockUtils().getCommentNumberIn3MonthsForCode(item[0])), \
        developPercent, countStr, '高管增持' if ggzc else '', ' ', averageHoliding[1]

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

def mainMethod():
    currentTimeStamp = datetime.now()
    #
    currentDate = datetime.strftime(currentTimeStamp, "%Y-%m-%d")
    fourMonthAgoTimeStamp = currentTimeStamp - timedelta(days=120)
    fourMonthAgoDate = datetime.strftime(fourMonthAgoTimeStamp, "%Y-%m-%d")
    #
    #sendReq(fourMonthAgoDate, currentDate)

    # 机构评级数量排行,最近3个月至少10个买入/增持推荐
    outArray = getSortedValue()
    codeArray = [x[0] for x in outArray]
    otherDevelopHighArray = []

    if outArray:
        outArray = sorted(outArray, key=lambda x: float(x[3]), reverse=True)
        print '\n外资持股增长+业绩高速增长如下:'
        for item in outArray:
            # 调试用
            isgood = isGoodStock(item[0])
            developPercentHigh = StockUtils().getDevelopPercentOfCost(item[0])
            if isgood:
                printInfo(item, False)
            elif developPercentHigh[0] >= 1:
                otherDevelopHighArray.append(item)
        #其他研发比例高的企业
        print '\n外资增持+业绩增速/净利率一般:：'
        for item in otherDevelopHighArray:
            printInfo(item, False)

        # 外资持股比例排行
        print '\n\n外资持股排行,共%s个' % len(outArray)
        for item in outArray:
            printInfo(item, False)

    print '\n外资暂无持股，但是业绩很好的股票：'
    codes = StockUtils().getAllStockList()
    for code in codes:
        if code in codeArray:
            continue
        else:
            ret = isGoodStock(code)
            if ret:
                printInfo(code, True)


if __name__ == '__main__':
    mainMethod()
