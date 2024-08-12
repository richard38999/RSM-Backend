import base64
import datetime
import hashlib
import sqlite3
import time
import requests
import zipfile
import Configuration
# import Crypto
# from Crypto.PublicKey import RSA
# from Crypto.Hash import SHA, SHA256
# from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature, PKCS1_v1_5
db_name = Configuration.DB_path

def getResultMessage(iRet):
    if iRet == '0':
        return 'Success'
    if iRet == '-1':
        return 'Other operation in progress.'
    if iRet == '-2':
        return 'Invalid amount'
    if iRet == '-3':
        return 'Invalid barcode'
    if iRet == '-4':
        return 'Invalid ECR reference number'
    if iRet == '-5':
        return 'No such record'
    if iRet == '-6':
        return 'No such transaction request'
    if iRet == '-7':
        return 'Waiting for response'
    if iRet == '-8':
        return 'Invalid TID'
    if iRet == '-9':
        return 'Invalid MID'
    if iRet == '-10':
        return 'Invalid Trace'
    if iRet == '-11':
        return 'Reversal Pending'
    if iRet == '-12':
        return 'Connection problem'
    if iRet == '-13':
        return 'Transaction already voided'
    if iRet == '-14':
        return 'Transaction Timeout or Communication Error'
    if iRet == '-15':
        return 'UPLOAD_REJECT'
    if iRet == '-16':
        return 'Invalid RRN'
    if iRet == '-17':
        return 'Invalid Approval Code'
    if iRet == '-90':
        return 'OP_NOT_SUPPORT'
    if iRet == '-98':
        return 'Unknown error'


def getTransactionRecord(tr):
    returndata = {'paymentType': tr.paymentType,
                  'transType': tr.transType,
                  'merchantID': tr.merchantID,
                  'terminalID': tr.terminalID,
                  'respondCode': tr.respondCode,
                  'approvalCode': tr.approvalCode,
                  'ECRReferenceNumber': tr.ECRReferenceNumber,
                  'barcode': tr.barcode,
                  'amount': tr.amount,
                  'transactionDateTime': tr.transactionDateTime,
                  'cutOffDay': tr.cutOffDay,
                  'traceNum': tr.traceNum,
                  'debitInCurrency': tr.debitInCurrency,
                  'debitInAmount': tr.debitInAmount,
                  'OrderNumber': tr.OrderNumber,
                  'hostMessage': tr.hostMessage,
                  'voided': tr.voided,
                  'originalTraceNum': tr.originalTraceNum,
                  'originalOrderNumber': tr.originalOrderNumber,
                  'RRN': tr.RRN,
                  'hostDateTime': tr.hostDateTime,
                  'discountAmount': tr.discountAmount,
                  'couponAmount': tr.couponAmount,
                  'paymentAmount': tr.paymentAmount,
                  'oriTID': tr.oriTID,
                  'buyerAccountID': tr.buyerAccountID,
                  'LogoUrl': tr.LogoUrl,
                  'open_id': tr.open_id,
                  'respondText': tr.respondText}
    return returndata


def getXmlResp(tr, RawRequest, RawResponse):
    returndata = {'merchantID': tr.MID,
                  'terminalID': tr.TID,
                  'RRN': tr.RefNo,
                  # 'TransType': tr.TransType,
                  'hostDateTime': tr.TransDate + tr.TransTime,
                  'ECRReferenceNumber': tr.ERCRFN,
                  'open_id': tr.PayID,
                  'couponAmount': tr.CouponAMT,
                  'paymentAmount': tr.NetAMT,
                  'discountAmount': tr.OffsetAMT,
                  'originalOrderNumber': tr.Status,
                  'TotalSaleAMT': tr.TotalSaleAMT,
                  'TotalSaleCNT': tr.TotalSaleCNT,
                  'TotalRefundAMT': tr.TotalRefundAMT,
                  'TotalRefundCNT': tr.TotalRefundCNT,
                  'originalTraceNum': tr.OrgTraceNo,
                  'traceNum': tr.TraceNo,
                  'Rate': tr.Rate,
                  'LogoUrl': tr.LogoUrl,
                  'respondText': tr.respondText,
                  'RawRequest': RawRequest,
                  'RawResponse': RawResponse
                  }
    returndata['amount'] = None
    if tr.Amount != None:
        returndata['amount'] = tr.Amount
    if tr.TransactionAmount != None:
        returndata['amount'] = tr.TransactionAmount
    returndata['respondCode'] = None
    if tr.RespCode != None:
        returndata['respondCode'] = tr.RespCode
    returndata['TransactionRespondCode'] = None
    if tr.TransactionRespondCode != None:
        returndata['TransactionRespondCode'] = tr.TransactionRespondCode

    returndata['barcode'] = None
    if tr.CardNo != None:
        returndata['barcode'] = tr.CardNo
    if tr.PAN != None:
        returndata['barcode'] = tr.PAN
    returndata['approvalCode'] = None
    if tr.ApproCode != None:
        returndata['approvalCode'] = tr.ApproCode
    if tr.ApprovedNo != None:
        returndata['approvalCode'] = tr.ApprovedNo
    if tr.TransID != None:
        returndata['OrderNumber'] = tr.TransID
    if tr.VoucherNo != None:
        returndata['OrderNumber'] = tr.VoucherNo

    return returndata


def get_login_account():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM users;')
    values = cursor.fetchall()
    cursor.close()
    conn.close()
    return values


def userView(username):
    returnmessage = []
    data = []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    command = 'select * from users where username = "{0}";'.format(username)
    cursor.execute(command)
    id = cursor.fetchall()[0][0]  # for get user ID
    command = 'select * from users_role where user_id = {0};'.format(id)
    cursor.execute(command)
    temp = cursor.fetchall()
    chooseKey = []
    for i in temp:
        chooseKey.append(i[1])
    command = 'select * from Menus where level = 1;'
    cursor.execute(command)
    LevelONEvalues = cursor.fetchall()  # menus level one values
    command = 'select * from Menus where level = 2;'
    cursor.execute(command)
    LevelTWOvalues = cursor.fetchall()  # menus level two values
    command = 'select * from Menus where level = 3;'
    cursor.execute(command)
    LevelTHREEvalues = {}
    if len(cursor.fetchall()) > 0:
        LevelTHREEvalues = cursor.fetchall()  # menus level three values
    for i in LevelONEvalues:
        twomessage = []
        for j in LevelTWOvalues:
            threemessage = []
            if j[4] == None:  # parent id 有就代表是二级菜单
                continue
            elif j[4] != i[0]:  # parent id 不等于 level one 的 id
                continue
            else:  # parent id 等于 level one 的 id
                for k in LevelTHREEvalues:
                    if k[4] == None:
                        continue
                    elif k[4] != j[0]:
                        continue
                    else:
                        threemessage.append(
                            {'id': k[0], 'authName': k[1], 'path': k[2], 'level': k[3], 'parent_id': k[4], 'icon': k[6],
                             'children': []})
            twomessage.append(
                {'id': j[0], 'authName': j[1], 'path': j[2], 'level': j[3], 'parent_id': j[4], 'icon': j[6],
                 'children': threemessage})
        data.append({'id': i[0], 'authName': i[1], 'path': i[2], 'level': i[3], 'parent_id': i[4], 'icon': i[6],
                     'children': twomessage})
    returnmessage = {'chooseKey': chooseKey, 'data': data}
    cursor.close()
    conn.close()
    return returnmessage


def get_Menu(username):
    returnmessage = []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    command = 'select * from users where username = "{0}";'.format(username)
    cursor.execute(command)
    id = cursor.fetchall()[0][0]  # for get user ID
    command = 'select DISTINCT * from users_role ur LEFT JOIN Menus p on ur.role_id where ur.user_id = "{0}" and ur.role_id = p.id and p.level = 1 order by sort;'.format(
        id)
    cursor.execute(command)
    LevelONEvalues = cursor.fetchall()  # menus level one values
    command = 'select DISTINCT * from users_role ur LEFT JOIN Menus p on ur.role_id where ur.user_id = "{0}" and ur.role_id = p.id and p.level = 2;'.format(
        id)
    cursor.execute(command)
    LevelTWOvalues = cursor.fetchall()  # menus level two values
    command = 'select DISTINCT * from users_role ur LEFT JOIN Menus p on ur.role_id where ur.user_id = "{0}" and ur.role_id = p.id and p.level = 3;'.format(
        id)
    cursor.execute(command)
    LevelTHREEvalues = {}
    if len(cursor.fetchall()) > 0:
        LevelTHREEvalues = cursor.fetchall()  # menus level three values
    for i in LevelONEvalues:
        twomessage = []
        for j in LevelTWOvalues:
            threemessage = []
            if j[6] == None:  # parent id 有就代表是二级菜单
                continue
            elif j[6] != i[2]:  # parent id 不等于 level one 的 id
                continue
            else:  # parent id 等于 level one 的 id
                for k in LevelTHREEvalues:
                    if k[6] == None:
                        continue
                    elif k[6] != j[2]:
                        continue
                    else:
                        threemessage.append(
                            {'id': k[2], 'authName': k[3], 'path': k[4], 'level': k[5], 'parent_id': k[6], 'icon': k[8],
                             'children': []})
            twomessage.append(
                {'id': j[2], 'authName': j[3], 'path': j[4], 'level': j[5], 'parent_id': j[6], 'icon': j[8],
                 'children': threemessage})
        returnmessage.append(
            {'id': i[2], 'authName': i[3], 'path': i[4], 'level': i[5], 'parent_id': i[6], 'icon': i[8],
             'children': twomessage})

    cursor.close()
    conn.close()
    return returnmessage


def get_userlist(pagenum, pagesize):
    returnmessage = []
    userlist = []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('select * FROM users;')
    values = cursor.fetchall()
    cursor.close()
    conn.close()
    for i in range((pagenum - 1) * pagesize, pagenum * pagesize):
        if (i >= len(values)):
            break
        if (values[i][4] == 1):
            status = True
        else:
            status = False
        userlist.append({
            'username': values[i][1],
            'roles': values[i][3],
            'status': status,
            'createdatetime': values[i][5],
            'lastlogindatetime': values[i][6]
        })

    returnmessage = {'userlist': userlist, 'total': len(values)}
    return returnmessage


def update_lastlogindatetime(nowdatetime, username):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('update users set lastlogindatetime="{0}" where username="{1}";'.format(nowdatetime, username))
    conn.commit()
    cursor.close()
    conn.close()


def update_AccountStatus(username, status):
    try:
        if (status == 'true'):
            vaule = 1
        else:
            vaule = 0
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('update users set status={0} where username="{1}";'.format(vaule, username))
        conn.commit()
        cursor.close()
        conn.close()
        returnmessage = {'UpdateResult': True}
        return returnmessage
    except Exception as err:
        print(err)
        returnmessage = {'UpdateResult': False}
        return returnmessage


def delete_Account(username):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE from users where username="{0}"'.format(username))
        conn.commit()
        cursor.close()
        conn.close()
        returnmessage = {'DeleteResult': True}
        return returnmessage
    except Exception as err:
        print(err)
        returnmessage = {'DeleteResult': False}
        return returnmessage


def convertToCardNo(maskedCardNo):
    returnmessage = ''
    for i in maskedCardNo:
        if i == 'a' or i == 'b' or i == 'c' or i == 'd' or i == 'e':
            returnmessage += '0'
        elif i == 'f' or i == 'g' or i == 'h' or i == 'i' or i == 'j':
            returnmessage += '1'
        elif i == 'k' or i == 'l' or i == 'm' or i == 'n' or i == 'o':
            returnmessage += '2'
        elif i == 'p' or i == 'q' or i == 'r' or i == 's' or i == 't':
            returnmessage += '3'
        elif i == 'u' or i == 'v' or i == 'w' or i == 'x' or i == 'y':
            returnmessage += '4'
        elif i == 'z' or i == 'A' or i == 'B' or i == 'C' or i == 'D':
            returnmessage += '5'
        elif i == 'E' or i == 'F' or i == 'G' or i == 'H' or i == 'I':
            returnmessage += '6'
        elif i == 'J' or i == 'K' or i == 'L' or i == 'M' or i == 'N':
            returnmessage += '7'
        elif i == 'O' or i == 'P' or i == 'Q' or i == 'R' or i == 'S':
            returnmessage += '8'
        elif i == 'T' or i == 'U' or i == 'V' or i == 'W' or i == 'X':
            returnmessage += '9'
    return returnmessage


def ChangePassword(username, oldPassword, newPassword):
    try:
        returnmessage = ''
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('select * FROM users where username="{0}";'.format(username))
        vaules = cursor.fetchall()[0][2]
        if oldPassword == vaules:
            #     password match, update password
            cursor.execute('update users set password="{0}" where username="{1}";'.format(newPassword, username))
            conn.commit()
            returnmessage = {'status': 'Success', 'msg': 'Change Password Success'}
        else:
            # Password Not match
            returnmessage = {'status': 'Failed', 'msg': 'Password Not Match'}
        cursor.close()
        conn.close()
        return returnmessage
    except Exception as err:
        print(err)
        returnmessage = {'status': 'Failed', 'msg': "{0}".format(err)}
        return returnmessage


def PostToHost(url, data, timeout):
    try:
        req = requests.post(url, data=data, timeout=timeout)
    except Exception as err:
        print(err)
    finally:
        return req


def GetToHost(url, timeout):
    try:
        req = requests.get(url, timeout=timeout)
    except Exception as err:
        print(err)
    finally:
        return req

def setconfig_Spiral(username='',
                      Tag='',
                      clientId='',
                      merchantRef='',
                      cmd='',
                      amount='',
                      type='',
                      goodsName='',
                      Flow='',
                      orderId='',
                      URL='',
                      goodsDesc='',
                      channel='',
                      cardToken='',
                      cardTokenSrc='',
                      successUrl='',
                      failureUrl='',
                      webhookUrl='',
                      duration='',
                      durationHr='',
                      privateKey='',
                      publicKey='',
                      JavaScriptLibrary='',
                      locale=''
                      ):
    returnmessage = {}
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        f'select * FROM Spiral_Config where username="{username}" and Tag="{Tag}";')
    values = cursor.fetchall()
    if values != []:
        cursor.close()
        conn.close()
        return {'status': 1, 'msg': 'Tag Already exist! Please change the Tag.'}
    cmd = f'INSERT INTO Spiral_Config VALUES ("{username}", "{Tag}", "{clientId}", "{merchantRef}", "{cmd}", "{Flow}", "{type}", "{amount}", "{goodsName}", "{goodsDesc}", "{channel}", "{cardToken}", "{cardTokenSrc}", "{successUrl}", "{failureUrl}", "{webhookUrl}", "{duration}", "{durationHr}", "{orderId}", "{privateKey}", "{publicKey}", "{URL}", "{JavaScriptLibrary}", "{locale}");'
    cursor.execute(cmd)
    conn.commit()
    cursor.close()
    conn.close()
    return {'status': 0, 'msg': 'Set Config Success'}

def setconfig_Offline(username='',
                      Gateway_Name='',
                      Tag='',
                      MID='',
                      TID='',
                      TransactionType='',
                      PaymentType='',
                      barcode='',
                      amount='',
                      ecrRefNo='',
                      ApprovalCode='',
                      RRN='',
                      IP='',
                      Port='',
                      TPDU='',
                      COMMTYPE='',
                      Timeout='',
                      MsgType='',
                      TraceNo='',
                      URL='',
                      PayType='',
                      OrdDesc='',
                      Products='',
                      AUTH='',
                      shopcarts='',
                      OriTID=''
                      ):
    returnmessage = {}
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        f'select * FROM Offline_Txn_Config where username="{username}" and Gateway_Name="{Gateway_Name}" and Tag="{Tag}";')
    values = cursor.fetchall()
    if values != []:
        cursor.close()
        conn.close()
        return {'status': 1, 'msg': 'Tag Already exist! Please change the Tag.'}
    cmd = f'INSERT INTO Offline_Txn_Config VALUES ("{username}", "{Gateway_Name}", "{Tag}", "{MID}", "{TID}", "{TransactionType}", "{PaymentType}", "{amount}", "{barcode}", "{ApprovalCode}", "{RRN}", "{TraceNo}", "{OriTID}", "{URL}", "{IP}", "{Port}", "{TPDU}", "{Timeout}", "{MsgType}", "{COMMTYPE}", "{OrdDesc}", "{Products}");'
    cursor.execute(cmd)
    conn.commit()
    cursor.close()
    conn.close()
    return {'status': 0, 'msg': 'Set Config Success'}


def setconfig_VMP(username='', Gateway_Name='', Tag='', APIType='', User_Confirm_Key='', SecretCode='', Amount='', Service='', out_trade_no='', TransactionType='',
                  PaymentType='', eft_trade_no='', refund_no='', Wallet='',
                   buyerType='', subject='', body='', fee_type='', tid='',
                  scene_type='', openid='', sub_openid='', wechatWeb='', active_time='', URL='', notify_url='',
                  return_url='', app_pay='', lang='', goods_body='', goods_subject='',
                  reuse='', redirect='', refund_reason='', reason='', mobileNumber='',
                  fullName='', shippingAddress_countryCode='', shippingAddress_postCode='', shippingAddress_lines='',
                  billingAddress_countryCode='', billingAddress_postCode='', billingAddress_lines='',
                  app_link='', browser='', pay_scene=''):
    returnmessage = {}
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        f'select * FROM VMP_Config where username="{username}" and Gateway_Name="{Gateway_Name}" and Tag="{Tag}";')
    values = cursor.fetchall()
    if values != []:
        cursor.close()
        conn.close()
        return {'status': 1, 'msg': 'Tag Already exist! Please change the Tag.'}
    cmd = f'INSERT INTO VMP_Config VALUES ("{username}", "{Gateway_Name}", "{Tag}", "{APIType}", "{User_Confirm_Key}", ' \
          f'"{SecretCode}", "{Amount}", "{Service}", "{out_trade_no}", "{TransactionType}", ' \
          f'"{PaymentType}", "{eft_trade_no}", "{refund_no}", "{Wallet}", "{buyerType}", ' \
          f'"{subject}", "{body}", "{fee_type}", "{tid}", "{scene_type}", ' \
          f'"{openid}", "{sub_openid}","{wechatWeb}", "{active_time}", "{URL}", "{notify_url}","{return_url}",' \
          f'"{app_pay}", "{lang}","{goods_body}", "{goods_subject}","{reuse}",' \
          f'"{redirect}", "{refund_reason}","{reason}", "{mobileNumber}","{fullName}",' \
          f'"{shippingAddress_countryCode}", "{shippingAddress_postCode}","{shippingAddress_lines}", "{billingAddress_countryCode}","{billingAddress_postCode}",'\
          f'"{billingAddress_lines}", "{app_link}", "{browser}", "{pay_scene}");'
    print(cmd)
    cursor.execute(cmd)
    conn.commit()
    cursor.close()
    conn.close()
    return {'status': 0, 'msg': 'Set Config Success'}

def loadconfig(username=None, Gateway_Name=None):
    returnmessage = []
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if Gateway_Name == 'VMP' or Gateway_Name == 'BOCVMP':
        cmd = f'select * FROM VMP_Config where username="{username}" and Gateway_Name="{Gateway_Name}";'
    elif Gateway_Name == 'Spiral':
        cmd = f'select * FROM Spiral_Config where username="{username}";'
    else:
        cmd = f'select * FROM Offline_Txn_Config where username="{username}" and Gateway_Name="{Gateway_Name}";'
    cursor.execute(cmd)
    values = cursor.fetchall()
    # print(values)
    cursor.close()
    conn.close()
    desc = list(zip(*cursor.description))[0]  # To get column names
    for row in values:
        rowdict = dict(zip(desc, row))
        returnmessage.append(rowdict)
    return returnmessage


def deleteconfig(username='', Gateway_Name='', Tag=''):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        if Gateway_Name == 'VMP' or Gateway_Name == 'BOCVMP':
            cursor.execute(
                f'DELETE from VMP_Config where username="{username}" and Gateway_Name="{Gateway_Name}" and Tag="{Tag}";')
        elif Gateway_Name == 'Spiral':
            cursor.execute(
                f'DELETE from Spiral_Config where username="{username}" and Tag="{Tag}";')
        else:
            cursor.execute(
                f'DELETE from Offline_Txn_Config where username="{username}" and Gateway_Name="{Gateway_Name}" and Tag="{Tag}";')
        conn.commit()
        cursor.close()
        conn.close()
        returnmessage = {'status': 0, 'msg': 'DELETE Config Success'}
        return returnmessage
    except Exception as err:
        returnmessage = {'status': 1, 'msg': err}
        return returnmessage

def SQL_script(script):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(script)
    returnmData = cursor.fetchall()
    # print(values)
    conn.commit()
    cursor.close()
    conn.close()
    return returnmData

def insert_Offline_Txn(DateTime='', username='', GatewayName='', MID='', TID='',  TransactionType='', Amount='', RRN='', approvalCode='', respondCode='', respondText='',Email_Subject='', Remark='', Requested_by='', Approved_by='', Requested_time='', Approved_time='', Approved_status='', BatchNo=''):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cmd = f'insert INTO Offline_Txn_DB VALUES("{DateTime}", "{username}", "{GatewayName}", "{MID}", "{TID}", "{TransactionType}", "{Amount}", "{RRN}", "{approvalCode}", "{respondCode}", "{respondText}", "{Email_Subject}", "{Remark}", "{Requested_by}", "{Approved_by}", "{Requested_time}", "{Approved_time}", "{Approved_status}", "{BatchNo}");'
    cursor.execute(cmd)
    # returnmData = cursor.fetchall()
    # print(values)
    conn.commit()
    cursor.close()
    conn.close()

def insert_VMP_Txn(DateTime='', username='', GatewayName='', API_Type='', PaymentType='',  TransType='', Amount='', user_confirm_key='', Secret_Code='', out_trade_no='', eft_trade_no='',Response_Code='', Response_Text='', Email_Subject='', Remark=''):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cmd = f'insert INTO VMP_Txn_DB VALUES("{DateTime}", "{username}", "{GatewayName}", "{API_Type}", "{PaymentType}", "{TransType}", "{user_confirm_key}", "{Secret_Code}", "{Amount}", "{out_trade_no}", "{eft_trade_no}", "{Response_Code}", "{Response_Text}", "{Email_Subject}", "{Remark}");'
    cursor.execute(cmd)
    # returnmData = cursor.fetchall()
    # print(values)
    conn.commit()
    cursor.close()
    conn.close()

def check_offline_refund_txn(GateName='', MID='', TID='', RRN='', check_ResponseCode=True):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    if check_ResponseCode:
        cmd = f'select * from Offline_Txn_DB where Gateway_Name = "{GateName}" and MID = "{MID}" and TID = "{TID}" and RRN = "{RRN}" and Response_Code = "00" and (TransType = "REFUND" or TransType = "ADMINREFUND");'
    else:
        cmd = f'select * from Offline_Txn_DB where Gateway_Name = "{GateName}" and MID = "{MID}" and TID = "{TID}" and RRN = "{RRN}" and (TransType = "REFUND" or TransType = "ADMINREFUND");'
    cursor.execute(cmd)
    returnmData = cursor.fetchall()
    # print(values)
    conn.commit()
    cursor.close()
    conn.close()
    return returnmData

def check_vmp_refund_txn(GateName='', user_confirm_key='', out_trade_no='', eft_trade_no=''):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cmd = ''
    if out_trade_no != '' and eft_trade_no != '':
        cmd = f'select * from VMP_Txn_DB where Gateway_Name = "{GateName}" and user_confirm_key = "{user_confirm_key}" and Response_Code = "00" and TransType = "REFUND" and out_trade_no = "{out_trade_no}" and eft_trade_no = "{eft_trade_no}";'
    elif out_trade_no != '' and eft_trade_no == '':
        cmd = f'select * from VMP_Txn_DB where Gateway_Name = "{GateName}" and user_confirm_key = "{user_confirm_key}" and Response_Code = "00" and TransType = "REFUND" and out_trade_no = "{out_trade_no}";'
    elif out_trade_no == '' and eft_trade_no != '':
        cmd = f'select * from VMP_Txn_DB where Gateway_Name = "{GateName}" and user_confirm_key = "{user_confirm_key}" and Response_Code = "00" and TransType = "REFUND" and eft_trade_no = "{eft_trade_no}";'
    elif out_trade_no == '' and eft_trade_no == '':
        cmd = f'select * from VMP_Txn_DB where Gateway_Name = "{GateName}" and user_confirm_key = "{user_confirm_key}" and Response_Code = "00" and TransType = "REFUND" and out_trade_no = "{out_trade_no}" and eft_trade_no = "{eft_trade_no}";'
    cursor.execute(cmd)
    returnmData = cursor.fetchall()
    # print(values)
    conn.commit()
    cursor.close()
    conn.close()
    return returnmData

def local_to_utc():
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    time_struct = time.mktime(local_time.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st.strftime('%Y-%m-%dT%H:%M:%SZ')

def rsa_encrypt_data(data='', Key_path=''):
    private_key = get_key(Key_path)
    # 对拼接后的字符串进行SHA-256签名
    signature = hashlib.sha256(data.encode()).hexdigest()
    # print("***********sha256_signature:")
    # print(signature)
    # signature = rsa_sign(data.encode(encoding='utf-8'), private_key)
    # signature = base64.b64encode(signature)
    # signature = signature.decode("UTF-8")
    return signature

# def rsa_sign(plaintext, key, hash_algorithm=Crypto.Hash.SHA256):
#     """RSA 数字签名"""
#     signer = PKCS1_v1_5.new(RSA.importKey(key))
#
#     #hash算法必须要pycrypto库里的hash算法，不能直接用系统hashlib库，pycrypto是封装的hashlib
#     hash_value = hash_algorithm.new(plaintext)
#     return signer.sign(hash_value)

def get_key(key_file):
    with open(key_file) as f:
        data = f.read()
        # key = RSA.importKey(data)
    return data

def packJsonMsg(obj):
    retuenStr = {}
    for name, value in vars(obj).items():
        if value != None and value != '':
        # if value != None:
            retuenStr[name] = value
            # retuenStr.append({name: value})
    return retuenStr

def unzip_file(file_path=None, extract_folder=None, password=None):
    result = False
    with zipfile.ZipFile(file_path) as file:
        # password you pass must be in the bytes you converted 'str' into 'bytes'
        if password != None:
            file.extractall(path=extract_folder, pwd=bytes(password, 'utf-8'))
        else:
            file.extractall(path=extract_folder, pwd=password)
        result = True
    return result