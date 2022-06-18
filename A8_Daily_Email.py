import Configuration
import smtplib
from Logger import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import Email
log = Log('A8-Daily-Email')
log.start('A8 Daily Email')
Email_info = Configuration.get_Email_info()
Sent_To = Configuration.get_A8_PW_Email()

url = 'http://10.17.2.238/password/'
response = requests.get(url)
temp = response.text.find('password')
password = str(response.text)
password = password[temp+10:temp+16]
# password = '123456'
to = ''
for i in Sent_To:
    to += (i[0]) + ';'
to = to[:len(to)-1]

date = time.strftime("%Y%m%d", time.localtime())
log.info('Today: {0}'.format(date))
# content = MIMEMultipart()  # 建立MIMEMultipart物件
Email_subject = "[{0}]A8 Daily Password: {1}".format(date, password)  # 郵件標題
log.info('Email subject: {0}'.format(Email_subject))
Email_from = 'no.reply@eftpay.com.hk'  # 寄件者
log.info('Email From: {0}'.format(Email_from))
Email_to = to # 收件者
log.info('Email to: {0}'.format(to))
Email_content = "A8 Daily Password: {0}".format(password)  # 郵件純文字內容
log.info('Email Content: {0}'.format(Email_content))
Email.sentEmail(Email_to=to,
                Email_subject=Email_subject,
                Email_content=Email_content)
# with smtplib.SMTP(host=Email_info[0][1], port=Email_info[0][2]) as smtp:  # 設定SMTP伺服器
#     for i in range(5):
#         try:
#             # log.info('Start ehlo')
#             # smtp.ehlo()  # 驗證SMTP伺服器
#             # log.info('ehlo Success')
#             log.info('Start starttls')
#             smtp.set_debuglevel(1)
#             smtp.starttls()  # 建立加密傳輸
#             log.info('starttls Success')
#             log.info('Start login')
#             smtp.login(Email_info[0][0], Email_info[0][4])  # 登入寄件者gmail
#             log.info('login Success')
#             log.info('Start send Email')
#             # smtp.send_message(email, from_addr=Email_from, to_addrs=to_addrs)  # 寄送郵件
#             smtp.send_message(email)  # 寄送郵件
#             sentResult = True
#             log.info('Send Email success')
#             break
#         except Exception as e:
#             log.error("sent email Failed, Erroe message: {0}".format(e))

log.end('A8 Daily Email')