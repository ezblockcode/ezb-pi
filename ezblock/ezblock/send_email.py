#!/usr/bin/env python
 
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class SendMail(object):
    
    # mail_host = "smtp.xxx.com"
    # sender = "123@qq.com"
    # mail_pass = "xxxx" 
    # subject = 'Ezblock Message'
    def __init__(self, mail_host, sender, mail_pass, subject): 
        self.mail_host = mail_host      # 邮箱的服务器名字
        self.sender = sender            # 发送者邮箱
        self.mail_pass = mail_pass      # 发送者邮箱的生成授码权（口令）（打开SMTP服务）

    def send(self, receivers, msg, subject):
        print("sender:", self.sender)
        message = MIMEText(msg, 'plain', 'utf-8')
        message['From']=formataddr([self.sender, self.sender])  # sender name
        try:
            message['To']=formataddr([receivers,receivers]) 
            message['Subject']= subject   # Email subject
        
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 25)
            smtpObj.login(self.sender, self.mail_pass)
            smtpObj.sendmail(self.sender, receivers, message.as_string())
            print("Email sent successfully")
        except smtplib.SMTPException:
            print("Error: Email sending failed")


def test():
    send11 = SendMail("smtp.qq.com", "xxx@qq.com", "nfsjbvkolswkhddg", "Ezblock Message")
    send11.send('xxx2.com', "who send email?")

if __name__ == "__main__":
    test()
