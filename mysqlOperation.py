#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.8.16

import MySQLdb
from constant import stockDetailTableList

conn = MySQLdb.connect(host='localhost',
                       port=3306,
                       user='root',
                       passwd='123456',
                       db ='stockDB',
                       )

class mysqlOp(object):
    pass
    def __init__(self):
        super(mysqlOp,self).__init__()
        self.conn = conn
        self.cur = conn.cursor()

    def executeSQL(self,sql):
        '''初始化数据'''
        if sql and len(sql) > 0:
            #return self.cur.execute(sql)
            return None
        else:
            return  None
    def getNewestDate(self):
        '''获取最新股票信息日期'''
        self.cur.execute('select  distinct sdate from  stock5DayDetailData')
        string =  self.cur.fetchall()[0][0]
        return string.split(' ')[0]

    def moveDataIntables(self,tablelist):
        '''必须要至少2个元素，现在是写死的10个'''
        if len(tablelist) < 2:return
        for table in tablelist:
            if table == tablelist[0]:
                self.clearTableData(table)
            else:
                index = tablelist.index(table) - 1
                src = table
                dst = tablelist[index]
                self.clearTableData(dst)
                sql = 'insert into %s(code,sname,startPrice,minPrice,maxPrice,endPrice,inflowCount,sdate,priceIncrementPercent) select code,sname,startPrice,minPrice,maxPrice,endPrice,inflowCount,sdate,priceIncrementPercent from %s' % (dst,src)
                self.executeSQL(sql)
    def clearTableData(self,tableName):
        self.executeSQL('delete from %s' % tableName)
