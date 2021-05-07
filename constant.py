#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.8.16

#每次更新一张表，共5张表
stockDetailTableList = ['stock_5DayDetailData','stock_4DayDetailData','stock_3DayDetailData','stock_2DayDetailData','stock_1DayDetailData','stock1DayDetailData','stock2DayDetailData','stock3DayDetailData','stock4DayDetailData','stock5DayDetailData']
stocklistName = 'stocklist'


'''
修复Python找不到数据的问题
install_name_tool -change libmysqlclient.18.dylib  /usr/local/mysql/lib/libmysqlclient.18.dylib  /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/_mysql.so
'''


'''
CREATE TABLE `stock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` char(10) DEFAULT NULL,
  `name` char(20) DEFAULT NULL,
  `total` char(20) DEFAULT NULL,
  `percent` char(20) DEFAULT NULL,
  `date` char(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5933705 DEFAULT CHARSET=utf8 
'''