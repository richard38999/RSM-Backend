import os
import datetime as datetime
import sys
import SFTP
import Logger
import Configuration
import imaplib
import email
from email.header import decode_header
import decorator
import Email
import Utility
import pandas as pd
import openpyxl

log = Logger.Log('PAOB_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
sftp = SFTP.init('SCB_FPS_Report')
Settlement_Date = None
Transaction_Date = None
email_Transaction_date = None
Root_Folder = 'PAOB_Report'
email_result = False
notify_email_content = ''
attachment_name = ''
extract_folder = ''
alert_email_to = '' # if None, default send to richardding@eftpay.com.hk
email_body = ''
Email_attachment = None
for i in AlertEmail:
    if i[1] == 'PAOB_Report':  # i[1] == Project Name , i[0] == alert email address
        alert_email_to = i[0]
@decorator.except_output('PAOB_Report',
                         isSendEmail=True,
                         Email_to=alert_email_to,
                         Email_subject=f'[{email_result}] PAOB Report Upload Result({email_Transaction_date})',
                         Email_from=Email_info[0][3],
                         Email_displayName='PAOB Report')
def main():
    global email_body
    log.start('main')
    YYYYMM_Date = datetime.datetime.now().strftime("%Y%m")
    YYYYMMDD_Date = datetime.datetime.now().strftime("%Y%m%d")

    # daily report
    for i in range(1,7):
        process_YYYYMMDD_Date = (datetime.datetime.strptime(YYYYMMDD_Date, "%Y%m%d") + datetime.timedelta(days=-i)).strftime(
        "%Y%m%d")
        process_YYYYMM_Date = process_YYYYMMDD_Date[:6]
        create_folder(process_YYYYMM_Date=process_YYYYMM_Date)
        # get daily report
        csv_report_name = f'customertrans{process_YYYYMMDD_Date}.csv'
        excel_report_name = f'customertrans{process_YYYYMMDD_Date}.xlsx'
        excel_path = f'PAOB/excel/{process_YYYYMM_Date}/{excel_report_name}'
        csv_path = f'PAOB/csv/{process_YYYYMM_Date}/{csv_report_name}'

        if not get_report(Process_YYYYMMDD_Date=process_YYYYMMDD_Date, Process_YYYYMM_Date=process_YYYYMM_Date, report_name=csv_report_name, localPath=csv_path):
            continue
        csv_to_excel(csv_path=csv_path, excel_path=excel_path)
        upload_to_merchant_sftp(Process_YYYYMM_Date=process_YYYYMMDD_Date, report_name=excel_report_name, locaPath=excel_path)
    # Monthly Report


    send_email()
    log.end('main')

def create_folder(process_YYYYMM_Date=''):
    if not os.path.exists('PAOB'):
        os.mkdir('PAOB')
    if not os.path.exists(f'PAOB/csv'):
        os.mkdir(f'PAOB/csv')
    if not os.path.exists(f'PAOB/excel'):
        os.mkdir(f'PAOB/excel')
    if not os.path.exists(f'PAOB/csv/{process_YYYYMM_Date}'):
        os.mkdir(f'PAOB/csv/{process_YYYYMM_Date}')
    if not os.path.exists(f'PAOB/excel/{process_YYYYMM_Date}'):
        os.mkdir(f'PAOB/excel/{process_YYYYMM_Date}')

def get_report(Process_YYYYMMDD_Date='', Process_YYYYMM_Date='', report_name='', localPath=''):
    log.start('get_report')
    # YYYYMM_Date = datetime.datetime.now().strftime("%Y%m")
    remotePath = f'/home/eft/PAOB/upload/{Process_YYYYMM_Date}/{report_name}'
    if not sftp.checkSftpFile(SFTP_info[0], remotepath=remotePath):
        global email_body
        email_body += f"Con't fount the Report: {remotePath}"
        return False
    sftp.getSftpFile(SFTP_info[0], remotepath=remotePath, localpath=localPath)
    log.end('get_report')
    return True

def csv_to_excel(csv_path='', excel_path=''):
    pass
    log.start('csv_to_excel')
    # Reading the csv file
    df_new = pd.read_csv(csv_path)
    # saving xlsx file
    GFG = pd.ExcelWriter(excel_path)
    df_new.to_excel(GFG, index=False, header=True, encoding='utf-8')
    GFG.save()
    log.end('csv_to_excel')
def upload_to_merchant_sftp(Process_YYYYMM_Date='', report_name='', locaPath=''):
    global email_body
    log.start('upload_to_merchant_sftp')
    sftp.putSftpFile(SFTP_info[4], remotepath=f'/upload/{Process_YYYYMM_Date}/{report_name}', localpath=locaPath)
    email_body += f'{report_name}: Upload Success!\n'
    log.end('upload_to_merchant_sftp')
def send_email():
    global email_body
    log.start('send_email')
    Email.sentEmail(Log_Name='PAOB_Report',
                    Email_subject=f'[{email_result}] PAOB Report Upload Result({email_Transaction_date})',
                    Email_content=email_body,
                    Email_to=alert_email_to,
                    Email_from=Email_info[0][3],
                    Email_displayName='PAOB Report')
    log.end('send_email')

if __name__ == "__main__":
    log.start('PAOB_Report')
    main()
    log.end('PAOB_Report')