import csv
import decorator
from flask import Flask,send_from_directory, request, jsonify, send_file, json
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
import clr
from werkzeug.utils import secure_filename
import xlrd
import Utility
import Configuration
from Logger import *
import time
import datetime
import requests
import Octopus
import hashlib
import VMP
import Spiral
from zipfile import ZipFile
clr.FindAssembly('DLL\\EFTPaymentsServer.dll')
clr.AddReference('DLL\\EFTPaymentsServer')
clr.FindAssembly('DLL\\XML_InterFace.dll')
clr.AddReference('DLL\\XML_InterFace')
from EFTSolutions import *
from XML_InterFace import *
log = Log('Flask')
ENVIRONMENT = 'DEV'
# ENVIRONMENT = 'PROD'
app = Flask(__name__)
app.config.from_object(Configuration.Flask_Config[ENVIRONMENT])
Config = Configuration.Flask_Config.get(ENVIRONMENT)

# 設定 JWT 密鑰
jwt = JWTManager()
jwt.init_app(app)
now_date = time.strftime("%Y%m%d", time.localtime())
CORS(app)

@app.route("/login", methods=['POST'])
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def login():
    log.start('login')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    # request.form = request.form.to_dict()
    username = request.json.get("username")
    password = request.json.get("password")
    FrontEndVersion = request.json.get('version')
    meta = {'status': 'Failed', 'msg': 'username not exist'}
    data = {'username': username, 'password': password}
    login_account = Utility.get_login_account()
    if Config.FrontEndVersion == FrontEndVersion:
        for i in login_account:
            if i[1] == username:
                if i[2] == password:
                    if i[4] == 1:
                        access_token = jwt._create_access_token(identity=username, expires_delta=datetime.timedelta(minutes=60*12))
                        meta = {'status': 'SUCCESS', 'msg': 'LOGIN SUCCESS'}
                        data = {'username': username, 'password': password, 'token': access_token}
                        nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        Utility.update_lastlogindatetime(nowdatetime,username)
                    else:
                        meta = {'status': 'Failed', 'msg': 'Account Status was closed'}
                        data = {'username': username}
                else:
                    meta = {'status': 'Failed', 'msg': 'PASSWORD NOT MATCH'}
                    data = {'username': username}
                break
    else:
        meta = {'status': 'Failed', 'msg': 'Version Not Updated, please re-start browser'}
        data = {'username': username}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('login')
    return jsonify(returnmessage)

@app.route("/ChangePassword", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def ChangePassword():
    log.start('ChangePassword')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.json.get("username")
    oldpassword = request.json.get("oldpassword")
    newpassword = request.json.get("newpassword")
    meta = {'status': 'Failed', 'msg': 'Password Not Match'}
    data = {}
    meta = Utility.ChangePassword(username, oldpassword,newpassword)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('ChangePassword')
    return jsonify(returnmessage)

@app.route("/userView", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def userView():
    log.start('userView')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    viewUser = request.args.get("username")
    data = Utility.userView(viewUser)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('userView')
    return jsonify(returnmessage)

@app.route("/menus", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def menu():
    log.start('menu')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    menuUser = request.args.get("username")
    data = Utility.get_Menu(menuUser)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('menu')
    return jsonify(returnmessage)

@app.route("/userlist", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def userlist():
    log.start('userlist')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    pagenum = request.args.get('pagenum')
    pagesize = request.args.get('pagesize')
    data = Utility.get_userlist(int(pagenum), int(pagesize))
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('userlist')
    return jsonify(returnmessage)

@app.route("/updateuserstatus", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def updateuserstatus():
    log.start('updateuserstatus')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    updateUsername = request.args.get('username')
    status = request.args.get('status')
    data = Utility.update_AccountStatus(updateUsername, status)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('updateuserstatus')
    return jsonify(returnmessage)

@app.route("/deleteUser", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def deleteUser():
    log.start('deleteUser')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    deleteUsername = request.args.get('username')
    status = request.args.get('status')
    data = Utility.delete_Account(deleteUsername)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('deleteUser')
    return jsonify(returnmessage)

@app.route("/Spiral", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Spiral_Transaction():
    log.start('Spiral_Transaction')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    cmd = request.json.get('cmd')
    clientId = request.json.get('clientId')
    merchantRef = request.json.get('merchantRef')
    if merchantRef == '':
        merchantRef = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    amount = request.json.get('amount')
    if amount != '':
        amount = round(float(amount), 2)
    type = request.json.get('type')
    goodsName = request.json.get('goodsName')
    Flow = request.json.get('Flow')
    orderId = request.json.get('orderId')
    URL = request.json.get('URL')
    goodsDesc = request.json.get('goodsDesc')
    channel = request.json.get('channel')
    cardToken = request.json.get('cardToken')
    cardTokenSrc = request.json.get('cardTokenSrc')
    successUrl = request.json.get('successUrl')
    failureUrl = request.json.get('failureUrl')
    webhookUrl = request.json.get('webhookUrl')
    duration = request.json.get('duration')
    if duration != '':
        duration = int(round(float(duration), 2))
    durationHr = request.json.get('durationHr')
    if durationHr != '':
        durationHr = int(round(float(durationHr), 2))
    Email_Subject = request.json.get('Email_Subject')
    Remark = request.json.get('Remark')
    privateKey = request.json.get('privateKey')
    publicKey = request.json.get('publicKey')
    data = {}
    RawRequest = ''
    utcTime = Utility.local_to_utc()
    log.info(f'utcTime: {utcTime}')
    Payload = clientId + merchantRef + utcTime
    log.info(f'Payload: {Payload}')
    currentlyPath = os.getcwd()
    cert_path = f'{currentlyPath}\\cert\\Spiral\\{privateKey}'
    if not os.path.exists(cert_path):
        meta = {'status': -1, 'msg': 'Certificate Not Exist'}
        returnmessage = {'meta': meta, 'data': data}
        return jsonify(returnmessage)
    Signature = str(Utility.rsa_encrypt_data(data=Payload, Key_path=cert_path))
    headers = {
        'Spiral-Request-Datetime': utcTime,
        'Spiral-Client-Signature': Signature
    }
    method = 'put'
    Spiral_Request = Spiral.Request()
    if Flow == 'Payment Link':
        if cmd == 'QUERY':
            method = 'get'
            URL = URL + f'/merchants/{clientId}/paymentlink/{merchantRef}'
        else:
            Spiral_Request = Spiral.packRequest(clientId=clientId,
                                               merchantRef=merchantRef,
                                               amt=amount,
                                               goodsName=goodsName,
                                               goodsDesc=goodsDesc,
                                               webhookUrl=webhookUrl,
                                               durationHr=durationHr
                                               )
            URL = URL + f'/merchants/{clientId}/paymentlink/{merchantRef}'
    else: # Direct
        if cmd == 'SALE' or cmd == 'AUTH' or cmd == 'SALESESSION' or cmd == 'AUTHSESSION':
            Spiral_Request = Spiral.packRequest(clientId=clientId,
                                                merchantRef=merchantRef,
                                                cmd=cmd,
                                                type=type,
                                                amt=amount,
                                                goodsName=goodsName,
                                                goodsDesc=goodsDesc,
                                                channel=channel,
                                                cardToken=cardToken,
                                                cardTokenSrc=cardTokenSrc,
                                                successUrl=successUrl,
                                                failureUrl=failureUrl,
                                                webhookUrl=webhookUrl,
                                                duration=duration
                                                )
            URL = URL + f'/merchants/{clientId}/transactions/{merchantRef}'
        elif cmd == 'CAPTURE' or cmd == 'REFUND':
            Spiral_Request = Spiral.packRequest(clientId=clientId,
                                                merchantRef=merchantRef,
                                                cmd=cmd,
                                                orderId=orderId,
                                                amt=amount,
                                                webhookUrl=webhookUrl
                                                )
            URL = URL + f'/merchants/{clientId}/transactions/{merchantRef}'
        elif cmd == 'QUERY':
            method = 'get'
            URL = URL + f'/merchants/{clientId}/transactions/{merchantRef}'

    if cmd != 'QUERY':
        RawRequest = json.dumps(Spiral.packJsonMsg(Spiral_Request))
    log.info(f'Raw_Request: {RawRequest}')
    log.info(f'URL: {URL}')
    resp = requests.request(method=method, data=RawRequest,timeout=30,url=URL, headers=headers)
    log.info(f'resp.status_code: {resp.status_code}')
    log.info(f'resp.text: {resp.text}')
    if resp.status_code == 200:
        meta = {'status': resp.status_code, 'msg': 'Success'}
    else:
        meta = {'status': resp.status_code, 'msg': resp.text}
    if cmd != 'QUERY':
        data = {'RawReqURL': URL, 'RawRequest': json.loads(RawRequest), 'RawResponse': json.loads(resp.text.encode("utf8"))}
    else:
        data = {'RawReqURL': URL, 'RawRequest': RawRequest, 'RawResponse': json.loads(resp.text.encode("utf8"))}
    # data = {'RawReqURL': URL, 'RawRequest': json.loads(RawRequest), 'RawResponse': json.loads(resp.text.encode("utf8"))}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('Spiral_Transaction')
    return jsonify(returnmessage)

@app.route("/Spiral/Certificate/<action>", methods=['GET', 'POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Spiral_Certificate(action):
    log.start('Spiral_Certificate')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    certname = request.args.get('certname')
    clientId = request.args.get('clientId')
    meta = {}
    data = []
    if action == 'getCertificateList':
        currentlyPath = os.getcwd()
        certlist = os.listdir(f'{currentlyPath}\\cert\\Spiral')
        for cert in certlist:
            data.append({
                'certname': cert
            })
        data = {'certlist': data, 'total': len(certlist)}
        meta = {'status': 0, 'msg': 'SUCCESS'}
    elif action == 'getCertData':
        currentlyPath = os.getcwd()
        certPath = f'{currentlyPath}\\cert\\Spiral\\{certname}'
        with open(certPath) as certFile:
            data = certFile.read().splitlines()
        meta = {'status': 0, 'msg': 'SUCCESS'}
    elif action == 'delete':
        currentlyPath = os.getcwd()
        certPath = f'{currentlyPath}\\cert\\Spiral\\{certname}'
        os.remove(certPath)
        meta = {'status': 0, 'msg': 'SUCCESS'}
    elif action == 'UploadCertificate':
        currentlyPath = os.getcwd()
        certlist = os.listdir(f'{currentlyPath}\\cert\\Spiral')
        f = request.files['file']
        if secure_filename(f.filename) in certlist:
            meta = {'status': -1, 'msg': 'Certificate Already Exist'}
        else:
            filepath = f'{currentlyPath}\\cert\\Spiral\\{secure_filename(f.filename)}'
            f.save(filepath)
            meta = {'status': 0, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('Spiral_Certificate')
    return jsonify(returnmessage)

@app.route("/<Till_Number>/<TransactionType>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Transaction(Till_Number, TransactionType):
    log.start('Transaction')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    MID = request.json.get('MID')
    TID = request.json.get('TID')
    barcode = request.json.get('barcode')
    amount = request.json.get('amount')
    ecrRefNo = request.json.get('ecrRefNo')
    ApprovalCode = request.json.get('ApprovalCode')
    # TransactionType = request.json.get('TransactionType')
    RRN = request.json.get('RRN')
    IP = request.json.get('IP')
    Port = request.json.get('Port')
    TPDU = request.json.get('TPDU')
    COMMTYPE = request.json.get('COMMTYPE')
    if COMMTYPE == 'TLS':
        COMMTYPE = 2
    elif COMMTYPE == 'PlainText':
        COMMTYPE = 1
    Timeout = request.json.get('Timeout')
    MsgType = request.json.get('MsgType')
    TraceNo = request.json.get('TraceNo')
    URL = request.json.get('URL')
    OrdDesc = request.json.get('OrdDesc')
    PayType = request.json.get('PayType')
    NumOfProduct = request.json.get('NumOfProduct')
    AUTH = request.json.get('AUTH')
    shopcarts = request.json.get('AUTH')
    OriTID = request.json.get('OriTID')
    Email_Subject = request.json.get('Email_Subject')
    Remark = request.json.get('Remark')
    if str(TransactionType).upper() == 'REFUND' or str(TransactionType).upper() == 'ADMINREFUND':
        if Remark == '' or Remark == None:
            Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
    iRet = -1
    msg = ''
    meta = {}
    data = []
    RawRequest = ''
    RawResponse = ''
    errormessage = ''
    nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    confirm_Refund = request.json.get('confirm_Refund')
    # check refund record
    if confirm_Refund != 'Y':
        if TransactionType == 'REFUND' or TransactionType == 'ADMINREFUND':
            Refund_Result = Utility.check_offline_refund_txn(GateName=Till_Number, MID=MID, RRN=RRN)
            if Refund_Result != []:
                for i in range(len(Refund_Result)):
                    data.append({'ID': i, 'DateTime': Refund_Result[i][0], 'UserName': Refund_Result[i][1], 'MID': Refund_Result[i][3], 'TID': Refund_Result[i][4], 'Amount': Refund_Result[i][6], 'RRN': Refund_Result[i][7], 'ResponseCode': f'{Refund_Result[i][9]}({Refund_Result[i][10]})', 'Email_Subject': Refund_Result[i][11], 'Remark': Refund_Result[i][12]})
                meta = {'status': 'confirm_Refund', 'msg': msg}
                returnmessage = {'meta': meta, 'data': data}
                log.info(returnmessage)
                log.end('Transaction')
                return jsonify(returnmessage)
    if MsgType == 'ISO' or MsgType == None: #ISO 接口
        eft = EFTPaymentsServer()
        Transaction_resp = TransactionRecord()
        eft.initialize(Till_Number, MID, TID, IP, Port, TPDU, COMMTYPE, Timeout)
        # 检查交易类型
        if TransactionType == 'SALE':
            iRet = eft.sale(barcode, amount, ecrRefNo)
            if iRet == 0:
                iRet = eft.getSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'VOID':
            iRet = eft.voidSale(amount, barcode, TraceNo)
            if iRet == 0:
                iRet = eft.getVoidSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'QUERY':
            iRet = eft.query(RRN, ApprovalCode)
            if iRet == 0:
                iRet = eft.getQueryResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'REFUND':
            iRet = eft.refund(RRN, amount, ecrRefNo, ApprovalCode)
            if iRet == 0:
                iRet = eft.getRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'SALEADVICE':
            iRet = eft.SaleAdvice(RRN, ecrRefNo, amount, ApprovalCode)
            if iRet == 0:
                iRet = eft.getSaleAdviceResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'REVERSAL':
            iRet = eft.Reversal(RRN, barcode, amount, TraceNo)
            if iRet == 0:
                iRet = eft.getReversalResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'AUTH':
            iRet = eft.AUTH(amount)
            if iRet == 0:
                iRet = eft.getAUTHResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'ADMINREFUND':
            iRet = eft.adminRefund(RRN, OriTID, amount, ecrRefNo)
            if iRet == 0:
                iRet = eft.getRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
                    Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=OriTID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=OriTID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)

    else:# XML接口
        XML = InterFace()
        XML_resp = XML_Resp()
        ShopCart = XML_Req()
        XML.initialize(Till_Number, MID, TID, URL, COMMTYPE, Timeout, PayType)
        amount = str(amount)
        if TransactionType == 'SALE':
            if Till_Number == 'payme':
                iRet = XML.SALE(barcode, amount, ecrRefNo, OrdDesc, 0, ShopCart)
            else:
                iRet = XML.SALE(barcode, amount, ecrRefNo, '', 0, ShopCart)
        elif TransactionType == 'VOID':
            iRet = XML.Void(barcode, amount, TraceNo)
        elif TransactionType == 'QUERY':
            iRet = XML.QUERY(RRN, barcode, AUTH)
        elif TransactionType == 'REFUND':
            iRet = XML.REFUND(RRN, amount, ecrRefNo, ApprovalCode)
        elif TransactionType == 'SALEADVICE':
            iRet = XML.SALE_ADVICE(RRN, ecrRefNo,barcode, ApprovalCode)
        elif TransactionType == 'REVERSAL':
            iRet = XML.REVERSAL(barcode, amount, RRN, TraceNo)
        elif TransactionType == 'AUTH':
            iRet = XML.AUTH(amount, ecrRefNo, OrdDesc, 0, ShopCart)
            #iRet = XML.AUTH(amount, ecrRefNo, OrdDesc, NumOfProduct, ShopCart)
        elif TransactionType == 'ADMINREFUND':
            iRet = XML.ADMIN_REFUND(RRN, amount, ecrRefNo, OriTID)

        if iRet == True:  # 成功
            iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
            meta = {'status': '0', 'msg': 'Success'}
            data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])
            if TransactionType == 'REFUND':
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                           respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            elif TransactionType == 'ADMINREFUND':
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=OriTID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                           respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                   TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'],
                                   approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                   respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)

        else:  # 失败
            status = iRet
            iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
            msg = iRet[4]
            meta = {'status': status, 'msg': msg}
            Utility.insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                       TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                       approvalCode=None,
                                       respondCode=None, respondText=meta['msg'])

    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('Transaction')
    return jsonify(returnmessage)


@app.route("/<Till_Number>/<BatchFor>/Upload", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def BatchFor(Till_Number, BatchFor):
    log.start('BatchFor')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    f = request.files['file']
    datetime = time.strftime("%Y%m%d%H%M%S", time.localtime())
    filepath = os.path.join('Batch Process/', '{0}_'.format(datetime) + secure_filename(f.filename))
    f.save(filepath)
    URL = request.form['URL']
    IP = request.form['IP']
    Port = request.form['Port']
    # return_url = request.form['return_url']
    TPDU = request.form['TPDU']
    COMMTYPE = request.form['COMMTYPE']
    if COMMTYPE == 'TLS':
        COMMTYPE = 2
    elif COMMTYPE == 'PlainText':
        COMMTYPE = 1
    Timeout = request.form['Timeout']
    ecrRefNo = request.form['ecrRefNo']
    APIType = ''
    out_trade_no = ''
    eft_trade_no = ''
    User_Confirm_Key = ''
    SecretCode = ''
    PaymentType = ''
    amount = ''
    wallet = 'HK'
    xlsx = xlrd.open_workbook(filepath)
    table = xlsx.sheet_by_index(0)
    meta = []
    data = []
    Email_Subject = ''
    Remark = ''
    RawRequest = ''
    nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if BatchFor == 'BatchForSale':
        meta = {'status': 0, 'msg': "All Account Activated"}
        amount = '10'
        barcode = '280000000000000000'
        for i in range(table.nrows):
            log.info(table.row_values(i))
            if (i == 0):
                data.append([table.row_values(i)[0], table.row_values(i)[1], 'Respond Code'])
                continue
            if table.cell(i,0).ctype == 2:
                MID = str(int(float(table.cell_value(i,0))))
            else:
                MID = table.cell_value(i,0)
            if table.cell(i, 1).ctype == 2:
                TID = str(int(float(table.cell_value(i, 1))))
            else:
                TID = table.cell_value(i,1)
            eft = EFTPaymentsServer()
            Transaction_resp = TransactionRecord()
            eft.initialize(Till_Number, MID, TID, IP, Port, TPDU, COMMTYPE, Timeout)
            iRet = eft.sale(barcode, amount, ecrRefNo)
            if iRet == 0:
                iRet = eft.getSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    if iRet[1].respondCode != '14' and iRet[1].respondCode != '30' and iRet[1].respondCode != '54':
                        meta = {'status': 1, 'msg': "Some Account did't Activate"}
                    data.append([MID,TID,iRet[1].respondCode])
            else:
                meta = {'status': 1, 'msg': "Some Account did't Activate"}
    elif BatchFor == 'BatchForRefund':
        if Till_Number == 'BOCVMP' or Till_Number == 'VMP':
            meta = {'status': 0, 'msg': "All Transactions Refund Success"}
            for i in range(table.nrows):
                log.info(table.row_values(i))
                if (i == 0):
                    data.append(['User_Confirm_Key','SecretCode','Amount','APIType', 'Payment Type','out_trade_no','eft_trade_no', 'Respond Code/Result','Email Subject','Remark'])
                    continue
                User_Confirm_Key = str(table.cell_value(i, 0)).replace(' ', '')
                SecretCode = str(table.cell_value(i, 1)).replace(' ', '')
                if table.cell(i, 2).ctype == 2:
                    amount = str(round(float(table.cell_value(i, 2)),2))
                else:
                    amount = str(round(float(table.cell_value(i, 2)), 2))
                # amount = str(table.cell_value(i, 2)).replace(' ', '')
                APIType = str(table.cell_value(i, 3)).replace(' ', '')
                PaymentType = str(table.cell_value(i, 4)).replace(' ', '')
                out_trade_no = str(table.cell_value(i, 5))
                eft_trade_no = str(table.cell_value(i, 6))
                Email_Subject = str(table.cell_value(i, 7))
                Remark = str(table.cell_value(i, 8))
                if Remark == '' or Remark == None:
                    Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
                URL = request.form['URL']
                if APIType == 'WEB':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.out_trade_no = out_trade_no
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.payType = 'Alipay'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.payType = 'WeChat'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.payType = 'ATOME'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.payType = 'UnionPay'
                    # VMP_req.payType = PaymentType
                    VMP_req.pay_scene = 'WEB'
                    VMP_req.reason = 'Refund'
                    VMP_req.return_amount = amount
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.service = 'service.alipay.web.Refund'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.service = 'service.wechat.web.Refund'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.service = 'service.atome.web.Refund'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.service = 'service.unionpay.web.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.total_fee = amount
                    VMP_req.user_confirm_key = User_Confirm_Key
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.wallet = 'ALIPAY' + wallet
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.wallet = 'WECHAT' + wallet
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.wallet = 'ATOME'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.wallet = 'UNIONPAY'
                    signStr = VMP.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
                    pass
                elif APIType == 'EOPG':
                    return_url = URL + f'/{Till_Number}/EOPG/eopg_return_addr'
                    URL += f'/{Till_Number}/eopg/ForexRefundRecetion'
                    EOPG_req = VMP.EOPG_Request()
                    EOPG_req.merch_ref_no = out_trade_no
                    EOPG_req.mid = User_Confirm_Key
                    EOPG_req.payment_type = PaymentType
                    EOPG_req.refund_amount = amount
                    EOPG_req.refund_reason = 'Refund'
                    EOPG_req.return_url = ''
                    EOPG_req.service = 'REFUND'
                    EOPG_req.trans_amount = amount
                    signStr = VMP.packSignStr_EOPG(EOPG_req, SecretCode)
                    log.info(signStr)
                    EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    EOPG_req.merch_refund_id = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    EOPG_req.api_version = '2.9'
                    EOPG_req.redirect = 'N'
                    EOPG_req.balance_ignore = 'N'
                    RawRequest = VMP.packGetMsg(EOPG_req, URL)
                elif APIType == 'JSAPI':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.out_trade_no = out_trade_no
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.payment_type = 'ALIPAY' + wallet
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.payment_type = 'WECHAT' + wallet
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.payType = 'Alipay'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.payType = 'WeChat'
                    VMP_req.refund_desc = 'Refund'
                    VMP_req.refund_no = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.service = 'service.alipay.jsapi.Refund'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.service = 'service.wechat.jsapi.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.total_fee = amount
                    VMP_req.transaction_amount = amount
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = VMP.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
                    pass
                elif APIType == 'APP':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'AppTradeRefund.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.out_trade_no = out_trade_no
                    VMP_req.reason = 'Refund'
                    VMP_req.return_amount = amount
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = VMP.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
                    pass
                elif APIType == 'QRCODE':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.buyertype = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_trade_no = out_trade_no
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.payment_type = 'ALIPAY' + wallet
                        VMP_req.paytype = 'Alipay'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.payment_type = 'WECHAT' + wallet
                        VMP_req.paytype = 'WeChet'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.payment_type = PaymentType
                        VMP_req.paytype = 'ATOME'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.payment_type = PaymentType
                        VMP_req.payType = 'UnionPay'
                    VMP_req.refund_no = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.service = 'service.alipay.qrcode.Refund'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.service = 'service.wechat.qrcode.Refund'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.service = 'service.atome.v1.qrcode.Refund'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.service = 'service.unionpay.qrcode.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.transaction_amount = amount
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = VMP.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
                    pass
                elif APIType == 'CASHIER':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.out_trade_no = out_trade_no
                    VMP_req.pay_scene = 'WAP'
                    VMP_req.reason = 'Refund'
                    VMP_req.return_amount = amount
                    VMP_req.service = 'service.united.wap.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = VMP.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
                    pass
                Refund_Result = Utility.check_vmp_refund_txn(GateName=Till_Number, user_confirm_key=User_Confirm_Key,
                                                             out_trade_no=out_trade_no, eft_trade_no=eft_trade_no)
                if Refund_Result != []:
                    data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, f'This transaction already did the refund by "{Refund_Result[0][1]}" on {Refund_Result[0][0]}. Not allow to use Batch Refund. Please use manual refund!', Refund_Result[0][13], Refund_Result[0][14]])
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                    continue
                log.info(f'URL: {URL}')
                log.info(f'RawRequest: {RawRequest}')
                resp = Utility.PostToHost(URL, RawRequest, timeout=30)
                if resp.status_code == 200:
                    log.info('RawResponse: {0}'.format(resp.text.encode("utf8")))
                    RawResponse = json.loads(resp.text.encode("utf8"))
                    if RawResponse['return_status'] == '00':
                        data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, RawResponse['return_status'], Email_Subject, Remark])
                    else:
                        meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                        data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, f"{RawResponse['return_status']}[{RawResponse['return_char']}]", Email_Subject, Remark])
                    Utility.insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, API_Type=APIType,
                                           PaymentType=PaymentType, TransType='REFUND', Amount=amount,
                                           user_confirm_key=User_Confirm_Key,
                                           Secret_Code=SecretCode, out_trade_no=out_trade_no, eft_trade_no=eft_trade_no,
                                           Response_Code=RawResponse['return_status'],
                                           Response_Text=RawResponse['return_char'], Email_Subject=Email_Subject,
                                           Remark=Remark)
                else:
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                    data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no,
                                 f"{resp.status_code}[{resp.text.encode('utf8')}]", Email_Subject,
                                 Remark])

        else:
            ApprovalCode = ''
            meta = {'status': 0, 'msg': "All Transactions Refund Success"}
            for i in range(table.nrows):
                log.info(table.row_values(i))
                if (i == 0):
                    if Till_Number == 'CUP' or Till_Number == 'BOC':
                        data.append(['MID','TID','Amount','RRN','ApprovalCode','Respond Code/Result','Email Subject','Remark'])
                    else:
                        data.append(['MID','TID','Amount','RRN','Respond Code/Result','Email Subject','Remark'])
                    continue
                if table.cell(i, 0).ctype == 2:
                    MID = str(int(float(table.cell_value(i, 0))))
                else:
                    MID = table.cell_value(i, 0)
                if table.cell(i, 1).ctype == 2:
                    TID = str(int(float(table.cell_value(i, 1))))
                else:
                    TID = table.cell_value(i, 1)
                if table.cell(i, 2).ctype == 2:
                    Amount = str(int(round(float(table.cell_value(i, 2) * 100),2)))
                else:
                    Amount = str(int(round(float(table.cell_value(i, 2)) * 100, 2)))
                if table.cell(i, 3).ctype == 2:
                    RRN = str(int(float(table.cell_value(i, 3))))
                else:
                    RRN = table.cell_value(i, 3)

                if Till_Number == 'CUP' or Till_Number == 'BOC':
                    if table.cell(i, 4).ctype == 2:
                        ApprovalCode = str(int(float(table.cell_value(i, 4))))
                    else:
                        ApprovalCode = table.cell_value(i, 4)
                    if table.cell(i, 5).ctype == 2:
                        Email_Subject = str(int(float(table.cell_value(i, 5))))
                    else:
                        Email_Subject = table.cell_value(i, 5)
                    if table.cell(i, 6).ctype == 2:
                        Remark = str(int(float(table.cell_value(i, 6))))
                    else:
                        Remark = table.cell_value(i, 6)
                else:
                    if table.cell(i, 4).ctype == 2:
                        Email_Subject = str(int(float(table.cell_value(i, 4))))
                    else:
                        Email_Subject = table.cell_value(i, 4)
                    if table.cell(i, 5).ctype == 2:
                        Remark = str(int(float(table.cell_value(i, 5))))
                    else:
                        Remark = table.cell_value(i, 5)

                # request by joe, if remark is empty, default is DD MMM YYYY format, (19 JAN 2022)
                if Remark == '' or Remark == None:
                    Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
                Refund_Result = Utility.check_offline_refund_txn(GateName=Till_Number, MID=MID, RRN=RRN)
                if Refund_Result != []:
                    if Till_Number == 'CUP' or Till_Number == 'BOC':
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, ApprovalCode, f'This transaction already did the refund by "{Refund_Result[0][1]}" on {Refund_Result[0][0]}. Not allow to use Batch Refund. Please use manual refund!',
                                    Refund_Result[0][11], Refund_Result[0][12]])
                    else:
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, f'This transaction already did the refund by "{Refund_Result[0][1]}" on {Refund_Result[0][0]}. Not allow to use Batch Refund. Please use manual refund!', Refund_Result[0][11],
                                    Refund_Result[0][12]])
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                    continue
                eft = EFTPaymentsServer()
                Transaction_resp = TransactionRecord()
                eft.initialize(Till_Number, MID, TID, IP, Port, TPDU, COMMTYPE, Timeout)
                iRet = eft.refund(RRN, Amount, ecrRefNo, ApprovalCode)
                if iRet == 0:
                    iRet = eft.getSaleResponse(Transaction_resp)
                    if iRet[0] == 0:
                        Utility.insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType='REFUND', Amount=Amount, RRN=RRN, approvalCode=ApprovalCode, respondCode=iRet[1].respondCode, respondText=iRet[1].respondText,Email_Subject=Email_Subject, Remark=Remark)
                        if iRet[1].respondCode != '00':
                            meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                        if Till_Number == 'CUP' or Till_Number == 'BOC':
                            data.append([MID, TID, round(float(int(Amount)/100),2), RRN, ApprovalCode, f'{iRet[1].respondCode}[{iRet[1].respondText}]', Email_Subject, Remark])
                        else:
                            data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, f'{iRet[1].respondCode}[{iRet[1].respondText}]', Email_Subject, Remark])
                else:
                    if Till_Number == 'CUP' or Till_Number == 'BOC':
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, ApprovalCode, f'{iRet}[{Utility.getResultMessage(iRet)}]', Email_Subject, Remark])
                    else:
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN,
                                     f'{iRet}[{Utility.getResultMessage(iRet)}]', Email_Subject, Remark])
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
    os.remove(filepath)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('BatchFor')
    return jsonify(returnmessage)

@app.route("/CUP/BatchForCardNo", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def BatchForCardNo():
    log.start('BatchForCardNo')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.header.get("username")
    f = request.files['file']
    filepath = os.path.join('Batch Process/', secure_filename(f.filename))
    f.save(filepath)
    xlsx = xlrd.open_workbook(filepath)
    table = xlsx.sheet_by_index(0)
    meta = {'status': 1, 'msg': "Failed"}
    data = []
    for i in range(table.nrows):
        log.info(table.row_values(i))
        # Column 19 == Masked CardNo
        if (i == 0):
            header = []
            for j in table.row_values(i):
                header.append(j)
            header.append('Real CardNo')
            data.append(header)
            continue
        rowData = []
        for j in range(table.ncols):
            if table.cell(i,j).ctype == 2:
                rowData.append(str(int(float(table.cell_value(i,j)))))
            else:
                rowData.append(table.cell_value(i,j))
        rowData.append(Utility.convertToCardNo(table.cell_value(i,18)))
        data.append(rowData)
    meta = {'status': 0, 'msg': "Success"}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('BatchForCardNo')
    return jsonify(returnmessage)

@app.route("/A8_Password", methods=['GET'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def A8_Password():
    log.start('A8_Password')
    log.info(request.headers)
    # log.info()()("BODY: %s" % request.get_data())
    #http://10.17.2.238/password/
    meta = {}
    data = {}
    username = request.headers.get("username")
    url = 'http://10.17.2.238/password/'
    response = requests.get(url)
    temp = response.text.find('password')
    password = str(response.text)
    password = password[temp+10:temp+16]
    trainingmodePW = '80' + password
    data = {"password": password, "trainingmodePW": trainingmodePW}
    meta = {'status': 200, 'msg': 'success'}
    returnmessage = {'meta': meta, 'data':data }
    log.info(returnmessage)
    log.end('A8_Password')
    return jsonify(returnmessage)

@app.route("/Octopus/Report/<action>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Octopus_Report(action):
    log.start('Octopus_Report')
    log.info(request.headers)
    # log.info()()("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    meta = {}
    data = {}
    # try:
    if action == 'Check_SPIDStatus':
        SPID = request.json.get("SPID")
        DateFrom = request.json.get("DateFrom")
        DateTo = request.json.get("DateTo")
        temp = Octopus.Report()
        result = temp.Check_SPIDStatus(SPID, DateFrom, DateTo)
        if result[0] == True:
            meta = {'status': 0, 'msg': '{0}'.format(result[1])}
        else:
            meta = {'status': 1, 'msg': '{0}'.format(result[1])}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'Download_SPID':
        SPID = request.json.get("SPID")
        DateFrom = request.json.get("DateFrom")
        DateTo = request.json.get("DateTo")
        temp = Octopus.Report()
        result = temp.Download_SPID(SPID, DateFrom, DateTo)
        log.end('Octopus_Report')
        return send_file(result[1], as_attachment=True)
    elif action == 'Download_MonthlyReport':
        Month = request.json.get("Month")
        temp = Octopus.Report()
        Monthly_Report_Status = temp.Check_MonthlyReportStatus(Month)
        if Monthly_Report_Status[0] == True:
            result = temp.Download_MonthlyReport(Month)
            if result[0] == True:
                meta = {'status': 0, 'msg': 'Success'}
                data = result[1]
            else:
                meta = {'status': 1, 'msg': 'Failed'}
        else:
            meta = {'status': 1, 'msg': Monthly_Report_Status[1]}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'Download_YearlyReport':
        Year = request.json.get("Year")
        temp = Octopus.Report()
        Yearly_Report_Status = temp.Check_YearlyReportStatus(Year)
        if Yearly_Report_Status[0] == True:
            result = temp.Download_YearlyReport(Year)
            if result[0] == True:
                meta = {'status': 0, 'msg': 'Success'}
                data = result[1]
            else:
                meta = {'status': 1, 'msg': 'Failed'}
        else:
            meta = {'status': 1, 'msg': Yearly_Report_Status[1]}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'UploadRawData':
        log.info(request.files)
        files = request.files.getlist("files")
        # files = files.split(",")
        # files = list(filter(None, files))
        for f in files:
            # f = request.files[file]
            # namefile = secure_filename(file)
            pass
            # f = request.files['files']
            filepath = os.path.join('Octopus/Rawfiles/', secure_filename(f.filename))
            directory = str(f.filename).split('.')
            unzipPath = os.path.join('Octopus/Parsefiles/', '')
            # unzipPath = os.path.join('Octopus/Parsefiles/', secure_filename(directory[0]))
            f.save(filepath)
            with ZipFile(filepath, 'r') as zipObj:
                zipObj.extractall(unzipPath)
        meta = {'status': 0, 'msg': '{}'.format('Upload Success')}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)

@app.route("/PAOB/Report/<action>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def PAOB_Report(action):
    log.start('PAOB_Report')
    log.info(request.headers)
    # log.info()()("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    meta = {}
    data = {}
    if action == 'UploadRawData':
        log.info(request.files)
        files = request.files.getlist("files")
        data = []
        for f in files:
            filepath = os.path.join('PAOB/', secure_filename(f.filename))
            f.save(filepath)
            vlookupFile = ''
            i = 1
            with open(os.path.join('PAOB/','temp.txt')) as temp:
                vlookupFile = temp.read().splitlines()
                # log.info(vlookupFile)
            with open(filepath, newline='') as csvfile:
                rows = csv.reader(csvfile)
                addHeader = False
                for row in rows:
                    # log.info(f'{i}: {row}')
                    # log.info(row[0])
                    # i += 1
                    if addHeader == False:
                        data.append(row)
                        addHeader = True
                    if len(row) != 0:
                        if row[0] in vlookupFile:
                            if row[8] == 'SALE ADVICE':
                                row[8] = 'SALE'
                            data.append(row)
            os.remove(filepath)
        meta = {'status': 0, 'msg': '{}'.format('Upload Success')}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('PAOB_Report')
        return jsonify(returnmessage)

@app.route("/VMP/<Gateway>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def VMP_Transaction(Gateway):
    log.start('VMP_Transaction')
    log.info(request.headers)
    log.info("JSON: %s" % request.json)
    username = request.headers.get("username")
    service = request.json.get('service')
    User_Confirm_Key = request.json.get('User_Confirm_Key')
    PaymentType = request.json.get('PaymentType')
    wallet = request.json.get('wallet')
    amount = str(request.json.get('amount'))
    SecretCode = request.json.get('SecretCode')
    TransactionType = request.json.get('TransactionType')
    out_trade_no = request.json.get('out_trade_no')
    if out_trade_no == '' and str(TransactionType).upper() == 'SALE':
        out_trade_no = time.strftime("%Y%m%d%H%M%S", time.localtime())
    eft_trade_no = request.json.get('eft_trade_no')
    refund_no = request.json.get('refund_no')
    if refund_no == '' and str(TransactionType).upper() == 'REFUND':
        refund_no = 'refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
    buyerType = request.json.get('buyerType')
    subject = request.json.get('subject')
    body = request.json.get('body')
    fee_type = request.json.get('fee_type')
    tid = request.json.get('tid')
    scene_type = request.json.get('scene_type')
    openid = request.json.get('openid')
    sub_openid = request.json.get('sub_openid')
    wechatWeb = request.json.get('wechatWeb')
    active_time = request.json.get('active_time')
    URL = request.json.get('URL')
    notify_url = request.json.get('notify_url')
    return_url = request.json.get('return_url')
    reuse = request.json.get('reuse')
    lang = request.json.get('lang')
    redirect = request.json.get('redirect')
    refund_reason = request.json.get('refund_reason')
    APIType = request.json.get('APIType')
    GatewayType = request.json.get('GatewayType')
    Gateway_Name = request.json.get('Gateway_Name')
    app_pay = request.json.get('app_pay')
    customerInfo = request.json.get('customerInfo')
    shippingAddress = request.json.get('shippingAddress')
    billingAddress = request.json.get('billingAddress')
    Email_Subject = request.json.get('Email_Subject')
    Remark = request.json.get('Remark')
    if str(TransactionType).upper() == 'REFUND':
        if Remark == '' or Remark == None:
            Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
    items = request.json.get('items')
    NewInterFace = request.json.get('NewInterFace')
    iRet = -1
    meta = {}
    data = []
    signStr = ''
    RawRequest = None
    RawResponse = None
    errormessage = ''
    EOPG_req = None
    VMP_req = None
    JSONMessage = None
    msg = ''
    nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    confirm_Refund = request.json.get('confirm_Refund')
    # check refund record
    if confirm_Refund != 'Y':
        if str(TransactionType).upper() == 'REFUND':
            Refund_Result = Utility.check_vmp_refund_txn(GateName=Gateway, user_confirm_key=User_Confirm_Key, out_trade_no=out_trade_no, eft_trade_no=eft_trade_no)
            if Refund_Result != []:
                for i in range(len(Refund_Result)):
                    data.append({'ID': i, 'DateTime': Refund_Result[i][0], 'UserName': Refund_Result[i][1],'API_Type': Refund_Result[i][3],
                                 'PaymentType': Refund_Result[i][4], 'TransType': Refund_Result[i][5], 'user_confirm_key': Refund_Result[i][6],
                                 'Amount': Refund_Result[i][8],'out_trade_no': Refund_Result[i][9], 'eft_trade_no': Refund_Result[i][10],
                                 'ResponseCode': f'{Refund_Result[i][11]}',
                                 'Email_Subject': Refund_Result[i][13], 'Remark': Refund_Result[i][14]})
                meta = {'status': 'confirm_Refund', 'msg': msg}
                returnmessage = {'meta': meta, 'data': data}
                log.info(returnmessage)
                log.end('VMP_Transaction')
                return jsonify(returnmessage)
    if APIType == 'EOPG': #EOPG 接口
        if return_url == '':
            return_url = URL + f'/{Gateway}/EOPG/eopg_return_addr'
        if str(TransactionType).upper() == 'SALE':
            URL += f'/{Gateway}/eopg/ForexTradeRecetion'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.fee_type = fee_type
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            EOPG_req.trans_amount = amount
            EOPG_req.wechatWeb = wechatWeb
            signStr = VMP.packSignStr_EOPG(EOPG_req,SecretCode)
            log.info(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.app_pay = app_pay
            EOPG_req.return_url = return_url
            EOPG_req.goods_subject = subject
            EOPG_req.goods_body = body
            EOPG_req.notify_url = notify_url
            EOPG_req.wallet = wallet
            EOPG_req.tid = tid
            EOPG_req.active_time = active_time
            EOPG_req.api_version = '2.9'
            EOPG_req.lang = lang
            EOPG_req.reuse = reuse
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
        elif str(TransactionType).upper() == 'REFUND':
            URL += f'/{Gateway}/eopg/ForexRefundRecetion'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.refund_amount = amount
            EOPG_req.refund_reason = refund_reason
            EOPG_req.return_url = ''
            EOPG_req.service = service
            EOPG_req.trans_amount = amount
            signStr = VMP.packSignStr_EOPG(EOPG_req, SecretCode)
            log.info(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.merch_refund_id = refund_no
            EOPG_req.api_version = '2.9'
            EOPG_req.redirect = redirect
            EOPG_req.balance_ignore = 'N'
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
            # teustubg
        elif str(TransactionType).upper() == 'QUERY':
            URL += f'/{Gateway}/eopg/ForexCheckQuery'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            signStr = VMP.packSignStr_EOPG(EOPG_req, SecretCode)
            log.info(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.api_version = '2.9'
            EOPG_req.redirect = redirect
            EOPG_req.return_url = return_url
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
        elif str(TransactionType).upper() == 'QUERYREFUND':
            URL += f'/{Gateway}/eopg/ForexCheckRefund'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.merch_refund_id = refund_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            signStr = VMP.packSignStr_EOPG(EOPG_req, SecretCode)
            log.info(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.api_version = '2.9'
            EOPG_req.redirect = redirect
            EOPG_req.return_url = ''
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
    elif APIType == 'WEB':
        if return_url == '':
            return_url = URL + '/VMP/returnSuccess'
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.active_time = active_time
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.billingAddress = str(billingAddress)
            VMP_req.body = body
            VMP_req.buyerType = buyerType
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.customerInfo = str(customerInfo)
            VMP_req.fee_type = fee_type
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.items = str(items)
            VMP_req.lang = lang
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            VMP_req.payType = PaymentType
            if service == 'service.wechat.oauth2.Authorize':
                VMP_req.pay_scene = 'WXWEB'
            elif service == 'service.alipay.wap.PreOrder':
                VMP_req.pay_scene = 'WAP'
            elif service == 'service.unionpay.online.web.PreOrder':
                VMP_req.pay_scene = 'ONLINE_WEB'
            elif service == 'service.jetco.wap.PreOrder':
                VMP_req.pay_scene = 'WAP'
            else:
                VMP_req.pay_scene = 'WEB'
            VMP_req.return_url = return_url
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.web.PreOrder'
            else:
                VMP_req.service = service
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.shippingAddress = str(shippingAddress)
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.wallet = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.wallet = 'WECHAT' + wallet
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.wallet = 'ATOME'
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.wallet = 'UNIONPAY'
            elif str(PaymentType).upper() == 'JETCO':
                VMP_req.wallet = 'JETCOHK'
            elif str(PaymentType).upper() == 'OCT':
                VMP_req.wallet = 'OCT'
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.buyerType = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_refund_no = refund_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.payType = PaymentType
            if service == 'service.alipay.wap.Refund':
                VMP_req.pay_scene = 'WAP'
            elif service == 'service.unionpay.online.web.Refund':
                VMP_req.pay_scene = 'ONLINE_WEB'
            elif service == 'service.jetco.wap.Refund':
                VMP_req.pay_scene = 'WAP'
            else:
                VMP_req.pay_scene = 'WEB'
            VMP_req.reason = body
            VMP_req.return_amount = amount
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.web.Refund'
            else:
                VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.total_fee = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.wallet = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.wallet = 'WECHAT' + wallet
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.wallet = 'ATOME'
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.wallet = 'UNIONPAY'
            elif str(PaymentType).upper() == 'JETCO':
                VMP_req.wallet = 'JETCOHK'
            elif str(PaymentType).upper() == 'OCT':
                VMP_req.wallet = 'OCT'
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
            if NewInterFace:
                URL = URL + 'JSAPIService.do'
            else:
                URL = URL + 'QRcodeTradeQuery.do'
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            if NewInterFace:
                VMP_req.service = 'service.common.Query'
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
    elif APIType == 'JSAPI':
        if return_url == '':
            return_url = URL + '/VMP/returnSuccess'
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.fee_type = fee_type
            VMP_req.notify_url = notify_url
            VMP_req.openid = openid
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
            VMP_req.paytype = PaymentType
            VMP_req.return_url = return_url
            VMP_req.scene_type = scene_type
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.jsapi.PreOrder'
            else:
                VMP_req.service = service
            VMP_req.sub_openid = sub_openid
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
            VMP_req.paytype = PaymentType
            VMP_req.refund_desc = body
            VMP_req.refund_no = refund_no
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.jsapi.Refund'
            else:
                VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.total_fee = amount
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
            if NewInterFace:
                URL = URL + 'CommonTradeQuery.do'
            else:
                URL = URL + 'QRcodeTradeQuery.do'
            VMP_req.buyertype = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
            VMP_req.paytype = PaymentType
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
    elif APIType == 'QRCode':
        if return_url == '':
            return_url = URL + '/VMP/returnSuccess'
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.buyertype = buyerType
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.payType = PaymentType
                VMP_req.pay_scene = 'QRCODE'
                VMP_req.payment_type = PaymentType.upper()
            elif str(PaymentType).upper() == 'GBPAY':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.qrcode.PreOrder'
            else:
                VMP_req.service = service
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.buyertype = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.payment_type = PaymentType
                VMP_req.payType = PaymentType
            VMP_req.refund_no = refund_no
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.qrcode.Refund'
            else:
                VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
            # if NewInterFace:
            #     URL = URL + 'CommonTradeQuery.do'
            # else:
            #     URL = URL + 'JSAPIService.do'
            URL = URL + 'JSAPIService.do'
            VMP_req.eftpay_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.payType = PaymentType
                VMP_req.payment_type = 'UNIONPAY'
            elif str(PaymentType).upper() == 'GBPAY':
                VMP_req.payment_type = 'GBPAY'
                VMP_req.paytype = PaymentType
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.qrcode.Query'
            else:
                VMP_req.service = service

            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'CANCEL':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'QRcodeTradeCancel.do'
            VMP_req.buyertype = buyerType
            VMP_req.out_trade_no = out_trade_no
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.payment_type = 'ALIPAY' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.payment_type = 'WECHAT' + wallet
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ATOME':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'UNIONPAY':
                VMP_req.payment_type = PaymentType
                VMP_req.payType = PaymentType
            # if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
            #     VMP_req.service = 'service.alipayplus.qrcode.Refund'
            # else:
            #     VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
    elif APIType == 'APP':
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            if NewInterFace:
                URL = URL + 'CommonAppTradePay.do'
            else:
                URL = URL + 'AppTradePay.do'
            VMP_req.body = body
            VMP_req.buyerType = buyerType
            VMP_req.fee_type = fee_type
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            VMP_req.payType = PaymentType
            VMP_req.pay_scene = 'APP'
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.wallet = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.wallet = 'WECHAT' + wallet
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            if NewInterFace:
                URL = URL + 'CommonAppTradeRefund.do'
            else:
                URL = URL + 'AppTradeRefund.do'
            VMP_req.buyerType = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_refund_no = refund_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.reason = body
            VMP_req.return_amount = amount
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
            if NewInterFace:
                URL = URL + 'CommonTradeQuery.do'
            else:
                URL = URL + 'QRcodeTradeQuery.do'
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
    elif APIType == 'Cashier':
        if return_url == '':
            return_url = URL + '/VMP/returnSuccess'
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.active_time = active_time
            VMP_req.body = body
            VMP_req.buyerType = buyerType
            VMP_req.fee_type = fee_type
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            VMP_req.pay_scene = 'WAP'
            VMP_req.return_url = return_url
            VMP_req.service = service
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.buyerType = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_refund_no = refund_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.pay_scene = 'WAP'
            VMP_req.reason = body
            VMP_req.return_amount = amount
            if NewInterFace:
                VMP_req.service = 'service.common.Refund'
            else:
                VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'QRcodeTradeQuery.do'
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            log.info(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            pass
    log.info('RawRequest: {0}'.format(RawRequest))
    if APIType == 'EOPG':
        if (str(TransactionType).upper()) != 'SALE':
            resp = Utility.GetToHost(RawRequest, timeout=30)
            if resp.status_code == 200:
                log.info('RawResponse: {0}'.format(resp.text))
                RawResponse = str(resp.text)
                JSONMessage = dict(x.split('=') for x in resp.text.split('&'))
                Utility.insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Gateway, API_Type=APIType,
                                       PaymentType=PaymentType, TransType=str(TransactionType).upper(), Amount=amount,
                                       user_confirm_key=User_Confirm_Key,
                                       Secret_Code=SecretCode, out_trade_no=out_trade_no, eft_trade_no=eft_trade_no,
                                       Response_Code=JSONMessage['return_status'],
                                       Response_Text=JSONMessage['return_char'], Email_Subject=Email_Subject,
                                       Remark=Remark)
    else:
        resp = Utility.PostToHost(URL, RawRequest, timeout=30)
        if resp.status_code == 200:
            log.info('RawResponse: {0}'.format(resp.text.encode("utf8")))
            RawResponse = json.loads(resp.text.encode("utf8"))
            Utility.insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Gateway, API_Type=APIType,
                                       PaymentType=PaymentType, TransType=str(TransactionType).upper(), Amount=amount, user_confirm_key=User_Confirm_Key,
                                       Secret_Code=SecretCode,out_trade_no=out_trade_no, eft_trade_no=eft_trade_no,
                                       Response_Code=RawResponse['return_status'], Response_Text=RawResponse['return_char'], Email_Subject=Email_Subject,
                                       Remark=Remark)

    data = {'RawRequest': RawRequest, 'RawResponse': RawResponse, 'JSONMessage': JSONMessage}
    meta = {'status': 0, 'msg': 'Success'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('VMP_Transaction')
    return jsonify(returnmessage)

@app.route("/download/<string:filename>", methods=['GET'])
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def imagedownload(filename):
    log.start('imagedownload')
    currentlyPath = os.getcwd()
    if (os.path.isfile(os.path.join(currentlyPath,filename))):
        log.end('imagedownload')
        return send_from_directory(currentlyPath,filename, as_attachment=True)
    return '404 NOT FOUND'

@app.route("/setconfig/<Till_Number>/<TransactionType>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def setconfig(Till_Number,TransactionType):
    log.start('setconfig')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    Tag = request.json.get('Tag')
    MID = request.json.get('MID')
    TID = request.json.get('TID')
    barcode = request.json.get('barcode')
    amount = request.json.get('amount')
    ecrRefNo = request.json.get('ecrRefNo')
    ApprovalCode = request.json.get('ApprovalCode')
    TransactionType = TransactionType
    RRN = request.json.get('RRN')
    IP = request.json.get('IP')
    Port = request.json.get('Port')
    TPDU = request.json.get('TPDU')
    COMMTYPE = request.json.get('COMMTYPE')
    Timeout = request.json.get('Timeout')
    MsgType = request.json.get('MsgType')
    TraceNo = request.json.get('TraceNo')
    URL = request.json.get('URL')
    OrdDesc = request.json.get('OrdDesc')
    PayType = request.json.get('PayType')
    NumOfProduct = request.json.get('NumOfProduct')
    AUTH = request.json.get('AUTH')
    shopcarts = request.json.get('AUTH')
    OriTID = request.json.get('OriTID')
    User_Confirm_Key = request.json.get('User_Confirm_Key')
    SecretCode = request.json.get('SecretCode')
    Amount = request.json.get('Amount')
    Service = request.json.get('Service')
    out_trade_no = request.json.get('out_trade_no')
    TransactionType = request.json.get('TransactionType')
    PaymentType = request.json.get('PaymentType')
    eft_trade_no = request.json.get('eft_trade_no')
    refund_no = request.json.get('refund_no')
    Wallet = request.json.get('Wallet')
    APIType = request.json.get('APIType')
    Gateway_Name = Till_Number
    buyerType = request.json.get('buyerType')
    subject = request.json.get('subject')
    body = request.json.get('body')
    fee_type = request.json.get('fee_type')
    tid = request.json.get('tid')
    scene_type = request.json.get('scene_type')
    openid = request.json.get('openid')
    sub_openid = request.json.get('sub_openid')
    wechatWeb = request.json.get('wechatWeb')
    active_time = request.json.get('active_time')
    notify_url = request.json.get('notify_url')
    return_url = request.json.get('return_url')
    app_pay = request.json.get('app_pay')
    lang = request.json.get('lang')
    goods_body = request.json.get('goods_body')
    goods_subject = request.json.get('goods_subject')
    reuse = request.json.get('reuse')
    redirect = request.json.get('redirect')
    refund_reason = request.json.get('refund_reason')
    reason = request.json.get('reason')
    mobileNumber = request.json.get('mobileNumber')
    fullName = request.json.get('fullName')
    shippingAddress_countryCode = request.json.get('shippingAddress_countryCode')
    shippingAddress_postCode = request.json.get('shippingAddress_postCode')
    shippingAddress_lines = request.json.get('shippingAddress_lines')
    billingAddress_countryCode = request.json.get('billingAddress_countryCode')
    billingAddress_postCode = request.json.get('billingAddress_postCode')
    billingAddress_lines = request.json.get('billingAddress_lines')
    cmd = request.json.get('cmd')
    clientId = request.json.get('clientId')
    merchantRef = request.json.get('merchantRef')
    type = request.json.get('type')
    goodsName = request.json.get('goodsName')
    Flow = request.json.get('Flow')
    orderId = request.json.get('orderId')
    URL = request.json.get('URL')
    goodsDesc = request.json.get('goodsDesc')
    channel = request.json.get('channel')
    cardToken = request.json.get('cardToken')
    cardTokenSrc = request.json.get('cardTokenSrc')
    successUrl = request.json.get('successUrl')
    failureUrl = request.json.get('failureUrl')
    webhookUrl = request.json.get('webhookUrl')
    duration = request.json.get('duration')
    durationHr = request.json.get('durationHr')
    privateKey = request.json.get('privateKey')
    publicKey = request.json.get('publicKey')
    JavaScriptLibrary = request.json.get('JavaScriptLibrary')
    locale = request.json.get('locale')

    iRet = -1
    data = {}
    if Till_Number == 'VMP' or Till_Number == 'BOCVMP':
        meta = Utility.setconfig_VMP(username=username, Tag=Tag, User_Confirm_Key=User_Confirm_Key,
                                     SecretCode=SecretCode, Amount=Amount, Service=Service, out_trade_no=out_trade_no, TransactionType=TransactionType,
                                     PaymentType=PaymentType, eft_trade_no=eft_trade_no, refund_no=refund_no, Wallet=Wallet, APIType=APIType,
                                     Gateway_Name=Gateway_Name, buyerType=buyerType, subject=subject, body=body, fee_type=fee_type, tid=tid,
                                     scene_type=scene_type, openid=openid, sub_openid=sub_openid, wechatWeb=wechatWeb, active_time=active_time, URL=URL, notify_url=notify_url,
                                     return_url=return_url, app_pay=app_pay, lang=lang, goods_body=goods_body, goods_subject=goods_subject,
                                     reuse=reuse, redirect=redirect, refund_reason=refund_reason, reason=reason, mobileNumber=mobileNumber,
                                     fullName=fullName, shippingAddress_countryCode=shippingAddress_countryCode, shippingAddress_postCode=shippingAddress_postCode, shippingAddress_lines=shippingAddress_lines, billingAddress_countryCode=billingAddress_countryCode, billingAddress_postCode=billingAddress_postCode, billingAddress_lines=billingAddress_lines)
    elif Till_Number == 'Spiral':
        meta = Utility.setconfig_Spiral(username=username,Tag=Tag, clientId=clientId, merchantRef=merchantRef, cmd=cmd, amount=amount, type=type, goodsName=goodsName, Flow=Flow, orderId=orderId, URL=URL, goodsDesc=goodsDesc, channel=channel, cardToken=cardToken, cardTokenSrc=cardTokenSrc, successUrl=successUrl, failureUrl=failureUrl, webhookUrl=webhookUrl, duration=duration, durationHr=durationHr, privateKey=privateKey, publicKey=publicKey, JavaScriptLibrary=JavaScriptLibrary, locale=locale)
    else:
        meta = Utility.setconfig_Offline(username=username,Gateway_Name=Till_Number, Tag=Tag, MID=MID, TID=TID, TransactionType=TransactionType, PaymentType=PayType, amount=amount, barcode=barcode, ApprovalCode=ApprovalCode, RRN=RRN, TraceNo=TraceNo, OriTID=OriTID, URL=URL, IP=IP, Port=Port, TPDU=TPDU, Timeout=Timeout, MsgType=MsgType, COMMTYPE=COMMTYPE)
    returnmessage = {'meta': meta, 'data': data}
    return jsonify(returnmessage)

@app.route("/loadconfig/<Till_Number>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def loadconfig(Till_Number):
    log.start('loadconfig')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    iRet = -1
    data = Utility.loadconfig(username=username,Gateway_Name=Till_Number)
    meta = {'status': 0, 'msg': 'Success'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    return jsonify(returnmessage)

@app.route("/deleteconfig/<Till_Number>/<Tag>", methods=['POST'])
@jwt_required
@decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def deleteconfig(Till_Number, Tag):
    log.start('deleteconfig')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    iRet = -1
    data = {}
    meta = Utility.deleteconfig(username=username,Gateway_Name=Till_Number, Tag=Tag)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    return jsonify(returnmessage)


if __name__ == '__main__':
    log.start('Flask')
    app.run(host='0.0.0.0', port=5000)
    log.end('Flask')
