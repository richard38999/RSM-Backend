import os
import csv
import sys
import datetime as datetime
import pysftp
import Logger
import Configuration
import decorator
import Email
log = Logger.Log('Maxims_VMP_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
Maxims_VMP_Report_Config = Configuration.get_Maxims_VMP_Report_Config()
today = ''
day_of_year = ''
Result = False
sftp = None
emailContent = ''
class VMP_RH:
    RecordIdentifier = None
    FileID = None
    FileDate = None
    MID = None
    MIDname = None

class VMP_RD:
    RecordIdentifier = None
    SettlementDate = None
    TerminalID = None
    BatchNumber = None
    TransactionDate = None
    TransactionTime = None
    Settlementno = None
    PaymentType = None
    Currency = None
    WalletVersion = None
    FXRate = None
    TransactionamountHKD = None
    TransactionamountRMB = None
    MDRFeeHKD = None
    MDR = None
    NetAmountHKD = None
    TraceNumber = None
    TransType = None
    RRN = None
    MerchantRRN = None
    Userconfirmkey = None

class VMP_RT:
    RecordIdentifier = None
    TotalofTrasaction = None
    TotalofAmount = None
    TotalofFee = None

RH = VMP_RH()
RT = VMP_RT()
RD = []
def getSftpFile(SFTP_info, remotepath=None, localpath=None):
    log.start('getSftpFile')
    log.info('start Connection')
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    sftp = pysftp.Connection(host=SFTP_info[0][0], port=SFTP_info[0][1], username=SFTP_info[0][2], password=SFTP_info[0][3], cnopts=cnopts)
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
    sftp = pysftp.Connection(host=SFTP_info[0][0], port=SFTP_info[0][1], username=SFTP_info[0][2], password=SFTP_info[0][3], cnopts=cnopts)
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
    sftp = pysftp.Connection(host=SFTP_info[0][0], port=SFTP_info[0][1], username=SFTP_info[0][2], password=SFTP_info[0][3], cnopts=cnopts)
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

def readCSV(path):
    log.start('readCSV')
    f = open(path, 'r')
    rows = csv.reader(f, delimiter=',')
    for row in rows:
        log.info(row)
        if row[0][1:] == 'RH':
            RH.RecordIdentifier = row[0][1:]
            RH.FileID = row[1][1:]
            RH.FileDate = row[2][1:]
            RH.MID = row[3][1:]
            RH.MIDname = row[4][1:]
        elif row[0][1:] == 'RD':
            rd = VMP_RD()
            rd.RecordIdentifier = row[0][1:]
            rd.SettlementDate = row[1][1:]
            rd.TerminalID = row[2][1:]
            rd.BatchNumber = row[3][1:]
            rd.TransactionDate = row[4][1:]
            rd.TransactionTime = row[5][1:]
            rd.Settlementno = row[6][1:]
            rd.PaymentType = row[7][1:]
            rd.Currency = row[8][1:]
            rd.WalletVersion = row[9][1:]
            rd.FXRate = row[10][1:]
            rd.TransactionamountHKD = row[11][1:]
            rd.TransactionamountRMB = row[12][1:]
            rd.MDRFeeHKD = row[13][1:]
            rd.MDR = row[14][1:]
            rd.NetAmountHKD = row[15][1:]
            rd.TraceNumber = row[16][1:]
            rd.TransType = row[17][1:]
            rd.RRN = row[18][1:]
            rd.MerchantRRN = row[19][1:]
            rd.Userconfirmkey = row[20][1:]
            RD.append(rd)
        elif row[0][1:] == 'RT':
            RT.RecordIdentifier = row[0][1:]
            RT.TotalofTrasaction = row[1][1:]
            RT.TotalofAmount = row[2][1:]
            RT.TotalofFee = row[3][1:]
    log.end('readCSV')
    return True
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
    if RH.MID == '852000058140017':
        RH.MIDname = 'New Concepts Chinese Rest'
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
@decorator.except_output('Maxims_VMP_Report', isSendEmail=True, Email_subject='Maxims_VMP_Report Error Alert!')
def main():
    log.start('Maxims_VMP_Report')
    log.info(str(sys.argv))
    global today
    global day_of_year
    global Result
    global sftp
    global emailContent
    global RH
    global RT
    global RD
    if len(sys.argv) == 2:
        today = sys.argv[1]
    else:
        today = datetime.datetime.now().strftime("%Y%m%d")
        # today = '20211030'
    for MID in Maxims_VMP_Report_Config:
        # MID = '852000058140011'
        MID = MID[0]

        RH = VMP_RH()
        RT = VMP_RT()
        RD = []
        Result = False
        log.info(f'MID: {MID}')
        day_of_year = str(datetime.date(int(today[:4]), int(today[4:6]), int(today[6:])).timetuple().tm_yday).zfill(3)
        TransDatetime_6_digits = (datetime.datetime.strptime(today,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%y%m%d")
        log.info(f'TransDatetime_6_digits: {TransDatetime_6_digits}')
        TransDatetime_8_digits = (datetime.datetime.strptime(today,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%Y%m%d")
        log.info(f'TransDatetime_8_digits: {TransDatetime_8_digits}')
        currentlyPath = os.getcwd()
        VMP_File_Remote_Path = '/home/eft/vmpfile/{0}/{1}_{2}.csv'.format(TransDatetime_8_digits, MID, TransDatetime_8_digits)
        log.info(f'VMP_File_Remote_Path: {VMP_File_Remote_Path}')
        VMP_File_Local_Path = currentlyPath + '\\Settlement_Report\\Maxims_VMP_Report\\VMP_Report\\{0}_{1}.csv'.format(MID, TransDatetime_8_digits)
        log.info(f'VMP_File_Local_Path: {VMP_File_Local_Path}')
        EOPG_File_Remote_Path = f'/home/{MID}/eopgfile/VMP_{MID}.{TransDatetime_6_digits}'
        log.info(f'EOPG_File_Remote_Path: {EOPG_File_Remote_Path}')
        EOPG_File_Local_Path = currentlyPath + '\\Settlement_Report\\Maxims_VMP_Report\\EOPG_Report\\{0}'.format(
            'VMP_' + MID + '.' + TransDatetime_6_digits)
        log.info(f'EOPG_File_Local_Path: {EOPG_File_Local_Path}')
        EOPG_File_Remote_folder = f'/home/{MID}/eopgfile'
        log.info(f'EOPG_File_Remote_folder: {EOPG_File_Remote_folder}')
        if not checkSftpFile(SFTP_info, remotepath=VMP_File_Remote_Path):
            emailContent = f'remotepath Not Exist: {VMP_File_Remote_Path}'
            log.info(emailContent)
            Result = False
            Email.sentEmail(Log_Name='Maxims_VMP_Report', Email_subject=f'[{Result}]Maxims_VMP_Report ({today}) - {MID}', Email_content=emailContent)
            log.end('Maxims_VMP_Report')
            continue
        getSftpFile(SFTP_info,
                    localpath=currentlyPath + '\\Settlement_Report\\Maxims_VMP_Report\\VMP_Report\\{0}_{1}.csv'.format(MID,TransDatetime_8_digits),
                    remotepath=VMP_File_Remote_Path)
        if readCSV(VMP_File_Local_Path):
            result = convertDataToEopgFormat()
            if result[0] == True:
                writeEOPGFile(path=EOPG_File_Local_Path, data=result[1])
                log.info('write EOPG file in local success')
        if not checkSftpFile(SFTP_info,remotepath=EOPG_File_Remote_folder):
            emailContent = f'Remote Folder Not Exist: {EOPG_File_Remote_folder}'
            log.info(emailContent)
            Result = False
            Email.sentEmail(Log_Name='Maxims_VMP_Report',
                            Email_subject=f'[{Result}]Maxims_VMP_Report ({today}) - {MID}', Email_content=emailContent)
            log.end('Maxims_VMP_Report')
            continue
        putSftpFile(SFTP_info, localpath=EOPG_File_Local_Path, remotepath=EOPG_File_Remote_Path)
        Result = True
        emailContent = f'''
        Settlement  Date: {today}\n
        Transaction Date: {TransDatetime_8_digits}\n
        Total Transaction: {RT.TotalofTrasaction}\n
        Total Fee: {RT.TotalofFee}\n
        Total Amount: {RT.TotalofAmount}'''
        Email.sentEmail(Log_Name='Maxims_VMP_Report', Email_subject=f'[{Result}]Maxims_VMP_Report ({today}) - {MID}',
                        Email_content=emailContent, Email_attachement=[VMP_File_Local_Path, EOPG_File_Local_Path])
    log.end('Maxims_VMP_Report')

if __name__ == '__main__':
    main()