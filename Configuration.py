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
DB_path = 'DataBase\\RSM_TEST.db'

def get_Merchant_Info():
    conn = sqlite3.connect(DB_path)
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
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM Email_info;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    Email_info = values
    return Email_info

def get_SFTP_info():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM SFTP_Info;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    sftp_info = values
    return sftp_info

def get_Alert_Email():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM AlertEmailList;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    sftp_info = values
    return sftp_info

def get_A8_PW_Email():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM A8_PW_Email;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    A8_PW_Email = values
    return A8_PW_Email

def get_Maxims_VMP_Report_Config():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM Maxims_VMP_Report_Config;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    Maxims_VMP_Report_Config = values
    return Maxims_VMP_Report_Config

def get_Settlement_Report_DailyEmail_Config():
    conn = sqlite3.connect(DB_path)
    cursor = conn.cursor()
    cursor.execute('select * FROM Settlement_Report_DailyEmail_Config;')
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    Settlement_Report_DailyEmail_Config = values
    return Settlement_Report_DailyEmail_Config

class Config():
    FrontEndVersion = ''
    isSentEmailAlert = None
    Environment = None

def loadConfig():
    Configuration = Config()
    config = configparser.ConfigParser()
    config.read("config.ini")
    Configuration.FrontEndVersion = config['Flask_Base_config']['FrontEnd Version']
    Configuration.Environment = config['Flask_Base_config']['Environment']
    if Configuration.Environment == 'PROD':
        Configuration.isSentEmailAlert = config['Flask_PROD_config']['isSentEmailAlert']
    elif Configuration.Environment == 'DEV':
        Configuration.isSentEmailAlert = config['Flask_DEV_config']['isSentEmailAlert']
    return Configuration

class Flask_Base_Config():
    JWT_SECRET_KEY = 'Testing123'
    FrontEndVersion = '1.0.19'

class Flask_PROD_Config(Flask_Base_Config):
    ENV = 'production'
    DEBUG = False
    isSentEmail = True

class Flask_DEV_Config(Flask_Base_Config):
    ENV = 'development'
    DEBUG = True
    isSentEmail = False

Flask_Config = {
    'DEV': Flask_DEV_Config,
    'PROD': Flask_PROD_Config
}