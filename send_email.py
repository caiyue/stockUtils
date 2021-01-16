#!/usr/bin/env python
# -*- coding:utf-8 -*-

import smtplib
from email.mime.text import MIMEText
#设置服务器所需信息
#163邮箱服务器地址
mail_host = 'smtp.163.com'

#163用户名
mail_user = '13146623011'
#密码(部分邮箱为授权码)
mail_pass = '25698469'
#邮件发送方邮箱地址
sender = '13146623011@163.com'
#邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
receivers = ['1072079578@qq.com', 'wpfun@foxmail.com']

#登录并发送邮件
def sendMail(subject, content):
    try:
        # 设置email信息
        # 邮件内容设置
        message = MIMEText(content, 'plain', 'utf-8')
        # 邮件主题
        message['Subject'] = subject
        # 发送方信息
        message['From'] = sender
        # 接受方信息
        message['To'] = receivers[0]

        smtpObj = smtplib.SMTP()
        #连接到服务器
        smtpObj.connect(mail_host, 25)
        #登录到服务器
        smtpObj.login(mail_user, mail_pass)
        #发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        #退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e) #打印错误


if __name__ == '__main__':
    sendMail('内容', 'bbbbb')