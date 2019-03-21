#!/usr/bin/env python
 
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import re

class SendMail(object):

    def __init__(self):
        self.mail_host = "smtp.qq.com"
        self.mail_user = "1262088901@qq.com"
        self.mail_pass = "tolqgnsngfcljeea"  # 口令
        self.sender = '1262088901@qq.com'
        self.subject = 'Ezblock Message'  
        receivers = []
    def recv(self, text):
        return re.split(',\s*', text)
    
    # def adressee(self, adr):
    #     r =  re.split('@', adr)
    #     return r[0]

    def send(self, receivers, msg):
        receivers = self.recv(receivers)
        if len(receivers) == 0:
            raise print("Lack of addressee")
        message = MIMEText(msg, 'plain', 'utf-8')
        message['From']=formataddr(["SunFounder",self.sender])  # sender name
        try:
        #     for i in range(0, len(receivers)):
            message['To']=formataddr([receivers[0],receivers[0]]) 
            message['Subject']= self.subject   # headline
        
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mail_host, 25)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, receivers, message.as_string())
            print("Email sent successfully")
        except smtplib.SMTPException:
            print("Error: Email sending failed")


def test():
    sendmail = SendMail().send('845864704@qq.com', "Devin send email")

if __name__ == "__main__":
    test()
