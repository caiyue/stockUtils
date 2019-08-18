#!/usr/bin/python
#coding=utf-8

# author:蔡董
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
from bs4 import BeautifulSoup
import pickle,pprint
#from mysqlOperation import mysqlOp
from send_email import sendMail

reload(sys)
sys.setdefaultencoding('utf8')


#5日新高
fiveDaysMaxPriceUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[hqzb05(1|5)]&p=1&jn=JODmOFXH&ps=100&s=hqzb05(1|5)&st=-1&r=1507347434465'


#60日新高
SixtyDaysMaxPrice = 'http://data.10jqka.com.cn/rank/cxg/board/4/field/stockcode/order/asc/ajax/1/'


#东方财富网-股东增持
gdzcBaseUrl = 'http://data.eastmoney.com/DataCenter_V3/gdzjc.ashx?pagesize=100&page=1&js=var%20ukjJZiRW&param=&sortRule=-1&sortType=BDJZ&tabid=jzc&code=&name=&rt=50102353'


#沪深A股价格相关数据
xxsjPrefixUrl = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=FCOIATA&sortType=C&sortRule=-1&page='
xxsjSuffix = '&pageSize=100&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.681840105810047'

#沪深A股市盈率、市净率、市值相关数据
sylDetailPrefixUrl = 'http://nuff.eastmoney.com/EM_Finance2015TradeInterface/JS.ashx?id='
sylDetailSuffixUrl = '&token=4f1862fc3b5e77c150a2b985b12db0fd&cb=jQuery183041202991002070233_1505234287664&_=1505234288231'


#净资产收益率12%  3年利润增长率10% 100亿市值以上
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz20(1|100y)]&p=1&jn=pUnYlfVk&ps=100&s=cz20(1|100y)&st=-1&r=1507352123438'
#净资产收益率12%  3年利润增长率10%，利润同比增长率
#mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_ylnl01(1|0.12)][cz_cznl06(1|0.1)][cz_jgcg01][cznl05(4|0.1)][cz19(1|100y)]&p=1&jn=DvMQgnCP&ps=100&r=1507563206241'
#3年净利润增长率10以上，资产收益率大于10%（0.1,5）），市值超过200亿
mostValueableStockUrl = 'http://xuanguapi.eastmoney.com/Stock/JS.aspx?type=xgq&sty=xgq&token=eastmoney&c=[cz_jgcg01][cz_ylnl01(4|0.20)][cz_ylnl04(1|0.3)][cz19(1|100y)]&p=%s&jn=fjnexJlG&ps=100&s=cz19(1|100y)&st=-1&r=1520242317534'


#ROE 投资回报率
ROEOfStockUrl = 'http://data.eastmoney.com/DataCenter_V3/stockdata/cwzy.ashx?code=%s'

#code = sh601318
ROEOfStockUrl2 = 'http://f10.eastmoney.com/NewFinanceAnalysis/MainTargetAjax?type=2&code=%s'

#年报
ROEOfStockInYears = 'http://f10.eastmoney.com/NewFinanceAnalysis/MainTargetAjax?type=1&code=%s'


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
    except  Exception:
            print 'exception  occur',url
            return None
    return res

def hasHTML(obj):
    return obj.startswith('<!DOCTYPE HTML PUBLIC')


def getJsonObj(obj):
    if not obj:return None
    if hasHTML(obj):return None
    #"var moJuuzHq="{"Results":["2,300672,国科微,是","2,300676,华大基因,是","1,603612,索通发展,是","1,603707,健友股份,是","2,002888,惠威科技,是","2,300678,中科信息,是","2,002889,东方嘉盛,是","1,603860,中公高科,是","2,300685,艾德生物,是","2,300687,赛意信息,是","1,603880,南卫股份,是","2,300689,澄天伟业,是","1,603602,纵横通信,是","2,300688,创业黑马,是","1,603721,中广天择,是","2,300691,联合光电,是","1,601326,秦港股份,是","1,603776,永安行,是","2,002892,科力尔,是","1,603129,春风动力,是","1,603557,起步股份,是"],"AllCount":"21","PageCount":"1","AtPage":"1","PageSize":"40","ErrMsg":"","UpdateTime":"2017/8/19 13:37:03","TimeOut":"3ms"}"
    # newobj = obj.split('=')[1]  #//必须要将前面的= 去掉
    # return  simplejson.loads(newobj)
    newobj = "{" + obj.split('={')[1]
    return simplejson.loads(newobj)


def getJsonObjOrigin(obj):
    if not obj:return None
    if hasHTML(obj): return None
    o = None

    try:
        o = simplejson.loads(obj)
    except Exception:
        print  Exception.__name__,Exception
    return o

def getFundCompanyListJsonObjFrom(obj):
    par = re.compile('var stockCodes=\[.*?\];')
    list = re.findall(par,obj)
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
    partern = re.compile("\(.*?\)")
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

def getCompanyListFromJsonObj(obj):
    return  None


def getMarketId(code):
    subCode = code[0:3]
    if subCode == '009' or subCode == '126' or subCode == '110':
        return '1'
    else:
        fCode = subCode[0:1]
        if fCode =='5' or fCode == '6' or fCode == '9':
            return '1'
        else:
            return '2'

def getMarketCode(code,prefix = False):
    ret = getMarketId(code)
    if prefix:
        if ret == '1':
            return  'sh' + code
        else:
            return  'sz' + code
    else:
        if ret == '1':
            return  code + '.SH'
        else:
            return  code + '.SZ'


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


    @classmethod
    def getFiveDaysMaxStockList(self):
        '''最近5天创新高'''
        res = getHtmlFromUrl(fiveDaysMaxPriceUrl)
        companyListObj = getJsonObj(res)
        if companyListObj:
            list =  companyListObj['Results']
            cList = []
            if list and len(list):
                for item in list:
                    stockInfo = item.split(',')
                    cinfo = CompanyInfo(stockInfo[1],stockInfo[2])
                    cList.append(cinfo)
                return cList
        return  None



    def get60DaysMaxStockList(self):
        '''最近5天创新高'''
        res = getHtmlFromUrl(SixtyDaysMaxPrice,True)
        if not res:
            return None
        part = re.compile('target="_blank">.*?</a></td>')
        li = re.findall(part,res)
        tu = [getStockCodeFromHtmlString(c) for c in li]
        return  list(tu)

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


    @classmethod
    def getStockholderHoldsStocks(self):
        '''股东增持'''
        res = getHtmlFromUrl(gdzcBaseUrl,True)
        companyList = getJsonObj2(res)
        if companyList and len(companyList):
            cList = []
            for item in companyList:
                '''item 是字符串，应该分割处理'''

                cList.append(item)
            return cList
        return None



    @classmethod
    def getDetailStockInfo(self,page):
        '''资金流入排行'''
        res = getHtmlFromUrl(xxsjPrefixUrl + str(page) + xxsjSuffix)
        companyListObj = getJsonObj4(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None

    def getStockNameFromCode(self,code):
        res = getHtmlFromUrl(companyNameUrl % code,utf8coding=True)
        pa = re.compile('=.*?;')
        li = re.findall(pa,res)
        if li and len(li):
            s = li[0]
            ret = (s[1:-1]).split(',')
            if ret and len(ret):
                return ret[4]
        else:
            return None

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
            if len(li) < pageSize:
                break
            startPage += 1
        return stockList

    def getGoodFundList(self):
        fl = []
        res = getHtmlFromUrl(goodFundUrl)
        fundList = getJsonObj7(res)
        if fundList:
            for item in fundList['datas']:
                fundArray = item.split(',')
                m = FundDetailModel(fundArray[0],fundArray[1],fundArray[3], fundArray[5],fundArray[6],fundArray[7],fundArray[8],fundArray[4],fundArray[11])
                fl.append(m)
        return fl


    def getStockListFromFund(self,fundCode):
        fl = []
        res = getHtmlFromUrl(fundHoldCompanyList % fundCode)
        compnanyList = getCompanyListFromJsonObj(res)
        return compnanyList

    def getFundHoldCompanyList(self,fundCode):
        res = getHtmlFromUrl(fundHoldCompanyList % fundCode)
        return getFundCompanyListJsonObjFrom(res)

    @classmethod
    def getInflowRankForPage(self,page):
        '''资金流入排行'''

        url = zjlrPrefix + str(page) + zjlrSuffix
        res = getHtmlFromUrl(url)
        companyListObj = getJsonObj3(res)
        if companyListObj and len(companyListObj):
            cList = []
            for item in companyListObj:
                cList.append(item)
            return cList
        return None
    @classmethod
    def getSylDetailDataForCode(self,code):
        '''市盈率、市值相关数据'''
        url = sylDetailPrefixUrl + code + getMarketId(code)+sylDetailSuffixUrl
        res = getHtmlFromUrl(url)
        valueList =  getJsonObj5(res)
        if valueList and len(valueList) > 0:
           return CompanyValueInfo(valueList[1],valueList[2],valueList[-15],valueList[-10],str(long(valueList[-7])/10000/10000), valueList[-16]+'%')
        return None



    def jiduAndNianduAndszyl(self,detailCode):
        detailModel = self.getSylDetailDataForCode(detailCode)
        model = szyjl(detailCode)
        if not model: return None
        print detailCode, detailModel.name, u'市值:' + detailModel.sz + u'亿', u'市盈率:' + detailModel.syl, u'换手率' + detailModel.hsl + '%'
        jidu = self.roeStringForCode(detailCode)
        niandu = self.roeStringInYearsForCode(detailCode)
        if jidu and niandu:
            bussString = bussinessPercentString(detailCode)
            if bussString:
                print bussString
                print jidu
                print niandu



def bussinessPercentString(code):
    s = ''
    li  = StockUtils().getCompanyBussinessPercentDetailForCode(code)
    if li and len(li) > 0:
        for model in li:
            s += model.bussinessName.ljust(13,' ') + (u'收入:' + model.income).ljust(13,' ') + (u'利润:' + model.profit).ljust(13,' ') + (u'收入占比:' + model.incomePercent).ljust(16,' ') + (u'利润占比:' + model.profitPercent).ljust(13,' ')
            s += '\n'
    if len(s) > 0:
        return s
    return None

def szyjl(code):
    return  StockUtils().getSylDetailDataForCode(code)

def szyjlString(model):
    return u'市值:'+ model.sz +u'亿' + u'  市盈率:'+model.syl + u'  市净率:'+model.sjl + u'  换手率:'+model.hsl

def szyjlRankString(model):
    return '\n' + u'市值排行:'+ model.szRank + u'  利润排行:'+model.profitRank + u'  市盈率排行:'+model.sjlRank + u'  市净率排行:'+model.sjlRank + u'  资产收益率排行:' +model.roeRank

def mostValueableCompanyString(model):
    return ('净资产收益率年增长率:'+model.jzcsyl).ljust(15,' ')  + ('  持仓机构数:' + model.orgCount)

def  validateStock(code):
    model = szyjl(code)
    if not model: return
    jidu =  StockUtils().roeStringForCode(code)
    niandu =  StockUtils().roeStringInYearsForCode(code, model)

    print jidu
    print niandu


def mainMethod():
    util = StockUtils()


    # #股东增持
    print '\n====================================股东增持====================================='
    gd = util.getStockholderHoldsStocks()
    if gd and len(gd):
         for item in gd:
             companyInfo = item.split(',')
             print companyInfo[0], companyInfo[1].ljust(7, ' '), companyInfo[-4], u'至', companyInfo[-3], (
             companyInfo[4]).ljust(30, ' '), companyInfo[5], (companyInfo[6] + u'万').ljust(13, ' '), (
                     u'占流通股的' + (companyInfo[7] + '%')).ljust(15, ' '), (
                     u'市值: ' + util.getSylDetailDataForCode(companyInfo[0]).sz + u'亿').ljust(15, ' ')


    # #价值投资选股
    print '\n===============================价值投资股票========================================'
    th = util.getAllStockList()
    if th and len(th) > 0:
        print '===============================共 %s 个========================================\n' % str(len(th))
        for item in th:
            model = szyjl(item)
            if not model: continue
            #不需要过滤换手率以及市值，价值投资
            print (u'第%s个: %s  %s' % (str(th.index(item) + 1), model.name, model.code))
            jidu = util.roeStringForCode(item)
            niandu = util.roeStringInYearsForCode(item)

            print jidu
            print niandu


if __name__ == '__main__':
    mainMethod()


