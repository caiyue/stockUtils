#!/usr/bin/python
#coding=utf-8

import requests
import urllib2
import re
import json
url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx'

def get_hiddenvalue(url):
    request=urllib2.Request(url)
    reponse=urllib2.urlopen(request)
    resu=reponse.read()
    html = resu.decode('utf-8') # python3
    VIEWSTATE = re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', html, re.I)
    EVENTVALIDATION = re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', html, re.I)
    print VIEWSTATE, EVENTVALIDATION
    return VIEWSTATE[0], EVENTVALIDATION[0]

VIEWSTATE, EVENTVALIDATION=get_hiddenvalue(url)
data = {
'__EVENTVALIDATION':EVENTVALIDATION,
'__VIEWSTATE':VIEWSTATE,
'__VIEWSTATEGENERATOR':'EC4ACD6F',
'sortBy': 'stockcode',
'sortDirection': 'asc',
'txtShareholdingDate': '2020/03/04',
'today': '20200307',
'btnSearch': '搜尋'
}

html_post = requests.post(url, data=data)
print(html_post.text)

import requests
from bs4 import BeautifulSoup
#
# headers = {
# 'Upgrade-Insecure-Requests':'1',
# 'Connection':'keep-alive',
# 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2700.0 Safari/537.36',
# 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
# 'Accept-Encoding':'gzip, deflate, sdch',
# 'Accept-Language':'zh-CN,zh;q=0.8',
# 'Cache-Control':'max-age=0'
# }
#
# data = {"eventvalidation": "","viewstate": "","viewstategenerator": ""}
# url = 'http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sz'
# resp = requests.post(url, headers=headers,allow_redirects=True)
#
# if resp.status_code == 200:
#     soup = BeautifulSoup(resp.text,'lxml')
#     ev = soup.find(id="__EVENTVALIDATION")
#     data["eventvalidation"] = ev["value"]
#
#     vs = soup.find(id="__VIEWSTATE")
#     data["viewstate"] = vs["value"]
#     vg = soup.find(id="__VIEWSTATEGENERATOR")
#     data["viewstategenerator"] = vs["value"]
#     post_data = {
#     "today":"20180110",
#     "sortBy":"",
#     "alertMsg":"",
#     "ddlShareholdingDay":"03",
#     "ddlShareholdingMonth":"06",
#     "ddlShareholdingYear":"2017",
#     "btnSearch.x":"17",
#     "btnSearch.y":"9",
#     "__VIEWSTATE":data["viewstate"],
#     "__VIEWSTATEGENERATOR":data["viewstategenerator"],
#     "__EVENTVALIDATION":data["eventvalidation"]
#     }
#     resp = requests.post(url, headers=headers,data=post_data,allow_redirects=True)
#     print resp.text
#     if resp.status_code == 200:
#         login_soup = BeautifulSoup(resp.text,'lxml')
#         pnlResult=login_soup.find_all('div',attrs = {'id' : 'pnlResult'})[0]
#         print pnlResult.find_all('div')[0].text
# else:
#     print resp.status_code