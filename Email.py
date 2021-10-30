from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import Configuration
import smtplib
import Logger
import os
import traceback

Email_info = Configuration.get_Email_info()
log = None
def sentEmail(Log_Name='Email', Email_to='richardding@eftpay.com.hk', Email_subject='', Email_from='RSM System', Email_content='', Email_attachement=None):
    try:
        log = Logger.Log(Log_Name)
        log.start('Email')
        log.info(f'Email_to: {Email_to}')
        log.info(f'Email_subject: {Email_subject}')
        log.info(f'Email_from: {Email_from}')
        log.info(f'Email_content: {Email_content}')
        log.info(f'Email_attachement: {Email_attachement}')
        email = MIMEMultipart()  # 建立MIMEMultipart物件
        email['Subject'] = Email_subject
        email["from"] = Email_from  # 寄件者
        email["to"] = Email_to  # 收件者
        email.attach(MIMEText(Email_content))  # 郵件純文字內容
        if type(Email_attachement) == str and Email_attachement != None:
            filename = os.path.basename(Email_attachement)
            attachement = MIMEText(open(Email_attachement, 'rb').read(), 'base64', 'utf-8')
            attachement["Content-Type"] = 'application/octet-stream'
            attachement["Content-Disposition"] = f'attachment; filename="{filename}"'
            email.attach(attachement)
        elif type(Email_attachement) == list:
            for att in Email_attachement:
                filename = os.path.basename(att)
                attachement = MIMEText(open(att, 'rb').read(), 'base64', 'utf-8')
                attachement["Content-Type"] = 'application/octet-stream'
                attachement["Content-Disposition"] = f'attachment; filename="{filename}"'
                email.attach(attachement)
        with smtplib.SMTP(host=Email_info[0][1], port=Email_info[0][2]) as smtp:  # 設定SMTP伺服器
            for i in range(5):
                try:
                    smtp.ehlo()  # 驗證SMTP伺服器
                    smtp.starttls()  # 建立加密傳輸
                    smtp.login(Email_info[0][0], Email_info[0][4])  # 登入寄件者gmail
                    smtp.send_message(email)  # 寄送郵件
                    log.info('sent email success')
                    break
                except Exception as ex:
                    log.error("sent email Failed, Erroe message: {0}".format(ex))
    except Exception as ex:
        sign = '*' * 100 + '\n'
        errorMessage = f'{sign}>>>Exception Time：\t{datetime.now()}\n>>>Exception def：\t{sentEmail.__name__}\n>>>Exception msg：\t{ex}\n{traceback.format_exc()}{sign}'
        log.error(errorMessage)
        log.end('Email')