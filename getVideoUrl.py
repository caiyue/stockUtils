#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.4.16

import os
import sys
import urllib
import re
import os.path as fpath
import urllib2
from wgety.wgety import Wgety
import random
# import  cookielib

import sys
reload(sys)
sys.setdefaultencoding('utf8')
videoUrldomain = 'http://www.46ef.com/'
AllPages = []
urlPrefix = videoUrldomain + 'list/'
fileSuffix = '.mp4'

def getAllPages():
    AllPages.append(videoUrldomain + 'list/10.html')
    for i in range(2,360):
        AllPages.append(urlPrefix +'10_'+ str(i) +'.html')
    return AllPages

def getVideoNameListFromPage(pageUrl):
    # partern = re.compile("video=\['(.*?)\->video/mp4'\]")
    html = getHtmlFromUrl(pageUrl)
    partern = re.compile('<a href="(.*?)" target="_blank"><img src="/template/max/images/bofang.gif"')
    list = re.findall(partern, html)
    return list

def getFullVideoUrl(videoName):
    return videoUrldomain + videoName


def getHtmlFromUrl(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(url, headers=headers)
    # content = urllib2.urlopen(req).read().  # UTF-8
    content = urllib2.urlopen(req).read().decode('gbk', 'ignore').encode('utf-8')
    return content

def getVideoDownloadUrlAndNameFromUrl(url):
    html = getHtmlFromUrl(url)
    if len(html) <= 0:
        return
    # partern = re.compile('<div id="imagelist"><img src=(.*?)')
    partern = re.compile("video=\['(.*?)\->video/mp4'\]")
    list = re.findall(partern,html)
    vurl = name = None
    if list and len(list) > 0:
        vurl = list[0]
    partern = re.compile("<title>(.*?)</title>")
    list = re.findall(partern, html)
    if list and len(list) > 0:
        name = list[0]
    if vurl and name:
        return (name,vurl)

def getFileListWithSuffix(dirPath,suffix=fileSuffix):
    jsonFileList = []
    f_list = os.listdir(dirPath)
    for i in f_list:
        # os.path.splitext():分离文件名与扩展名
        if fpath.splitext(i)[1] == suffix:
            jsonFileList.append(i)
    #not path,just name
    return jsonFileList

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per

def printWithNoNewLine(percentNum):
    print '%.2f%%' % percentNum
    print "\b\b\b\b\b\b"

def downLoadFileWithUrl(vname,vurl):

    # print 'downloadFile:' + url
    # try:
    #     local = url.split('/')[-1]
    #     urllib.urlretrieve(url,name+fileSuffix,Schedule)
    # except Exception:
    #     print Exception.__name__,url

    w = Wgety()
    w.execute(url=vurl,filename=(vname+fileSuffix))


def mainMethod():
    pageList = getAllPages()
    for page in pageList:
        videoList = getVideoNameListFromPage(page)
        if not videoList or len(videoList) == 0:continue
        for name in videoList:
            videoPageurl = getFullVideoUrl(name)
            if not videoPageurl: continue
            videoName, videoUrl = getVideoDownloadUrlAndNameFromUrl(videoPageurl)
            fileList = getFileListWithSuffix('./')
            if not videoUrl:continue
            if (videoName+fileSuffix) in fileList or (videoUrl+fileSuffix) in fileList:continue
            else:
                print 'Downloading Page:%s,videoName:%s,indexOfPage:%d' % (page,name,videoList.index(name))
                downLoadFileWithUrl(videoName, videoUrl)

if __name__ == '__main__':
    mainMethod()
