#!/usr/bin/python
#coding=utf-8


import  os
import  sys
import urllib2, urllib, requests
import bs4;
import  re
import simplejson
import  time
import socket
from datetime import datetime, timedelta
import os.path as fpath
from bs4 import BeautifulSoup
import pickle,pprint
from mysqlOperation import mysqlOp
from send_email import sendMail
import MySQLdb
import matplotlib.pyplot as plt
from matplotlib import pyplot

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
        # print code, name, total, percent
        sql = 'insert into %s(code,name,total,percent,date) VALUE  (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % ('stock', code, name, total, percent, hold_date)
        executeSQL(sql)


def stripString(res):
    par = re.compile('\(.*?\)')
    li = re.findall(par, res)
    if li:
        return li[0]
    else:
        return None

def sendReq(startDate, endDate):
    url = 'https://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

    page = 1
    while True: # 日期不受限制
        shReqUrl = shurl % (page, startDate, endDate)
        szReqUrl = szurl % (page, startDate, endDate)

        shres = stripString(getHtmlFromUrl(shReqUrl))
        szres = stripString(getHtmlFromUrl(szReqUrl))

        print 'page:%d, shres:%s, szres:%s' % (page, shres, szres)
        if shres or szres:
            page = page + 1
            shret = simplejson.loads(shres[1: -1])
            szret = simplejson.loads(szres[1: -1])
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
                    name = item['name']
                    code = item['symbol']
                    hold_num = item['hold_num']
                    hold_percent = item['hold_ratio']
                    hold_date = item['hold_date']

                    savePercent(code, name, hold_num, hold_percent, hold_date)
        conn.commit()  # 提交数据库
    else:
        return

def getHtmlFromUrl(url,utf8coding=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        req = urllib2.Request(url, headers=headers)
        ret = urllib2.urlopen(req)
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

def drawImage(data):
    fig = plt.figure(figsize=(10, 6))
    # unrate[]

    index = 0
    while index <= len(data):
        needData = data[index: index + 2]

        data1 = needData[0]
        name1 = data1[0][1]
        data2 = needData[1]
        name2 = data2[0][1]

        x = []
        if len(data1) > len(data2):
            x = map(lambda a: a[4], data1)
        else:
            x = map(lambda a: a[4], data2)

        y1 = map(lambda a: float(returnPercent(a)), data1)
        y2 = map(lambda a: float(returnPercent(a)), data2)

        plt.plot(x, y1, marker='o', mec='r', mfc='w', label='y1')
        plt.plot(x, y2, marker='o', mec='r', mfc='w', label='y2')
        plt.legend()

        plt.xlabel('Date')
        plt.ylabel("Percent")
        plt.title(name1 + '&' + name2)
        pyplot.yticks([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50])
        plt.savefig('./Img/%s&%s' % (name1, name2), dpi=900)

        index = index + 2



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

    # ret
    # drawImage(ret)


    # print good stock
    filterGood(ret)

def filterGood(ret):
    outArray = []
    for item in ret:
        if item and len(item) > 0:
            lastDataItem = item[-1]
            allCountArray = [int(x[2]) for x in item]
            averageCount = sum(allCountArray)/len(allCountArray)
            startCount = allCountArray[0]
            endCount = allCountArray[-1]
            maxCount = max(allCountArray)
            lastPercent = float(lastDataItem[3])
            if startCount < endCount and (endCount >= maxCount and lastPercent >= 0.8) or (endCount > averageCount and lastPercent >= 1.0):
            # if start < end and end > average and lastPercent > 1.0:

                outArray.append(lastDataItem)
                # print lastDataItem[0], lastDataItem[1], str(lastPercent)+'%'

    if outArray:
        outArray = sorted(outArray, key=lambda x: x[3], reverse=True)
        print '共%d只增持股票' % len(outArray)
        for item in outArray:
            print item[0], item[1], item[3], str(int(item[2])/10000) + '万股'







def mainMethod():

    # startDate = '2019/02/18'
    # startTimeStamp = datetime.strptime(startDate, "%Y/%m/%d")
    # timeStamp = startTimeStamp
    # currentDate = datetime.now().strftime('%Y%m%d')
    currentTimeStamp = datetime.now()

    # html = getHtmlFromUrl(shurl)
    # # print html
    # VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', html, re.I)[0]
    # VIEWSTATEGENERATOR = re.findall(r'<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />', html, re.I)[0]
    # EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />',
    #                              html, re.I)[0]

    count = 90
    index = 0
    # while index <= count:
    currentDate = datetime.strftime(currentTimeStamp, "%Y-%m-%d")
    fourMonthAgoTimeStamp = currentTimeStamp - timedelta(days=120)
    fourMonthAgoDate = datetime.strftime(fourMonthAgoTimeStamp, "%Y-%m-%d")

    sendReq(fourMonthAgoDate, currentDate)
    getSortedValue()

if __name__ == '__main__':
    mainMethod()
