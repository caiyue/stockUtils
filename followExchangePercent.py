
#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.8.16

import  os
import  sys
import  urllib2
import  re
import simplejson
import  time
import socket
from datetime import datetime
import os.path as fpath
from stockInfo import getHtmlFromUrl,getMarketId

exchangePercentUrl = 'http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?rtntype=5&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery18304829562165541863_1516114371398&id=%s&type=t5&iscr=false&_=1516114409450'


def getExchangedataForCode(code):
    url = exchangePercentUrl % (code + getMarketId(code))
    res = getHtmlFromUrl(url)
    