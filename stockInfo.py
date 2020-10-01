#!/usr/bin/python
#-*-coding:utf-8 -*-

# author:蔡董
#date:2017.8.16

import os
import sys
import urllib2
import re
import simplejson
import time
import socket
import datetime
import os.path as fpath
from bs4 import BeautifulSoup
import pickle,pprint
#from mysqlOperation import mysqlOp
from send_email import sendMail

reload(sys)
sys.setdefaultencoding('utf8')

#基金流通股占比
stockPercentOfFund = 'http://f10.eastmoney.com/ShareholderResearch/MainPositionsHodlerAjax?date=2020-03-31&code=%s'

#单季度在建工程
inprogressProject = 'http://f10.eastmoney.com/NewFinanceAnalysis/zcfzbAjax?companyType=4&reportDateType=0&reportType=1&endDate=&code=%s'

#报告期内现金流变动
cashChange = 'http://f10.eastmoney.com/NewFinanceAnalysis/xjllbAjax?companyType=4&reportDateType=0&reportType=1&endDate=&code=%s'

#股东数
GuDongcount = 'http://f10.eastmoney.com/ShareholderResearch/ShareholderResearchAjax?code=%s'

#人均持股金额
averageHolding = 'http://f10.eastmoney.com/ShareholderResearch/ShareholderResearchAjax?code=%s'


#十大流通股东
sdltgd = 'http://f10.eastmoney.com/ShareholderResearch/ShareholderResearchAjax?code=%s'

# QFII以及保险、社保数量
qfiicount = 'http://data.eastmoney.com/zlsj/detail.aspx?type=ajax&st=2&sr=-1&p=1&ps=100&jsObj=NMfupkBs&stat=0&code=%s'


#近半年的K线数据
halfYearHsl = 'http://push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery1124005434882013261677_1595068788894&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf61&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt=1&beg=0&end=20500000&_=1595068788972&secid='

#最近高管增持列表
adminStockChange = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=GG&sty=GGMX&p=1&ps=200&js=var%20BLUkGoqU={pages:(pc),data:[(x)]}&rt=52664684'

#个股高管增持情况
ggzcBaseUrl = 'http://f10.eastmoney.com/CompanyManagement/CompanyManagementAjax?code=%s'

#沪深A股价格相关数据
xxsjPrefixUrl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=FCOIATA&sortType=C&sortRule=-1&page='
xxsjSuffix = '&pageSize=100&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.681840105810047'

#换手率
hslUrl = 'http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&invt=2&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287&secid=%s&cb=jQuery1124007973482264905063_1579700999918&_=1579700999919'

#净资产收益率12%  3年利润增长率10% 100亿市值以上
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz20(1|100y)]&p=1&jn=pUnYlfVk&ps=100&s=cz20(1|100y)&st=-1&r=1507352123438'
#净资产收益率12%  3年利润增长率10%，利润同比增长率
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz_jgcg01][cznl05(4|0.1)][cz19(1|100y)]&p=1&jn=DvMQgnCP&ps=100&r=1507563206241'
#3年净利润增长率10以上，资产收益率大于10%（0.1,5）），市值超过200亿
mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_jgcg01][cz_ylnl01(4|0.20)][cz_ylnl04(1|0.3)][cz19(1|100y)]&p=%s&jn=fjnexJlG&ps=100&s=cz19(1|100y)&st=-1&r=1520242317534'


#半年内公司评级
companyCommentList = 'http://reportapi.eastmoney.com/report/list?cb=datatable7259366&pageNo=1&pageSize=100&code=%s&industryCode=*&industry=*&rating=*&ratingchange=*&beginTime=%s&endTime=%s&fields=&qType=0&_=1569424249615'

#ROE 投资回报率
ROEOfStockUrl = 'http://data.eastmoney.com/DataCenter_V3/stockdata/cwzy.ashx?code=%s'

#code = sh601318
ROEOfStockUrl2 = 'http://f10.eastmoney.com/NewFinanceAnalysis/MainTargetAjax?type=2&code=%s'

#年报
ROEOfStockInYears = 'http://f10.eastmoney.com/NewFinanceAnalysis/MainTargetAjax?type=1&code=%s'

#利润表
profitUrl =  'http://f10.eastmoney.com/NewFinanceAnalysis/lrbAjax?companyType=4&reportDateType=1&reportType=1&endDate=&code=%s'

#公司经营业务  sz000001
bussinessDetailUrl = 'http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/CoreConceptionAjax?code=%s'

#公司主营业务比例
companyBussinessPercentUrl = 'http://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/BusinessAnalysisAjax?code=%s'

companyNameUrl = 'http://suggest.eastmoney.com/SuggestData/Default.aspx?name=sData_1510989642587&input=%s&type=1,2,3'


#公司市值下限
companySzDownLimit = 50
companyHslDownLimit = 1.0
pageSize  = 100
roeSwitch = True


def getStockCodeFromHtmlString(string):
    if string and len(string):
        return string[16:22]

def getFloatFromString(s):
    if s == '--' or s == '-':
        return 0
    else:
        return float(s)

def getHtmlFromUrl(url, utf8coding=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        req = urllib2.Request(url, headers=headers)
        ret = urllib2.urlopen(req, timeout=7)
        if utf8coding:
            res = ret.read().decode('gbk', 'ignore').encode('utf-8')
        else:
            res = ret.read()
    except Exception:
            print 'exception  occur', url
            return None
    return res

def hasHTML(obj):
    return obj.startswith('<!DOCTYPE HTML PUBLIC')


def getJsonObj(obj):
    if not obj:
        return None
    if hasHTML(obj):
        return None
    #"var moJuuzHq="{"Results":["2,300672,国科微,是","2,300676,华大基因,是","1,603612,索通发展,是","1,603707,健友股份,是","2,002888,惠威科技,是","2,300678,中科信息,是","2,002889,东方嘉盛,是","1,603860,中公高科,是","2,300685,艾德生物,是","2,300687,赛意信息,是","1,603880,南卫股份,是","2,300689,澄天伟业,是","1,603602,纵横通信,是","2,300688,创业黑马,是","1,603721,中广天择,是","2,300691,联合光电,是","1,601326,秦港股份,是","1,603776,永安行,是","2,002892,科力尔,是","1,603129,春风动力,是","1,603557,起步股份,是"],"AllCount":"21","PageCount":"1","AtPage":"1","PageSize":"40","ErrMsg":"","UpdateTime":"2017/8/19 13:37:03","TimeOut":"3ms"}"
    # newobj = obj.split('=')[1]  #//必须要将前面的= 去掉
    # return  simplejson.loads(newobj)
    newobj = "{" + obj.split('={')[1]
    return simplejson.loads(newobj)


def getJsonObjOrigin(obj):
    if not obj:return None
    if hasHTML(obj):
        return None
    o = None

    try:
        o = simplejson.loads(obj)
        if isinstance(o, unicode):
            o = simplejson.loads(o)
    except Exception, e:
        print Exception.__name__,e
    return o

def getFundCompanyListJsonObjFrom(obj):
    par = re.compile('var stockCodes=\[.*?\];')
    list = re.findall(par, obj)
    if list and len(list) > 0:
        companyString = list[0]
        if companyString.startswith('var stockCodes='):
            #去除前面无效数据以及分号
            s = companyString[15:-1]
            return simplejson.loads(s)

    return None

def getJsonList(obj):
    '''解析列表,[ 开头'''
    if obj and obj.startswith('['):
        return simplejson.loads(obj)
    else:
        return None

def getJsonObj2(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':')[1]
        return simplejson.loads(sepString)
    else:
        return None


def getJsonObj2s(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("data\":{.*?}}")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s[6:]
        sepString = sepString[0: -1]
        return simplejson.loads(sepString)
    else:
        return None

def getJsonObj3(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("data:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None
def getJsonObj4(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("rank:.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None

def getJsonObj5(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("\"Value\":.*?\"]")
    list = re.findall(partern, obj)
    if list and len(list) > 0:
        s = list[0]
        sepString = s.split(':[')[1]
        return simplejson.loads('[' + sepString)
    else:
        return None

def getJsonObj6(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("\({.*?}\)")
    list = re.findall(partern, obj)
    try:
        if list and len(list) > 0:
            s = list[0]
            return simplejson.loads(s[1:-1])
        else:
            return None
    except Exception:
        print s
def getJsonObj7(obj):
    if not obj: return None
    if hasHTML(obj): return None
    partern = re.compile("{.*?}")
    list = re.findall(partern, obj)
    try:
        if list and len(list) > 0:
            s = list[0]
            return simplejson.loads(s)
        else:
            return None
    except Exception:
        print s

def getHoldChangeFromRes(obj):
    par = re.compile('data:\[.*?\]')
    list = re.findall(par,obj)
    if list and len(list) > 0:
        s = list[0]
        if s and len(s) > 5:
            try:
                return simplejson.loads(s[5:])
            except Exception:
                print obj

    return None

def getCompanyListFromJsonObj(obj):
    return None


# 深圳或者上海交易所
def getMark10Id(code):
    ret = getMarketCode(code, True)
    if 'sh' in ret:
        return 1
    else:
        return 0

def getMarketId(code):
    subCode = code[0:3]
    if subCode == '009' or subCode == '126' or subCode == '110':
        return '1'
    else:
        fCode = subCode[0:1]
        if fCode == '5' or fCode == '6' or fCode == '9':
            return '1'
        else:
            return '2'

def getMarketCode(code,prefix = False):
    ret = getMarketId(code)
    if prefix:
        if ret == '1':
            return 'sh' + code
        else:
            return 'sz' + code
    else:
        if ret == '1':
            return code + '.SH'
        else:
            return code + '.SZ'


class CompanyInfo(object):
    def __init__(self,code,name):
        super(CompanyInfo,self).__init__()
        self.code = code
        self.name = name


class CompanyValueInfo(CompanyInfo):
    def __init__(self,code,name,syl,sjl,sz,hsl):
        '''代码，名字，市盈率，市净率，市值、换手率'''
        super(CompanyValueInfo,self).__init__(code,name)
        self.syl = syl
        self.sjl = sjl
        self.sz = sz
        self.hsl = hsl


class   CompanyBussinessPercentDetailModel(CompanyInfo):
    '''主营业务收入、利润，收入占比、利润占比'''
    def __init__(self,code,name,time,bussinessName,income,profit,incomePercent,profitPercent):
        super(CompanyBussinessPercentDetailModel,self).__init__(code,name)
        self.time = time
        self.bussinessName = bussinessName
        self.income = income
        self.profit = profit
        self.incomePercent = incomePercent
        self.profitPercent = profitPercent


class MostValueableCompanyInfo(CompanyInfo):
    '''最可投资价值股票,净资产收益率>15%，3年净利润复合增长率>10%'''
    def __init__(self,code,name,jzcsyl,mlilv,orgCount,sz):
        super(MostValueableCompanyInfo,self).__init__(code,name)
        self.jzcsyl = jzcsyl
        self.maolilv = mlilv
        self.orgCount = orgCount
        self.sz = sz

    #如果要排序，就需要实现该方法
    def __lt__(self, other):
        return float(self.orgCount) > float(other.orgCount)

class RoeModel(object):
    '''日期，roe，利润增长率,收入增长率，总收入，总利润'''
    def __init__(self,date,roe,profitRate,incomeRate,income,profit,maolilv,jinglilv,zcfzl):
        super(RoeModel,self).__init__()
        self.dateOfRoe = date
        self.roe = roe
        self.profitRate = profitRate
        self.incomeRate = incomeRate
        self.income = income
        self.profit = profit
        self.maolilv = maolilv
        self.jinglilv = jinglilv
        self.zcfzl = zcfzl



class StockUtils(object):
    def __init__(self):
        super(StockUtils,self).__init__()

    def getCompanyBussinessDetailString(self,code):
        res = getHtmlFromUrl((bussinessDetailUrl % getMarketCode(code)))
        obj = getJsonObjOrigin(res)
        if obj:
            li = obj['hxtc']
            if li and len(li) > 2:
                return li[0]['ydnr'] + '\n' + li[1]['ydnr']
        return None

    def getCompanyBussinessPercentDetailForCode(self, code):
        bussinessList = []
        res = getHtmlFromUrl(companyBussinessPercentUrl % getMarketCode(code))
        obj = getJsonObjOrigin(res)
        if obj and  len(obj['zygcfx']) > 0 :
            o = obj['zygcfx'][0]
            if o:
                li = o['hy']
                if li and len(li) > 0:
                    for d in li:
                        m  = CompanyBussinessPercentDetailModel(code,None,d['rq'],d['zygc'],d['zysr'],d['zylr'],d['srbl'],d['lrbl'])
                        if m:bussinessList.append(m)

        return bussinessList




    @classmethod
    def getMostValueableStockList(self):
        '''价值投资股票列表'''
        page = 1
        cList = []
        while True:
            res = getHtmlFromUrl(mostValueableStockUrl % page)
            if res:page += 1
            companyListObj = getJsonObj(res)
            if companyListObj:
                list =  companyListObj['Results']
                if list and len(list):
                    for item in list:
                        stockInfo = item.split(',')
                        jzcsyl = str(float(stockInfo[4].split('(')[0]) * 100) + '%'
                        mlilv = str(float(stockInfo[5].split('(')[0]) * 100) + '%'
                        orgCount = stockInfo[3].split('(')[0]
                        sz = str(int(float(stockInfo[6])/10000/10000))
                        cinfo = MostValueableCompanyInfo(stockInfo[1],stockInfo[2],jzcsyl,mlilv,orgCount,sz)
                        cList.append(cinfo)
                    if len(list) < pageSize:break
                    #如果将要获取的页码比总共的页码大，那么直接退出
                    if int(companyListObj['PageCount']) < page:break
                else:break
            else:break
        return cList

    def getDevelopPercentOfCost(self, code):
        '''研发占比'''
        url = profitUrl % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url, False)
        obj = getJsonObjOrigin(res)

        if not obj:
            return 0, 0, 0
        else:
            if isinstance(obj, list) and len(obj) > 0:
                increaseHight = False
                # 最近三年的成长速度
                count = 0
                for item in obj:
                    # 最近两年成长
                    count += 1
                    # allExpense = item['TOTALOPERATEEXP']
                    # RDExpense = item['RDEXP']
                    # SaleExpense = item['SALEEXP']
                    # InvestIncome = item['INVESTINCOME']
                    incomeIncreaseByYear = item['OPERATEREVE_YOY']
                    profileIncreaseByYear = item['NETPROFIT_YOY']
                    try:
                        increaseHight = not (float(incomeIncreaseByYear) < 25 or
                                         float(profileIncreaseByYear) < 20 or
                                         incomeIncreaseByYear == '--' or
                                         profileIncreaseByYear == '--')

                        if not increaseHight or count == 2:
                            break
                    except Exception,e:
                        print 'parse exception: %s' % code

                # 最近一年的研发费用
                item=obj[0]
                allExpense = item['TOTALOPERATEEXP']
                RDExpense = item['RDEXP']
                if not RDExpense or len(RDExpense) == 0 or RDExpense == '--':
                    return 0, 0, increaseHight
                if not allExpense or len(allExpense) == 0 or allExpense == '--':
                    return 0, 0, increaseHight

                percent = float(RDExpense) * 1.0 / float(allExpense)
                if percent >= 0.2:
                    return 3, percent, increaseHight
                elif percent >= 0.08:
                    return 2, percent, increaseHight
                elif percent >= 0.05:
                    return 1, percent, increaseHight
                else:
                    return 0, percent, increaseHight

        return 0, 0, 0


    @classmethod
    def getCommentNumberIn3MonthsForCode(self, code):
        '''3个月内评级'''
        currentTimeStamp = datetime.datetime.now()

        # 100天内
        startTime = datetime.datetime.strftime(currentTimeStamp - datetime.timedelta(days=(90+10)), "%Y-%m-%d")
        endTime = datetime.datetime.strftime(currentTimeStamp, "%Y-%m-%d")

        url = companyCommentList % (code, startTime, endTime)
        res = getHtmlFromUrl(url, False)
        obj = getJsonObj6(res)
        ret = []
        if obj:
            data = obj['data']
            if data and len(data):
                for item in data:
                    if item['emRatingName'] == u'增持' or item['emRatingName'] == u'买入' or item['lastEmRatingName'] == u'增持' or item['lastEmRatingName'] == u'买入':
                        ret.append(item)

        return len(ret)


    @classmethod
    def getRoeModelListOfStockForCode(self,code):
        '''价值投资股票信息'''
        url = ROEOfStockUrl2 % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url, False)
        #ROEList = getJsonList(res)
        obj = getJsonObjOrigin(res)
        if not obj: return None

        ROEList = obj
        if isinstance(ROEList, list) and len(ROEList) > 0:
            cList = []
            for item in ROEList:
                m = RoeModel(item['date'], item['tbjzcsyl'], item['gsjlrtbzz'], item['yyzsrtbzz'], item['yyzsr'], item['kfjlr'], item['mll'], item['jll'], item['zcfzl'])
                cList.append(m)
            return cList
        else:
            return None


    def getRoeModelListOfStockInYearsForCode(self,code):
        '''价值投资股票信息'''
        url = ROEOfStockInYears % (getMarketCode(code,prefix=True))
        res = getHtmlFromUrl(url,False)
        #ROEList = getJsonList(res)
        obj = getJsonObjOrigin(res)
        if not obj:return None
        ROEList = obj
        if isinstance(ROEList,list) and len(ROEList) > 0:
            cList = []
            for item in ROEList:
                m = RoeModel(item['date'], item['jqjzcsyl'], item['gsjlrtbzz'], item['yyzsrtbzz'], item['yyzsr'], item['kfjlr'], item['mll'], item['jll'], item['zcfzl'])
                cList.append(m)
            return cList
        else:
            return  None

    @classmethod
    def roeStringForCode(self, code, returnData=False):
        li = self.getRoeModelListOfStockForCode(code)
        s = ''
        if returnData:
            return li
        if li and len(li) > 0:
            for item in li:
                    s += (u'季报:' + str(item.dateOfRoe)).ljust(15,' ') + (u'净资产收益率:' + str(item.roe) + '%').ljust(15,' ') + (u'收入同比增长率:' + str(item.incomeRate) + '%').ljust(17,' ') + (u'净利润同比增长率:' + str(item.profitRate) + '%').ljust(18,' ') + (u'总收入:' + str(item.income)).ljust(12,' ')  + (u' 总利润:' + str(item.profit)).ljust(12,' ') + (u'毛利率:' + str(item.maolilv) + '%').ljust(13,' ') + (u'净利率:' + str(item.jinglilv) + '%').ljust(13,' ') +(u'资产负债率:' + str(item.zcfzl) + '%').ljust(13,' ')
                    s += '\n'
            return s
        else:
            return None


    def roeStringInYearsForCode(self, code):
        li = self.getRoeModelListOfStockInYearsForCode(code)
        s = ''
        if li and len(li) > 0:
            for item in li:
                s += (u'年报:' + str(item.dateOfRoe)).ljust(15, ' ') + (u'净资产收益率:' + str(item.roe) + '%').ljust(15,' ') + (u'收入同比增长率:' + str(item.incomeRate) + '%').ljust(17,' ') + (u'净利润同比增长率:' + str(item.profitRate) + '%').ljust(18,' ') + (u'总收入:' + str(item.income)).ljust(12,' ')  + (u' 总利润:' + str(item.profit)).ljust(12,' ') + (u'毛利率:' + str(item.maolilv) + '%').ljust(13,' ') + (u'净利率:' + str(item.jinglilv) + '%').ljust(13,' ') + (u'资产负债率:' + str(item.zcfzl) + '%').ljust(13,' ')
                s += '\n'

        return s

    '''最近3个季度平均超过5500w的在建工程'''
    def inprogressProject(self, code):
        url = inprogressProject % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url)
        if res:
            obj = getJsonObjOrigin(res)
            if obj and isinstance(obj, list) and len(obj) > 0:
                maxValue = 0
                total = 0
                #最近三个季度平均5500w的在建项目
                arr = obj[0: 3] if len(obj) >= 3 else obj
                for item in arr:
                    num = item['CONSTRUCTIONPROGRESS']
                    if num and len(num) > 0 and num != '-':
                        n = float(num)
                        total += n
                        if n > maxValue:
                            maxValue = float(num)
                    else:
                        total += 0
            return maxValue >= 55000000 or total/len(arr) >= 55000000
        return False


    '''现金流增长3000w以上'''
    def cashIncrease(self, code):
        url = cashChange % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url)
        if res:
            obj = getJsonObjOrigin(res)
            if obj and isinstance(obj, list) and len(obj) > 0:
                o = obj[0]
                if o:
                    num = o['NICASHEQUI']
                    if num and len(num) > 0 and num != '-':
                        return float(num) >= 30000000

    def getGuDongCount(self, code):
        url = GuDongcount % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url)
        count = getJsonObjOrigin(res)
        countLi = count['gdrs']
        ret = [x1['gdrs'] for x1 in countLi]
        ret = map(lambda x: round(float(x[0:-1]), 2) * 10000 if '万' in x else float(x), ret)
        if ret:
            ok = False
            if (len(ret) > 1 and ret[0] < ret[1] and ret[0] <= 15000) or ret[0] <= 10000:
                ok = True
            if len(ret) > 4:
                return ret[0:4], ok
            else:
                return ret, ok
        else:
            return [], False

    def getAverageHolding(self, code):
        url = averageHolding % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url)
        obj = getJsonObjOrigin(res)
        if obj and isinstance(obj, object):
            holdings = obj['gdrs']
            if holdings and len(holdings) > 0:
                try:
                    holdingsCount = map(lambda x: x['gdrs'], holdings)
                    jes = map(lambda x: x['rjcgje'], holdings)
                    counts = map(lambda x: x['rjltg'], holdings)

                    holdingsCountRet = map(lambda x: 0 if x == '--' else (float(x[0: -1]) * 10000 if '万' in x else float(x[0:-1]) * 10000 * 10000 if '亿' in x else float(x)), holdingsCount)
                    jeRet = map(lambda x: 0 if x == '--' else (float(x[0: -1]) if '万' in x else float(x) / 10000), jes)
                    countRet = map(lambda x: 0 if x == '--' else (float(x[0: -1]) * 10000 if '万' in x else float(x[0:-1]) * 10000 * 10000 if '亿' in x else float(x)), counts)

                    if jeRet and len(jeRet) > 0:
                        if len(jeRet) == 1:
                            return jeRet[0], [jeRet[0], jeRet[0], jeRet[0]], [countRet[0], countRet[0], countRet[0]], [holdingsCountRet[0], holdingsCountRet[0], holdingsCountRet[0]]
                        elif len(jeRet) == 2:
                            return jeRet[0], [jeRet[0], jeRet[1], jeRet[1]], [countRet[0], countRet[1], countRet[1]], [holdingsCountRet[0], holdingsCountRet[1], holdingsCountRet[1]]
                        else:
                            return jeRet[0], [jeRet[0], jeRet[1], jeRet[2]], [countRet[0], countRet[1], countRet[2]], [holdingsCountRet[0], holdingsCountRet[1], holdingsCountRet[2]]

                except Exception, e:
                    print 'process exception: code = ', code, e

        return 0, [], [], []

    def stockPercentOfFund(self, code):
        url = stockPercentOfFund % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url)
        obj = getJsonObjOrigin(res)
        if obj and len(obj) > 0:
            o = obj[0]
            percent = o['zltgbl'];
            if percent and percent != '--'  and percent != '%':
                return float(percent[0: -1])
        return 0


    def find_all(self, s2, s):
        index_list = []
        index = s.find(s2)
        while index != -1:
            index_list.append(index)
            index = s.find(s2, index + 1)

        if len(index_list) > 0:
            return index_list
        else:
            return []

    def getQFIICount(self, code):
        count = 0
        url = qfiicount % code
        res = str(getHtmlFromUrl(url))
        # qfii
        a1 = self.find_all('TypeCode":"2', res)
        # 社保
        a2 = self.find_all('TypeCode":"3', res)
        # 券商
        a3 = self.find_all('TypeCode":"4', res)
        # 保险
        a4 = self.find_all('TypeCode":"5', res)
        # 信托
        a5 = self.find_all('TypeCode":"6', res)

        count = len(a1) + len(a2) + len(a3) + len(a4) + len(a5)
        return count, len(a2), len(a1), len(a4), len(a3), len(a5)

    @classmethod
    def getAdminHoldingChange(self):
        '''股东增持'''
        res = getHtmlFromUrl(adminStockChange, False)
        companyList = getJsonObj2(res)
        if companyList and len(companyList):
            return companyList
        return None

    def getGDZJC(self):
        res = getHtmlFromUrl()

    def getAdminStockChange(self):
        ret = []
        for page in [1, 2, 3]:
            res = getHtmlFromUrl(adminStockChange % page)
            objs = getJsonObj2(res)
            if obj:
                for o in objs:

                    ret.append()


    @classmethod
    def getGGZCStock(cls, code):
        url = ggzcBaseUrl % (getMarketCode(code, prefix=True))
        res = getHtmlFromUrl(url, False)
        obj = getJsonObjOrigin(res)
        total = -1
        if not obj: return True
        li = obj['RptShareHeldChangeList']
        if not li or len(li) == 0:
            return True
        for s in li:
            year = s['rq']
            count = s['bdsl']

            if '2019' or '2020' in year:
                num = float(count)
                total += num
            else:
                break
        return total >= -1

    @classmethod
    def getDetailStockInfo(self, page):
        '''资金流入排行'''
        res = getHtmlFromUrl(xxsjPrefixUrl + str(page) + xxsjSuffix)
        companyListObj = getJsonObj4(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None

    def getStockNameFromCode(self, code):
        res = getHtmlFromUrl(companyNameUrl % code, utf8coding=True)
        pa = re.compile('=.*?;')
        if not isinstance(res, str):
            return None
        li = re.findall(pa, res)
        if li and len(li):
            s = li[0]
            ret = (s[1:-1]).split(',')
            if ret and len(ret):
                return ret[4]
        else:
            return None

    def prepareToIncreaseLastWeek(self, code):
        res = getHtmlFromUrl(halfYearHsl + str(getMark10Id(code)) + '.' + code, utf8coding=True)
        pa = re.compile('\[.*?\]')
        if not res or type(res) is not str: return None
        try:
            li = re.findall(pa, res)
            if li and len(li):
                s = getJsonObjOrigin(li[0])
                if s and len(s) > 0:
                    s = s[len(s) - 7:] if len(s) > 7 else s
                    # 嵌入的函数
                    def compute(x):
                        dataArray = x.split(",")
                        startPrice = float(dataArray[1])
                        endPrice = float(dataArray[2])
                        return True if endPrice >= startPrice else False
                    increaseArray = map(lambda x: compute(x), s)
                    for i in range(len(increaseArray)):
                        # 连续3天都在上涨则提示
                        if i + 2 < len(increaseArray) and increaseArray[i] and increaseArray[i+1] and increaseArray[i+2]:
                            return True
                    return False
            else:
                return False
        except Exception, e:
            print e, code


    def sdltgdTotalPercent(self, code):
        percent = 0
        res = getHtmlFromUrl(sdltgd % getMarketCode(code))
        obj = getJsonObjOrigin(res)
        if not obj:
            return percent
        li = obj['gdrs']
        if li and len(li) > 0:
            for item in li:
                o = item['qsdltgdcghj']
                if '--' in o or '-' in o:
                    percent = 0
                else:
                    percent = float(o)
                    break
        return percent

    def getAllStockList(self):
        stockList = []
        startPage = 1
        while True:
            li = StockUtils().getDetailStockInfo(startPage)
            if li and len(li) > 0:
                for item in li:
                    array = item.split(',')
                    # code1  name2   zhangfu5, startPrice10，max11，min12
                    code = str(array[1])
                    stockList.append(code)
            # 接口容易出现重复这里最多请求50 * 100 条数据
            if li and len(li) < pageSize or startPage >= 50:
                break
            startPage += 1

        return list(set(stockList)) if stockList and len(stockList) > 0 else []

    @classmethod
    def getHslAndSylForCode(self,code):
        '''市盈率、市值相关数据'''
        url = hslUrl % (str(getMark10Id(code)) + '.' + code)
        res = getHtmlFromUrl(url)
        obj = getJsonObj2s(res)
        if not obj:
            return 0
        else:
            return obj['f162']


def bussinessPercentString(code):
    s = ''
    li = StockUtils().getCompanyBussinessPercentDetailForCode(code)
    if li and len(li) > 0:
        for model in li:
            s += model.bussinessName.ljust(13,' ') + (u'收入:' + model.income).ljust(13,' ') + (u'利润:' + model.profit).ljust(13,' ') + (u'收入占比:' + model.incomePercent).ljust(16,' ') + (u'利润占比:' + model.profitPercent).ljust(13,' ')
            s += '\n'
    if len(s) > 0:
        return s
    return None

def szyjlString(model):
    return u'市值:'+ model.sz +u'亿' + u'  市盈率:'+model.syl + u'  市净率:'+model.sjl + u'  换手率:'+model.hsl

def szyjlRankString(model):
    return '\n' + u'市值排行:'+ model.szRank + u'  利润排行:'+model.profitRank + u'  市盈率排行:'+model.sjlRank + u'  市净率排行:'+model.sjlRank + u'  资产收益率排行:' +model.roeRank

def mostValueableCompanyString(model):
    return ('净资产收益率年增长率:'+model.jzcsyl).ljust(15,' ')  + ('  持仓机构数:' + model.orgCount)

def  validateStock(code):
    model = szyjl(code)
    if not model: return
    jidu = StockUtils().roeStringForCode(code)
    niandu = StockUtils().roeStringInYearsForCode(code, model)

    print jidu
    print niandu


def mainMethod():
    util = StockUtils()
    ret = util.getAdminHoldingChange()
    for gd in ret:
        companyInfo = gd.split(',')
        if companyInfo[6] != '-' and float(companyInfo[6]) > 0:
            print companyInfo[2], companyInfo[9].ljust(7, ' '), companyInfo[5], ' 增持: ', companyInfo[6], '增持后: ', companyInfo[7], (
            companyInfo[-2]).ljust(10, ' ')


if __name__ == '__main__':
    mainMethod()


