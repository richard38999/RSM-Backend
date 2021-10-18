import sqlite3
import configparser
'''
# Connect to Sqlite
# 如果文件不存在，程序會自動在當前目錄創建
db_name = "param.db"
conn = sqlite3.connect(db_name)
# 創建一個Cursor游標:
cursor = conn.cursor()
# 執行一條SQL語句：
cursor.execute('please input the sql command')
# Close the Cursor
cursor.close()
# 提交command
conn.commit()
# Close the connection
conn.close()

# 獲取sqlite數據
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
# 執行查詢語句
cursor.execute('please input the sql command')
values = cursor.fetchall()
print(values)
cursor.close()
conn.close()
'''
db_name = 'param.db'
def get_Merchant_Info():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM MerchantList;')
    values = cursor.fetchall()
    '''
    for i in values:
        Merchant_Name = i[0]
        Merchant_ID = i[1]
        GetReportTime = i[2]
        IsSentEmail = i[3]
        Merchant_EmailList = i[4]
        Payment_Type = i[5]
        SFTP_Report_Path = i[6]
        print(" Merchant_Name : {} \r\n Merchant_ID : {} \r\n GetReportTime : {}\r\n IsSentEmail : {}\r\n Merchant_EmailList : {}\r\n Payment_Type : {}\r\n SFTP_Report_Path : {}".format(Merchant_Name,Merchant_ID,GetReportTime,IsSentEmail,Merchant_EmailList,Payment_Type,SFTP_Report_Path))
    #print(values)
    '''
    cursor.close()
    conn.close()
    Merchant_info = values
    return Merchant_info

def get_Email_info():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM Email_info;')
    values = cursor.fetchall()
    #print(values)
    cursor.close()
    conn.close()
    Email_info = values
    return Email_info


def get_SFTP_info():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM SFTP_Info;')
    values = cursor.fetchall()
    #print(values)
    cursor.close()
    conn.close()
    sftp_info = values
    return sftp_info

def get_Alert_Email():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM AlertEmailList;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    sftp_info = values
    return sftp_info

def get_A8_PW_Email():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM A8_PW_Email;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    A8_PW_Email = values
    return A8_PW_Email

class Config():
    FrontEndVersion = ''

def loadConfig():
    Configuration = Config()
    config = configparser.ConfigParser()
    config.read("config.ini")
    Configuration.FrontEndVersion = config['config']['FrontEnd Version']
    return Configuration
