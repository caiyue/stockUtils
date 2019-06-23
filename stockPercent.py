#!/usr/bin/python
#coding=utf-8


import  os
import  sys
import  urllib, requests
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

conn = MySQLdb.connect(host='localhost',
                       port=3306,
                       user='root',
                       passwd='123456',
                       db='stockDB',
                       charset='utf8'
                       )

def mysql_init():
    cur = conn.cursor()
    if cur:
        return cur
    else:
        return cur.cursor();


def savePercent(code, name, total, percent, date):
    if code and name and total and percent and date:
        # print code, name, total, percent
        sql = 'insert into %s(code,name,total,percent,date) VALUE  (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % ('stock', code, name, total, percent, date)
        # print sql
        cur = mysql_init()
        cur.execute(sql)


def sendReq(currentDate, reqDate):
    url = 'https://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    formate = {
        "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
        "__VIEWSTATEGENERATOR": "EC4ACD6F",
        "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
        "today": currentDate,  # 20190621
        "sortBy": "stockcode",
        "sortDirection": "asc",
        "alertMsg": "",
        "txtShareholdingDate": reqDate,  # 2019/06/22
        "btnSearch": "搜寻"
    }
    data = urllib.urlencode(formate)
    try:
        res = requests.post(url, data=data, headers=headers)
        html = res.text
    except Exception as e:
        print e

    soup = BeautifulSoup(html, 'lxml')
    tables = soup.findAll('table')
    tab = tables[1]

    index = 0
    code = ''
    name = ''
    total = ''
    percent = ''

    for tr in tab.tbody.findAll('tr'):
        for td in tr.findAll('td'):
            # value = td.findAll('div')
            divValue = td.findAll('div')[1]
            value = divValue.get_text()
            if index == 0: #name
                code = value
                index = index + 1
            elif index == 1:
                name = value
                index = index + 1
            elif index == 2:
                total = value
                index = index + 1
            elif index == 3:
                percent = value
                index = 0 #重置index
        savePercent(code, name, total, percent, reqDate)

    conn.commit(); # 提交到数据库

def mainMethod():

    startDate = '2019/02/18'
    startTimeStamp = datetime.strptime(startDate, "%Y/%m/%d")
    timeStamp = startTimeStamp
    currentDate = datetime.now().strftime('%Y%m%d')
    currentTimeStamp = datetime.now();


    while timeStamp < currentTimeStamp:
        reqDate = datetime.strftime(timeStamp, "%Y/%m/%d");
        sendReq(currentDate, reqDate)
        timeStamp = timeStamp + timedelta(days=1)


if __name__ == '__main__':
    mainMethod()
