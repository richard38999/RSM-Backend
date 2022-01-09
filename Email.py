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
def sentEmail(
        Log_Name='Email',
        Email_to='richardding@eftpay.com.hk',
        Email_subject='',
        Email_from='RSM System',
        Email_content='',
        Email_attachement=None,
        isHTML=False
        ):
    try:
        log = Logger.Log(Log_Name)
        log.start('Email')
        log.info(f'Email_to: {Email_to}')
        log.info(f'Email_subject: {Email_subject}')
        log.info(f'Email_from: {Email_from}')
        log.info(f'Email_content: {Email_content}')
        log.info(f'Email_attachement: {Email_attachement}')
        log.info(f'isHTML: {isHTML}')
        email = MIMEMultipart()  # 建立MIMEMultipart物件
        email['Subject'] = Email_subject
        email["from"] = Email_from  # 寄件者

        if type(Email_to) == str and len(Email_to) > 0:
            email["to"] = Email_to  # 收件者
        elif type(Email_to) == list and len(Email_to) != 0:
            email["to"] = ';'.join(Email_to)   # 收件者
        if isHTML:
            email.attach(MIMEText(_text=Email_content, _subtype='html', _charset='utf-8'))  # 郵件HTML內容
        else:
            email.attach(MIMEText(_text=Email_content, _subtype='plain', _charset='utf-8'))  # 郵件純文字內容
        if type(Email_attachement) == str and Email_attachement != None:
            if os.path.exists(Email_attachement):
                filename = os.path.basename(Email_attachement)
                attachement = MIMEText(open(Email_attachement, 'rb').read(), 'base64', 'utf-8')
                attachement["Content-Type"] = 'application/octet-stream'
                attachement["Content-Disposition"] = f'attachment; filename="{filename}"'
                email.attach(attachement)
            else:
                log.info(f'Email_attachement Not Exist: {Email_attachement}')
        elif type(Email_attachement) == list and len(Email_attachement) != 0:
            for att in Email_attachement:
                if os.path.exists(att):
                    filename = os.path.basename(att)
                    attachement = MIMEText(open(att, 'rb').read(), 'base64', 'utf-8')
                    attachement["Content-Type"] = 'application/octet-stream'
                    attachement["Content-Disposition"] = f'attachment; filename="{filename}"'
                    email.attach(attachement)
                else:
                    log.info(f'Email_attachement Not Exist: {att}')
        with smtplib.SMTP(host=Email_info[0][1], port=int(Email_info[0][2])) as smtp:  # 設定SMTP伺服器
            for i in range(5):
                try:
                    log.info('Start ehlo')
                    smtp.ehlo()  # 驗證SMTP伺服器
                    log.info('ehlo Success')
                    log.info('Start starttls')
                    smtp.starttls()  # 建立加密傳輸
                    log.info('starttls Success')
                    log.info('Start login')
                    smtp.login(Email_info[0][0], Email_info[0][4])  # 登入寄件者gmail
                    log.info('login Success')
                    log.info('Start send Email')
                    smtp.send_message(email)  # 寄送郵件
                    log.info('Send Email success')
                    break
                except Exception as ex:
                    log.error("sent email Failed, Erroe message: {0}".format(ex))
    except Exception as ex:
        sign = '*' * 100 + '\n'
        errorMessage = f'{sign}>>>Exception Time：\t{datetime.now()}\n>>>Exception def：\t{sentEmail.__name__}\n>>>Exception msg：\t{ex}\n{traceback.format_exc()}{sign}'
        log.error(errorMessage)
        log.end('Email')