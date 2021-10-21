import Configuration
import smtplib
from Logger import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = Log('A8-Daily-Email')
log.start('A8 Daily Email')
Email_info = Configuration.get_Email_info()
Sent_To = Configuration.get_A8_PW_Email()

# url = 'http://10.17.2.238/password/'
# response = requests.get(url)
# temp = response.text.find('pw')
# password = str(response.text)
# password = password[temp+3:9+temp]
password = '123456'
to = ''
for i in Sent_To:
    to += (i[0]) + ';'
to = to[:len(to)-1]

date = time.strftime("%Y%m%d", time.localtime())
log.info('Today: {0}'.format(date))
content = MIMEMultipart()  # 建立MIMEMultipart物件
content["subject"] = "[{0}]A8 Daily Password: {1}".format(date, password)  # 郵件標題
log.info('Email subject: {0}'.format(content["subject"]))
content["from"] = 'RSM System'  # 寄件者
log.info('Email From: {0}'.format(content["from"]))
content["to"] = to # 收件者
log.info('Email to: {0}'.format(content["to"]))
content.attach(MIMEText("A8 Daily Password: {0}".format(password)))  # 郵件純文字內容
log.info("A8 Daily Password: {0}".format(password))
with smtplib.SMTP(host=Email_info[0][1], port=Email_info[0][2]) as smtp:  # 設定SMTP伺服器
    for i in range(5):
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(Email_info[0][0], Email_info[0][4])  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            log.info('sent email success')
            break
        except Exception as e:
            log.error("sent email Failed, Erroe message: {0}".format(e))

log.end('A8 Daily Email')