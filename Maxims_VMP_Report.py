import os
import csv
import datetime as datetime
import pysftp
import Logger
import Configuration

log = Logger.Log('Maxims_VMP_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()

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

sftp = None
def getSftpFile(SFTP_info, remotepath=None, localpath=None):
    try:
        log.start('getSftpFile')
        log.debug('start Connection')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(host=SFTP_info[0][0], port=SFTP_info[0][1], username=SFTP_info[0][2], password=SFTP_info[0][3], cnopts=cnopts)
        log.debug('end Connection')
        log.debug('start get file, localpath: {0}'.format(localpath))
        log.debug('start get file, remotepath: {0}'.format(remotepath))
        sftp.get(remotepath, localpath=localpath)
        log.debug('end get file')
        log.debug('start SFTP close')
        sftp.close()
        log.debug('end SFTP close')
        log.end('getSftpFile')
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('getSftpFile')

def putSftpFile(SFTP_info, localpath=None, remotepath=None):
    try:
        log.start('putSftpFile')
        log.debug('start Connection')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(host=SFTP_info[0][0], port=SFTP_info[0][1], username=SFTP_info[0][2], password=SFTP_info[0][3], cnopts=cnopts)
        log.debug('end Connection')
        log.debug('start put file, localpath: {0}'.format(localpath))
        log.debug('start put file, remotepath: {0}'.format(remotepath))
        sftp.put(localpath, remotepath=remotepath)
        log.debug('end put file')
        log.debug('start SFTP close')
        sftp.close()
        log.debug('end SFTP close')
        log.end('putSftpFile')
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('putSftpFile')
RH = VMP_RH()
RT = VMP_RT()
RD = []
def readCSV(path):
    try:
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
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('readCSV')
        return False

def writeEOPGFile(path, data):
    try:
        log.start('writeEOPGFile')
        log.info('path: {0}'.format(path))
        log.info('data: {0}'.format(data))
        f = open(path, "w")
        f.write(data)
        f.close()
        return True
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('writeEOPGFile')
        return False


def convertDataToEopgFormat():
    try:
        returnData = ''
        log.start('convertDataToEopgFormat')
        # RH: Record Identifier, 2, (RH)
        returnData += RH.RecordIdentifier
        # RH: File ID, 8, (Year+’N’+day of year, in YYYYXddd format. Example: 2013-2-1 = 2013N032)

        # RH: File Date, 8, (In CCYYMMDD format. It should be the current processing date.)

        # RH: Rate of fee, 5, (With 2 decimal points)

        # RH: MID, 15
        returnData += RH.MID.rjust(15, ' ')
        # RH: MID name, 30
        returnData += RH.MIDname.rjust(30, ' ')
        # RH: PID, 28
        returnData += '2088031839616494'.rjust(28,' ')
        # RH: Filler, 156
        returnData += ' ' * 156
        for rd in RD:
            # RD: Record Identifier, 2, (RD)
            returnData += rd.RecordIdentifier
            # RD: Settlement Date, 10, (In CCYY/MM/DD format)
            returnData += rd.SettlementDate
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
            returnData += rd.Currency
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
            returnData += rd.RRN.rjust(64,' ')
            # RD: Store ID, 8, (Space if no information or non-numeric value)
            returnData += ' '*8
            # RD: Wallet Currency, 3, (e.g. “HKD”,”RMB”)
            returnData += 'HKD'
            # RD: Transaction Entry mode, 1, (1- Spot Barcode Payment 2- QRCode Payment 3- Online Payment 4- Apps Payment)
            returnData += '3'
            # RD: Filler, 2, (Filled with spaces)
            returnData += ' '*2

        # RT: Record Identifier, 2, (RT)
        returnData += RT.RecordIdentifier
        # RT: Total of Transaction, 9,
        returnData += str(int(round(float(RT.TotalofTrasaction) * 100, 2))).zfill(9)
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
        pass
        return True
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('convertDataToEopgFormat')
        return False

if __name__ == '__main__':
    try:
        log.start('Maxims_VMP_Report')
        MID = '852000058140011'
        Datetime = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%y%m%d")
        currentlyPath = os.getcwd()
        path = currentlyPath + '\\Settlement_Report\\Maxims_VMP_Report\\VMP_Report\\852000057220001_20201103.csv'
        # getSftpFile(SFTP_info,localpath=currentlyPath + '\\Settlement_Report\\Maxims_VMP_Report\\VMP_Report\\' + MID + '.' + Datetime, remotepath='/home/852000058140011/eopgfile/' + MID + '.' + Datetime)
        if readCSV(path):
            convertDataToEopgFormat()

        log.end('Maxims_VMP_Report')
    except Exception as ex:
        log.error('Error message: {0}'.format(ex))
        log.end('Maxims_VMP_Report')