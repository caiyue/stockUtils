#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.8.16

'''
mysqlclient 1.3.0
MySQL-python是python和数据库的连接器，会通过mysqlclient来链接数据库
这2个是必须要的
'''

incomeBaseIncrease = 25
profitBaseIncrease = 25

sylLimit = 400
jeLimit = 15  # 有些新股好公司确定很低
jllLimit = 15
jllBottom = 11

jjccPercent = 20

shurl = 'http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTongHoldingRatioList?callback=sina_15618815495718682370855167358&page=%s&num=40&type=sh&start=%s&end=%s'
szurl = 'http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTongHoldingRatioList?callback=sina_15618815495718682370855167358&page=%s&num=40&type=sz&start=%s&end=%s'

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

'''
通常来说多线程相对于多进程有优势，因为创建一个进程开销比较大，然而因为在 python 中有 GIL 这把大锁的存在，
导致执行计算密集型任务时多线程实际只能是单线程。而且由于线程之间切换的开销导致多线程往往比实际的单线程还要慢，
所以在 python 中计算密集型任务通常使用多进程，因为各个进程有各自独立的 GIL，互不干扰。

而在 IO 密集型任务中，CPU 时常处于等待状态，操作系统需要频繁与外界环境进行交互，如读写文件，
在网络间通信等。在这期间 GIL 会被释放，因而就可以使用真正的多线程。
'''