import os
import csv
import sys
import datetime as datetime
import pysftp
import Logger
import Configuration
import decorator
import Email
log = Logger.Log('CLP_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
Maxims_VMP_Report_Config = Configuration.get_Maxims_VMP_Report_Config()
today = ''
day_of_year = ''
Result = False
sftp = None
emailContent = ''
class PID_Content:
    Partner_transaction_id = None
    Transaction_id = None
    Amount = None
    Fee = None
    Currency = None
    Payment_time = None
    Type = None
    Settlement_time = None
    MCC = None
    Merchant = None
    Merchant_ID = None
    Remarks = None
    Product = None
    Trans_Currency = None
    Trans_Amount = None
    Trans_forex_rate = None
    Issue = None

class MID_Content():
    class RD:
        RecordIdentifier = None
        SettlementDate = None
        TerminalID = None
        BatchNumber = None
        TransactionDate = None
        BarCodeNumber = None
        Type = None
        Currency = None
        SignofTransactionamount = None
        TransactionAmount = None
        ApprovalCode = None
        TraceNumber = None
        SignofMDRfee = None
        MDRfee = None
        OrderID = None
        EFTPRefNumber = None
        StoreID = None
        WalletCurrency = None
        TransactionEntrymode = None
        Filler = None

    class RT:
        RecordIdentifier = None
        TotalofTrasaction = None
        SignofTotalamount = None
        TotalofAmount = None
        TotalofFee = None
        Filler = None

    class RH:
        RecordIdentifier = None
        FileID = None
        FileDate = None
        Rateoffee = None
        MID = None
        MIDname = None
        PID = None
        Filler = None

def getSftpFile(SFTP_info, remotepath=None, localpath=None):
    log.start('getSftpFile')
    log.info('start Connection')
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
    log.info('end Connection')
    log.info('start get file, localpath: {0}'.format(localpath))
    log.info('start get file, remotepath: {0}'.format(remotepath))
    sftp.get(remotepath, localpath=localpath)
    log.info('end get file')
    log.info('start SFTP close')
    sftp.close()
    log.info('end SFTP close')
    log.end('getSftpFile')
def putSftpFile(SFTP_info, localpath=None, remotepath=None):
    log.start('putSftpFile')
    log.info('start Connection')
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
    log.info('end Connection')
    log.info('start put file, localpath: {0}'.format(localpath))
    log.info('start put file, remotepath: {0}'.format(remotepath))
    sftp.put(localpath, remotepath=remotepath)
    log.info('end put file')
    log.info('start SFTP close')
    sftp.close()
    log.info('end SFTP close')
    log.end('putSftpFile')
def checkSftpFile(SFTP_info, remotepath=None):
    isExist = None
    log.start('checkSftpFile')
    log.info('start Connection')
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
    log.info('end Connection')
    log.info('start check file, remotepath: {0}'.format(remotepath))
    isExist = sftp.exists(remotepath)
    log.info('end check file')
    log.info(f'remote file isExist: {isExist}')
    log.info('start SFTP close')
    sftp.close()
    log.info('end SFTP close')
    log.end('checkSftpFile')
    return isExist

def read_PID_Report(localpath=''):
    log.start('read_PID_Report')
    returnMessage = PID_Content()
    list_returnMessage = []
    f = open(localpath, 'r')
    rows = csv.reader(f, delimiter='|')
    for row in rows:
        log.info(row)
        returnMessage.Partner_transaction_id = row[0]
        returnMessage.Transaction_id = row[1]
        returnMessage.Amount = row[2]
        returnMessage.Fee = row[3]
        returnMessage.Currency = row[4]
        returnMessage.Payment_time = row[5]
        returnMessage.Type = row[6]
        returnMessage.Settlement_time = row[7]
        returnMessage.MCC = row[8]
        returnMessage.Merchant = row[9]
        returnMessage.Merchant_ID = row[10]
        returnMessage.Remarks = row[11]
        returnMessage.Product = row[12]
        returnMessage.Trans_Currency = row[13]
        returnMessage.Trans_Amount = row[14]
        returnMessage.Trans_forex_rate = row[15]
        returnMessage.Issue = row[16]
        list_returnMessage.append(returnMessage)
    log.end('read_PID_Report')
    return list_returnMessage

def read_RawMID_Report(localpath=''):
    log.start('read_RawMID_Report')
    returnMessage = MID_Content()

    f = open(localpath, 'r')
    rows = csv.reader(f, delimiter='|')
    for row in rows:
        if row[0:2] == 'RH':
            returnMessage.RH.RecordIdentifier = row[0:2]
            returnMessage.RH.FileID = row[2:10]
            returnMessage.RH.FileDate = row[10:18]
            returnMessage.RH.Rateoffee = row[18:23]
            returnMessage.RH.MID = row[23:38]
            returnMessage.RH.MIDname = row[38:68]
            returnMessage.RH.PID = row[68:96]
            returnMessage.RH.Filler = row[96:200]
        elif row[0:2] == 'RD':
            returnMessage.RD.RecordIdentifier = row[0:3]
            returnMessage.RD.SettlementDate = row[2:12]
            returnMessage.RD.TerminalID = row[12:20]
            returnMessage.RD.BatchNumber = row[20:26]
            returnMessage.RD.TransactionDate = row[26:41]
            returnMessage.RD.BarCodeNumber = row[41:60]
            returnMessage.RD.Type = row[60:70]
            returnMessage.RD.Currency = row[70:73]
            returnMessage.RD.SignofTransactionamount = row[73:74]
            returnMessage.RD.TransactionAmount = row[74:86]
            returnMessage.RD.ApprovalCode = row[86:92]
            returnMessage.RD.TraceNumber = row[92:98]
            returnMessage.RD.SignofMDRfee = row[98:99]
            returnMessage.RD.MDRfee = row[99:110]
            returnMessage.RD.OrderID = row[110:174]
            returnMessage.RD.EFTPRefNumber = row[174:186]
            returnMessage.RD.StoreID = row[186:194]
            returnMessage.RD.WalletCurrency = row[194:197]
            returnMessage.RD.TransactionEntrymode = row[197:198]
            returnMessage.RD.Filler = row[198:200]
        elif row[0:2] == 'RT':
            returnMessage.RT.RecordIdentifier = row[0:2]
            returnMessage.RT.TotalofTransaction = row[2:11]
            returnMessage.RT.SignofTotalamount = row[11:12]
            returnMessage.RT.TotalofAmount = row[12:30]
            returnMessage.RT.TotalofFee = row[30:48]
            returnMessage.RT.Filler = row[48:200]
    return returnMessage
def writeEOPGFile(path=None, data=None):
    log.start('writeEOPGFile')
    log.info('path: {0}'.format(path))
    log.info('data: {0}'.format(data))
    f = open(path, "w")
    f.write(data)
    f.close()
    log.end('writeEOPGFile')
    return True

def convertDataToEopgFormat():
    returnData = ''
    log.start('convertDataToEopgFormat')
    # RH: Record Identifier, 2, (RH)
    returnData += RH.RecordIdentifier
    # RH: File ID, 8, (Year+’N’+day of year, in YYYYXddd format. Example: 2013-2-1 = 2013N032)
    returnData += today[:4] + 'N' + day_of_year
    # RH: File Date, 8, (In CCYYMMDD format. It should be the current processing date.)
    returnData += today
    # RH: Rate of fee, 5, (With 2 decimal points)
    returnData += '00120'
    # RH: MID, 15
    returnData += RH.MID.rjust(15, ' ')
    # RH: MID name, 30
    returnData += RH.MIDname.rjust(30, ' ')
    # RH: PID, 28
    returnData += '2088031839616494'.rjust(28,' ')
    # RH: Filler, 156
    returnData += ' ' * 156
    returnData += '\n'
    for rd in RD:
        # RD: Record Identifier, 2, (RD)
        returnData += rd.RecordIdentifier
        # RD: Settlement Date, 10, (In CCYY/MM/DD format)
        returnData += '{0}/{1}/{2}'.format(rd.TransactionDate[:4],rd.TransactionDate[4:6],rd.TransactionDate[-2:])
        # RD: Terminal ID, 8, (Space if no information or non-numeric value)
        returnData += rd.TerminalID.rjust(8, ' ')
        # RD: Batch Number, 6, (Space if no information or non-numeric value)
        returnData += ' ' * 6
        # RD: Transaction Date, 15, (In YYYYMMDD:HH24MISS format)
        returnData += '{0}:{1}'.format(rd.TransactionDate, rd.TransactionTime)
        # RD: BarCode Number, 19, (Space if no information or non-numeric value)
        returnData += ' ' * 19
        # RD: Type, 10, (ALIPAY)
        returnData += rd.PaymentType.rjust(10, ' ')
        # RD: Currency, 3, (e.g. “HKD”,”RMB”,”USD”)
        returnData += 'HKD'
        # RD: Sign of Transaction amount, 1, ('-' means negative amount ' ' means positive amount)
        if rd.TransType == 'R':
            returnData += '-'
        elif rd.TransType == 'S':
            returnData += ' '
        # RD: Transaction Amount, 12, (With 2 decimal points)
        returnData += str(int(round(float(rd.TransactionamountHKD) * 100, 2))).zfill(12)
        # RD: Approval Code, 6, (Space if no information or non-numeric value)
        returnData += ' ' * 6
        # RD: Trace Number, 6, (Space if no information or non-numeric value)
        returnData += ' ' * 6
        # RD: Sign of MDR fee, 1, ('-' means negative amount ' ' means positive amount)
        if rd.TransType == 'R':
            returnData += '-'
        elif rd.TransType == 'S':
            returnData += ' '
        # RD: Alipay MDR fee, 11, (With 2 decimal points)
        returnData += str(int(round(float(rd.MDRFeeHKD) * 100, 2))).zfill(11)
        # RD: Alipay Order ID, 64, (Space if no information or non-numeric value)
        returnData += rd.Settlementno.rjust(64, ' ')
        # RD: EFTP Ref Number, 64, ()
        returnData += rd.MerchantRRN.rjust(64,' ')
        # RD: Store ID, 8, (Space if no information or non-numeric value)
        returnData += ' '*8
        # RD: Wallet Currency, 3, (e.g. “HKD”,”RMB”)
        if rd.WalletVersion[-2:] == 'HK':
            returnData += 'HKD'
        elif rd.WalletVersion[-2:] == 'CN':
            returnData += 'RMB'
        # RD: Transaction Entry mode, 1, (1- Spot Barcode Payment 2- QRCode Payment 3- Online Payment 4- Apps Payment)
        returnData += '3'
        # RD: Filler, 2, (Filled with spaces)
        returnData += ' '*2
        returnData += '\n'

    # RT: Record Identifier, 2, (RT)
    returnData += RT.RecordIdentifier
    # RT: Total of Transaction, 9,
    returnData += RT.TotalofTrasaction.zfill(9)
    # RT: Sign of Total amount, 1, ('-' means negative amount ' ' means positive amount)
    if RT.TotalofAmount[0] == '-':
        returnData += '-'
    else:
        returnData += ' '
    # RT: Total of Amount, 18, (With 2 decimal points)
    returnData += str(int(round(float(RT.TotalofAmount) * 100, 2))).zfill(18)
    # RT: Total of Fee, 18, (With 2 decimal points)
    returnData += str(int(round(float(RT.TotalofFee) * 100, 2))).zfill(18)
    # RT: Filler, 204, (Filled with spaces)
    returnData += ' '*204
    returnData += '\n'
    return [True, returnData]
@decorator.except_output('CLP_Report', isSendEmail=True, Email_subject='CLP_Report Error Alert!')
def main():
    log.start('CLP_Report')
    log.info(str(sys.argv))
    MID = '852000049000001'
    PID = '2088331466052909'
    global today
    global day_of_year
    global Result
    global sftp
    global emailContent
    if len(sys.argv) == 2:
        today = sys.argv[1]
    else:
        today = datetime.datetime.now().strftime("%Y%m%d")
    today = '20211127'
    Result = False
    log.info(f'MID: {MID}')
    log.info(f'PID: {PID}')
    TransDatetime_8_digits = (datetime.datetime.strptime(today,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    log.info(f'TransDatetime_8_digits: {TransDatetime_8_digits}')
    currentlyPath = os.getcwd()
    if not os.path.exists(currentlyPath + f'\\Settlement_Report\\CLP_Report'):
        os.makedirs(currentlyPath + f'\\Settlement_Report\\CLP_Report')
    if not os.path.exists(currentlyPath + f'\\Settlement_Report\\CLP_Report\\PID_Report'):
        os.makedirs(currentlyPath + f'\\Settlement_Report\\CLP_Report\\PID_Report')
    if not os.path.exists(currentlyPath + f'\\Settlement_Report\\CLP_Report\\RawMID_Report'):
        os.makedirs(currentlyPath + f'\\Settlement_Report\\CLP_Report\\RawMID_Report')
    if not os.path.exists(currentlyPath + f'\\Settlement_Report\\CLP_Report\\ParseMID_Report'):
        os.makedirs(currentlyPath + f'\\Settlement_Report\\CLP_Report\\ParseMID_Report')
    PID_File_Remote_Path = f'/settlefile/{TransDatetime_8_digits}/{PID}.{TransDatetime_8_digits}'
    log.info(f'PID_File_Remote_Path: {PID_File_Remote_Path}')
    PID_File_Local_Path = currentlyPath + f'\\Settlement_Report\\CLP_Report\\PID_Report\\{PID}.{TransDatetime_8_digits}'
    log.info(f'PID_File_Local_Path: {PID_File_Local_Path}')
    RawMID_File_Remote_Path = f'/settlefile/{TransDatetime_8_digits}/{MID}.{TransDatetime_8_digits}'
    log.info(f'RawMID_File_Remote_Path: {RawMID_File_Remote_Path}')
    RawMID_File_Local_Path = currentlyPath + f'\\Settlement_Report\\CLP_Report\\RawMID_Report\\{MID}.{TransDatetime_8_digits}'
    log.info(f'RawMID_File_Local_Path: {RawMID_File_Local_Path}')
    ParseMID_File_Remote_Path = f'/home/{MID}/settlefile/{MID}.{TransDatetime_8_digits}'
    log.info(f'ParseMID_File_Remote_Path: {ParseMID_File_Remote_Path}')
    ParseMID_File_Local_Path = currentlyPath + f'\\Settlement_Report\\CLP_Report\\ParseMID_Report\\{MID}.{TransDatetime_8_digits}'
    log.info(f'ParseMID_File_Local_Path: {ParseMID_File_Local_Path}')

    EOPG_File_Remote_folder = f'/home/{MID}/eopgfile'
    log.info(f'EOPG_File_Remote_folder: {EOPG_File_Remote_folder}')
    # check PID file
    if not checkSftpFile(SFTP_info[1], remotepath=PID_File_Remote_Path):
        emailContent = f'remotepath Not Exist: {PID_File_Remote_Path}'
        log.info(emailContent)
        Result = False
        Email.sentEmail(Log_Name='CLP_Report', Email_subject=f'[{Result}]CLP_Report ({today}) - {PID}', Email_content=emailContent)
        log.end('CLP_Report')
        return
    # get PID file
    getSftpFile(SFTP_info[1],localpath=PID_File_Local_Path,remotepath=PID_File_Remote_Path)
    # check Raw MID file
    if not checkSftpFile(SFTP_info[1], remotepath=RawMID_File_Remote_Path):
        emailContent = f'remotepath Not Exist: {RawMID_File_Remote_Path}'
        log.info(emailContent)
        Result = False
        Email.sentEmail(Log_Name='CLP_Report', Email_subject=f'[{Result}]CLP_Report ({today}) - {MID}', Email_content=emailContent)
        log.end('CLP_Report')
        return
    # get Raw MID File
    getSftpFile(SFTP_info[1], localpath=RawMID_File_Local_Path, remotepath=RawMID_File_Remote_Path)
    PID_Report = read_PID_Report(localpath=PID_File_Local_Path)
    RawMID_Report = read_RawMID_Report(localpath=RawMID_File_Local_Path)
    # ParseMID_Report = Combine_Report(localpath=ParseMID_File_Local_Path)

    putSftpFile(SFTP_info, localpath=ParseMID_File_Local_Path, remotepath=ParseMID_File_Remote_Path)
    Result = True
    emailContent = f'''
    Settlement  Date: {today}\n
    Transaction Date: {TransDatetime_8_digits}\n
    Total Transaction: {RT.TotalofTrasaction}\n
    Total Fee: {RT.TotalofFee}\n
    Total Amount: {RT.TotalofAmount}'''
    Email.sentEmail(Log_Name='CLP_Report', Email_subject=f'[{Result}]CLP_Report ({today}) - {MID}',
                    Email_content=emailContent, Email_attachement=[PID_File_Local_Path, RawMID_File_Local_Path, ParseMID_File_Local_Path])
    log.end('CLP_Report')

if __name__ == '__main__':
    main()