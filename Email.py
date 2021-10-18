import Configuration
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
content = MIMEMultipart()  # 建立MIMEMultipart物件
content["subject"] = "[{0}]A8 Daily Password: {1}".format(date, password)  # 郵件標題
content["from"] = 'RSM System'  # 寄件者
content["to"] = ','.join(Sent_To[0]) # 收件者
content.attach(MIMEText("A8 Password: {0}".format(password)))  # 郵件純文字內容
with smtplib.SMTP(host=Email_info[0][1], port=Email_info[0][2]) as smtp:  # 設定SMTP伺服器
    try:
        smtp.ehlo()  # 驗證SMTP伺服器
        smtp.starttls()  # 建立加密傳輸
        smtp.login(Email_info[0][0], Email_info[0][4])  # 登入寄件者gmail
        smtp.send_message(content)  # 寄送郵件
        print("Complete!")
    except Exception as e:
        print("Error message: ", e)