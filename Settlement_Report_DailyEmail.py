import os
import datetime as datetime
from zipfile import ZipFile
import SFTP
import Logger
import Configuration
import decorator
import Email
import time
import Utility

log = Logger.Log('Settlement_Report_DailyEmail')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
sftp = SFTP.init('Settlement_Report_DailyEmail')
@decorator.except_output('Settlement_Report_DailyEmail', isSendEmail=True, Email_subject='Settlement_Report_DailyEmail Error Alert!')
def main():
    Settlement_Report_DailyEmail_Config = Configuration.get_Settlement_Report_DailyEmail_Config()
    SettlementDate_6_digits = datetime.datetime.now().strftime("%y%m%d")
    SettlementDate_8_digits = datetime.datetime.now().strftime("%Y%m%d")
    # EmailDatetime_8_digits = datetime.datetime.now().strftime("%Y-%m-%d")
    TransDatetime_8_digits = (datetime.datetime.strptime(SettlementDate_8_digits,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    EmailDatetime_8_digits = (datetime.datetime.strptime(SettlementDate_8_digits,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    TransDatetime_6_digits = (datetime.datetime.strptime(SettlementDate_8_digits,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%y%m%d")
    # Check DB record if need to write today config or not
    totayConfig = Utility.SQL_script(f'select * FROM Settlement_Report_DailyEmail_Result where date={TransDatetime_8_digits};')
    emailContent = ''
    Result = 'UnConfirm'
    def parseDateFormat(fileFormat=None, TransDatetime_8_digits=None,TransDatetime_6_digits=None):
        fileName = ''
        if str(fileFormat).find('YYYYMMDD') != -1:
            fileName = fileFormat.replace('YYYYMMDD', TransDatetime_8_digits)
        elif str(fileFormat).find('YYMMDD') != -1:
            fileName = fileFormat.replace('YYMMDD', TransDatetime_6_digits)
        return fileName

    if totayConfig == []:
        log.info('Write Today Config Start!')
        for i in Settlement_Report_DailyEmail_Config:
            Utility.SQL_script(f'insert INTO Settlement_Report_DailyEmail_Result VALUES("{TransDatetime_8_digits}", {i[0]}, "N");')
        log.info('Write Today Config End!')
    # check if now is the right time to sent report ot not?
    SentResult = Utility.SQL_script(f'select DISTINCT * from Settlement_Report_DailyEmail_Result Result LEFT JOIN Settlement_Report_DailyEmail_Config Config on Result.id = Config.id where Result.date = "{TransDatetime_8_digits}";')
    for i in SentResult:
        if i[2] == 'N':
            if int(time.strftime("%H%M", time.localtime())) >= int(i[6]):
                filename = parseDateFormat(fileFormat=(i[10]), TransDatetime_8_digits=TransDatetime_8_digits, TransDatetime_6_digits=TransDatetime_6_digits)
                remotepath = i[9] + '/' + filename
                if not sftp.checkSftpFile(SFTP_info[int(i[11])], remotepath=remotepath):
                    emailContent += f'{i[4]}_{i[8]} - remotepath Not Exist: {remotepath}\r\n{"-"*180}\r\n'
                    Result = False
                    continue
                else:
                    if not os.path.exists(os.getcwd() + f'\\Settlement_Report\\Settlement_Report_DailyEmail'):
                        os.mkdir(os.getcwd() + f'\\Settlement_Report\\Settlement_Report_DailyEmail')
                    if not os.path.exists(os.getcwd() + f'\\Settlement_Report\\Settlement_Report_DailyEmail\\{i[4]}_{i[8]}'):
                        os.mkdir(os.getcwd() + f'\\Settlement_Report\\Settlement_Report_DailyEmail\\{i[4]}_{i[8]}')
                    localpath = os.getcwd() + f'\\Settlement_Report\\Settlement_Report_DailyEmail\\{i[4]}_{i[8]}\\{filename}'
                    sftp.getSftpFile(SFTP_info[int(i[11])], remotepath=remotepath, localpath=localpath)
                    if i[12] == 'Y': # ZIP Attachement
                        basename = os.path.basename(localpath)
                        file_name = os.path.splitext(basename)[0]
                        ziplocalpath = f'Settlement_Report\\Settlement_Report_DailyEmail\\{i[4]}_{i[8]}\\{file_name}.zip'
                        with ZipFile(ziplocalpath, 'w') as myzip:
                            myzip.write(localpath, filename)
                        localpath = ziplocalpath
                    MerchantemailContent = \
                    f"                   ---- Please do not reply to this email as this email address is used for broadcasting messages to clients only. ---\r\n\r\n"\
                    "Dear " + i[4] + ",\r\n\r\n"\
                    f"Please find attached the settlement files for {EmailDatetime_8_digits} for your reference.Please carefully examine the attached information and make note of any important messages contained therein.\r\n\r\n" \
                    "Should you have any questions, please send an email to service@eftpay.com.hk or contact us at(852) 3741 2116 and we will get back to you as soon as possible.\r\n\r\n\r\n" \
                    "Note:\r\n" \
                    "All settlement files will be retained for 12 months from the issue date, after which the documents will be automatically removed.\r\n\r\n\r\n\r\n" \
                    "Best regards,\r\n" \
                    "Customer Service Team\r\n\r\n" \
                    "                                                   ---- 此電郵地址只用作傳送訊息，請不要回覆此電郵。 ---\r\n\r\n" \
                    "尊貴的" + i[4] + ",\r\n\r\n" \
                    f"附件是{EmailDatetime_8_digits}的結算文件以供參考。請小心細閱結算文件內的所有資料和重要訊息\r\n\r\n" \
                    "如有任何疑問，請電郵至 service@eftpay.com.hk 或致電(852) 3741 2116與我們聯絡。我們會盡快回覆。 \r\n\r\n\r\n" \
                    "註:\r\n" \
                    "所有結算文件將由發出日期起計保留12個月，其後將會自動清除。\r\n\r\n\r\n\r\n" \
                    "客戶服務團隊 謹致"\

                    if Email.sentEmail(Log_Name='Settlement_Report_DailyEmail',
                                    Email_subject=f'{i[4]} - {i[8]} Settlement Files 結算文件 ({EmailDatetime_8_digits})',
                                    Email_content=MerchantemailContent,
                                    Email_to=i[7],
                                    Email_from=Email_info[0][3],
                                    Email_displayName='EFT Settlement Report',
                                    Email_attachement=localpath) == False:
                        continue
                    emailContent += f'[{i[4]}_{i[8]} : {i[5]}] Success!\nEmail Address: {i[7]}\r\n-----------------------------------------------------------------------------------------------\n'
                    Utility.SQL_script(f'update Settlement_Report_DailyEmail_Result set IsSentEmail="Y" where Date="{i[0]}" and id="{i[1]}";')
                    log.info(f'{i[4]}_{i[8]} ({i[5]}) - Sent email Success - to: {i[7]}')
            else:
                log.info(f'{i[4]}_{i[8]} ({i[5]}): Not the right time to send email')
                continue
        else:
            log.info(f'{i[4]}_{i[8]} ({i[5]}): Already sent email!')
            continue
    if Result == 'UnConfirm':
        Result = 'Success'
    if emailContent != '':
        emailHeader = "This is an automatically generated email - please do not reply to this e-mail. Thank you.\r\n\r\n"
        emailContent = emailHeader + emailContent
        Email.sentEmail(Log_Name='Settlement_Report_DailyEmail',
                        Email_subject=f'[{Result}]Daily Merchant Report ({EmailDatetime_8_digits})',
                        Email_content=emailContent)
if __name__ == '__main__':
    log.start('Settlement_Report_DailyEmail')
    main()
    log.end('Settlement_Report_DailyEmail')