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
TransDatetime_8_digits = ''
day_of_year = ''
Result = False
sftp = None
emailContent = ''
PID_Amount_Total = 0
PID_Fee_Total = 0
PID_Txns_Total = 0
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
    TotalofTransaction = None
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
    list_returnMessage = []
    f = open(localpath, 'r')
    rows = csv.reader(f, delimiter='|')
    for row in rows:
        log.info(row)
        if len(row) != 17:
            continue
        returnMessage = PID_Content()
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
    rh = RH()
    list_rd = []
    rt = RT()
    f = open(localpath, 'r')
    line = 1
    try:
        rows = f.read()
        filelength = len(rows)
        while True:
            if filelength >= line * 200:
                row = rows[(line-1)*200:(200*line)-1]
                if row[0:2] == 'RH':
                    rh.RecordIdentifier = row[0:2]
                    rh.FileID = row[2:10]
                    rh.FileDate = row[10:18]
                    rh.Rateoffee = row[18:23]
                    rh.MID = row[23:38]
                    rh.MIDname = row[38:68]
                    rh.PID = row[68:96]
                    rh.Filler = ' ' * 104
                elif row[0:2] == 'RD':
                    rd = RD()
                    rd.RecordIdentifier = row[0:3]
                    rd.SettlementDate = row[2:12]
                    rd.TerminalID = row[12:20]
                    rd.BatchNumber = row[20:26]
                    rd.TransactionDate = row[26:41]
                    rd.BarCodeNumber = row[41:60]
                    rd.Type = row[60:70]
                    rd.Currency = row[70:73]
                    rd.SignofTransactionamount = row[73:74]
                    rd.TransactionAmount = row[74:86]
                    rd.ApprovalCode = row[86:92]
                    rd.TraceNumber = row[92:98]
                    rd.SignofMDRfee = row[98:99]
                    rd.MDRfee = row[99:110]
                    rd.OrderID = row[110:174]
                    rd.EFTPRefNumber = row[174:186]
                    rd.StoreID = row[186:194]
                    rd.WalletCurrency = row[194:197]
                    rd.TransactionEntrymode = row[197:198]
                    rd.Filler = row[198:200]
                    list_rd.append(rd)
                elif row[0:2] == 'RT':
                    rt.RecordIdentifier = row[0:2]
                    rt.TotalofTransaction = row[2:11]
                    rt.SignofTotalamount = row[11:12]
                    rt.TotalofAmount = row[12:30]
                    rt.TotalofFee = row[30:48]
                    rt.Filler = row[48:]
                line += 1
            else:
                break
    finally:
        f.close()

    return [rh,list_rd,rt]

def Combine_Report(localpath=None, PID_Report=None,RawMID_Report=None):
    WriteData = ''
    global PID_Amount_Total
    global PID_Fee_Total
    global PID_Txns_Total
    global TransDatetime_8_digits
    # Raw MID RH
    WriteData += RawMID_Report[0].RecordIdentifier
    WriteData += RawMID_Report[0].FileID
    WriteData += RawMID_Report[0].FileDate
    WriteData += RawMID_Report[0].Rateoffee
    WriteData += RawMID_Report[0].MID
    WriteData += RawMID_Report[0].MIDname
    WriteData += RawMID_Report[0].PID
    WriteData += RawMID_Report[0].Filler
    # Raw MID RD
    for row in RawMID_Report[1]:
        WriteData += row.RecordIdentifier
        WriteData += row.SettlementDate
        WriteData += row.TerminalID
        WriteData += row.BatchNumber
        WriteData += row.TransactionDate
        WriteData += row.BarCodeNumber
        WriteData += row.Type
        WriteData += row.Currency
        WriteData += row.SignofTransactionamount
        WriteData += row.TransactionAmount
        WriteData += row.ApprovalCode
        WriteData += row.TraceNumber
        WriteData += row.SignofMDRfee
        WriteData += row.MDRfee
        WriteData += row.OrderID
        WriteData += row.EFTPRefNumber
        WriteData += row.StoreID
        WriteData += row.WalletCurrency
        WriteData += row.TransactionEntrymode
        WriteData += row.Filler
    # get PID Report Summary
    for i in PID_Report:
        if i.Product == 'shopQrCode':
            PID_Amount_Total += int(round(float(i.Amount) * 100, 2))
            PID_Fee_Total += int(round(float(i.Fee) * 100, 2))
            PID_Txns_Total += 1
            WriteData += 'RD'
            WriteData += '{0}/{1}/{2}'.format(TransDatetime_8_digits[:4],TransDatetime_8_digits[4:6],TransDatetime_8_digits[-2:])
            WriteData += ' ' * 8
            WriteData += '000001'
            WriteData += str(i.Payment_time).replace('-', '').replace(':', '').replace(' ', ':')
            WriteData += ' ' * 19
            WriteData += 'PAYMENT'.ljust(10, ' ')
            WriteData += i.Currency
            WriteData += ' '
            WriteData += str(int(round(float(i.Amount) * 100, 2))).zfill(12)
            WriteData += ' ' * 6
            WriteData += ' ' * 6
            WriteData += ' '
            WriteData += str(int(round(float(i.Fee) * 100, 2))).zfill(11)
            WriteData += i.Transaction_id.ljust(64, ' ')
            WriteData += ' ' * 12
            WriteData += ' ' * 8
            WriteData += i.Trans_Currency
            WriteData += '2'
            WriteData += ' ' * 2
    # Raw MID RT
    WriteData += RawMID_Report[2].RecordIdentifier
    WriteData += str(int(RawMID_Report[2].TotalofTransaction) + PID_Txns_Total).zfill(9)
    WriteData += RawMID_Report[2].SignofTotalamount
    WriteData += str(int(RawMID_Report[2].TotalofAmount) + PID_Amount_Total).zfill(18)
    WriteData += str(int(RawMID_Report[2].TotalofFee) + PID_Fee_Total).zfill(18)
    WriteData += ' ' * 152
    print(len(RawMID_Report[2].Filler))
    print(RawMID_Report[2].Filler)
    return writeCombineFile(path=localpath,data=WriteData)

def writeCombineFile(path=None, data=None):
    log.start('writeCombineFile')
    log.info('path: {0}'.format(path))
    log.info('data: {0}'.format(data))
    f = open(path, "w")
    f.write(data)
    f.close()
    log.end('writeCombineFile')
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
    returnData += RT.TotalofTransaction.zfill(9)
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
    global TransDatetime_8_digits
    if len(sys.argv) == 2:
        today = sys.argv[1]
    else:
        today = datetime.datetime.now().strftime("%Y%m%d")

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
    ParseMID_Report = Combine_Report(localpath=ParseMID_File_Local_Path, PID_Report=PID_Report,RawMID_Report=RawMID_Report)
    if ParseMID_Report:
        putSftpFile(SFTP_info[0], localpath=ParseMID_File_Local_Path, remotepath=ParseMID_File_Remote_Path)
        pass
    Result = True
    emailContent = f'''
    Settlement  Date: {today}\n
    Transaction Date: {TransDatetime_8_digits}\n
    PID showQRCode Count: {PID_Txns_Total}\n
    PID showQRCode Fee: {float(PID_Fee_Total)/100}\n
    PID showQRCode Amount: {float(PID_Amount_Total)/100}\n
    Raw MID Count: {RawMID_Report[2].TotalofTransaction}\n
    Raw MID Fee: {float(RawMID_Report[2].TotalofFee)/100}\n
    Raw MID Amount: {float(RawMID_Report[2].TotalofAmount)/100}\n
    Final Report Count: {str(int(RawMID_Report[2].TotalofTransaction) + PID_Txns_Total)}\n
    Final Report Fee: {float(RawMID_Report[2].TotalofFee)/100 + float(PID_Fee_Total)/100}\n
    Final Report Amount: {float(RawMID_Report[2].TotalofAmount)/100 + float(PID_Amount_Total)/100}'''
    Email.sentEmail(Log_Name='CLP_Report', Email_subject=f'[{Result}]CLP_Report ({today}) - {MID}',
                    Email_content=emailContent, Email_attachement=[PID_File_Local_Path,ParseMID_File_Local_Path])
    log.end('CLP_Report')

if __name__ == '__main__':
    main()