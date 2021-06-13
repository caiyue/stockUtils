#!/usr/bin/python
# -*- coding: utf-8 -*-

import  os
import  sys
import  urllib
import  re
import os.path as fpath
import urllib2
import requests
from tqdm import tqdm

video_domain = 'https://cdn3.lajiao-bo.com'
page_domain = 'https://wm.u37tv.com'


def getHtmlFromUrl(url, utf8coding=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        req = urllib2.Request(url, headers=headers)
        ret = urllib2.urlopen(req, timeout=100)
        if utf8coding:
            res = ret.read().decode('gbk', 'ignore').encode('utf-8')
        else:
            res = ret.read()
    except Exception, e:
            print 'exception  occur:%s, %s' % (e, url)
            return None
    return res


def formateM38uUrl(url):
    # 添加高清数码参数
    return url[:-10] + '500kb/hls/index.m3u8'


def getM3u8Content(url):
    res = getHtmlFromUrl(url)
    # title
    titlep = re.compile('<title>.*?</title>')
    titleList = re.findall(titlep, res)
    title = titleList[0][6: -8]

    # find m3u8
    partern = re.compile(".*?index.m3u8")
    list = re.findall(partern, res)
    if list and len(list) > 0:
        m3u8Url = list[0]
        # get m3u8 content
        formateUrl = formateM38uUrl(m3u8Url)
        print 'get m3u8 url:%s' % formateUrl
        m3u8Content = getHtmlFromUrl(formateUrl)

        # path
        filePath = '%s.ts' % title
        if os.path.exists(filePath):
            os.remove(filePath)
        with open('%s.ts' % title, "wb+") as file:
            for line in tqdm(m3u8Content.split('\n')):
                if not line.startswith('#'):
                    response = requests.get(video_domain + line, stream=True, verify=True)
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

def mainMethod():
    listUrl = 'https://wm.u37tv.com/link/zhip/page/%s'
    for i in range(2, 100):
        realUrl = listUrl % i
        listRes = getHtmlFromUrl(realUrl)
        hrefRe = re.compile("class=\"thumb\" href=\".*?\"")
        li = re.findall(hrefRe, listRes)
        if li and len(li) > 0:
            for path in li:
                p = path[20:-1]
                pageUrl = page_domain + p
                print 'start download page:%s' % pageUrl
                getM3u8Content(pageUrl)


if __name__ == '__main__':
    mainMethod()

