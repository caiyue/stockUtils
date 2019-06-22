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
from datetime import datetime
import os.path as fpath
from bs4 import BeautifulSoup
import pickle,pprint
from mysqlOperation import mysqlOp
from send_email import sendMail



def mainMethod():
    url = 'https://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    formate = {
        "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
        "__VIEWSTATEGENERATOR": "EC4ACD6F",
        "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
        "today": "20190622",
        "sortBy": "stockcode",
        "sortDirection": "asc",
        "alertMsg": "",
        "txtShareholdingDate": "2019/02/18",
        "btnSearch": "搜寻"
    }
    data = urllib.urlencode(formate)
    res = requests.post(url, data=data, headers=headers)
    html = res.text

    soup = BeautifulSoup(html, 'lxml')
    tables = soup.findAll('table')
    tab = tables[1]
    for tr in tab.tbody.findAll('tr'):
        for td in tr.findAll('td'):
            value = td.findAll('div')[1]
            print value.getText()



if __name__ == '__main__':
    mainMethod()
