import os
from flask import Flask, current_app, session, make_response, send_from_directory, request, jsonify, send_file, json
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
import clr
from werkzeug.utils import secure_filename
import xlrd
import Utility
import Configuration
import logging
import time
import datetime
import requests
import Octopus
import hashlib
import VMP
from zipfile import ZipFile
import Log
from logging.handlers import TimedRotatingFileHandler
clr.FindAssembly('EFTPaymentsServer.dll')
clr.AddReference('EFTPaymentsServer')
clr.FindAssembly('XML_InterFace.dll')
# clr.AddReference('InterFace')
clr.AddReference('XML_InterFace')
from EFTSolutions import *
from XML_InterFace import *

app = Flask(__name__)
# 設定 JWT 密鑰
app.config['JWT_SECRET_KEY'] = 'Testing123'
jwt = JWTManager()
jwt.init_app(app)
now_date = time.strftime("%Y%m%d", time.localtime())
logging.basicConfig(level=logging.DEBUG)
# file_log_handler = RotatingFileHandler("logs/{0}.log".format(now_date), maxBytes=1024 * 1024 * 100, backupCount=10)
file_log_handler = TimedRotatingFileHandler("logs/{0}.log".format(now_date), when='midnight',interval=1, backupCount=10)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)
CORS(app)

@app.route("/login", methods=['POST'])
def login():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
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
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/ChangePassword", methods=['POST'])
def ChangePassword():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.json.get("username")
    oldpassword = request.json.get("oldpassword")
    newpassword = request.json.get("newpassword")
    meta = {'status': 'Failed', 'msg': 'Password Not Match'}
    data = {}
    meta = Utility.ChangePassword(username, oldpassword,newpassword)
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/userView", methods=['GET'])
@jwt_required
def userView():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.args.get('username')
    data = Utility.userView(username)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/menus", methods=['GET'])
@jwt_required
def menu():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.args.get('username')
    data = Utility.get_Menu(username)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/userlist", methods=['GET'])
@jwt_required
def userlist():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.args.get('username')
    pagenum = request.args.get('pagenum')
    pagesize = request.args.get('pagesize')
    data = Utility.get_userlist(int(pagenum), int(pagesize))
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/updateuserstatus", methods=['GET'])
@jwt_required
def updateuserstatus():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.args.get('username')
    status = request.args.get('status')
    data = Utility.update_AccountStatus(username, status)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/deleteUser", methods=['GET'])
@jwt_required
def deleteUser():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.args.get('username')
    status = request.args.get('status')
    data = Utility.delete_Account(username)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/<Till_Number>/<TransactionType>", methods=['POST'])
@jwt_required
def Transaction(Till_Number, TransactionType):
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
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
    iRet = -1
    meta = {}
    data = {}
    RawRequest = ''
    RawResponse = ''
    errormessage = ''
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
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'VOID':
            iRet = eft.voidSale(amount, barcode, TraceNo)
            if iRet == 0:
                iRet = eft.getVoidSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
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
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'SALEADVICE':
            iRet = eft.SaleAdvice(RRN, ecrRefNo, amount, ApprovalCode)
            if iRet == 0:
                iRet = eft.getSaleAdviceResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'REVERSAL':
            iRet = eft.Reversal(RRN, barcode, amount, TraceNo)
            if iRet == 0:
                iRet = eft.getReversalResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'AUTH':
            iRet = eft.AUTH(amount)
            if iRet == 0:
                iRet = eft.getAUTHResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}
        elif TransactionType == 'ADMINREFUND':
            iRet = eft.adminRefund(RRN, OriTID, amount, ecrRefNo)
            if iRet == 0:
                iRet = eft.getRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': Utility.getResultMessage(str(iRet[0]))}
                    data = Utility.getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': Utility.getResultMessage(str(iRet))}

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
            if iRet == True: # 交易成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else: #交易失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}

        elif TransactionType == 'VOID':
            iRet = XML.Void(barcode, amount, TraceNo)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'QUERY':
            iRet = XML.QUERY(RRN, barcode, AUTH)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'REFUND':
            iRet = XML.REFUND(RRN, amount, ecrRefNo, ApprovalCode)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'SALEADVICE':
            iRet = XML.SALE_ADVICE(RRN, ecrRefNo,barcode, ApprovalCode)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'REVERSAL':
            iRet = XML.REVERSAL(barcode, amount, RRN, TraceNo)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'AUTH':
            iRet = XML.AUTH(amount, ecrRefNo, OrdDesc, 0, ShopCart)
            #iRet = XML.AUTH(amount, ecrRefNo, OrdDesc, NumOfProduct, ShopCart)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}
        elif TransactionType == 'ADMINREFUND':
            iRet = XML.ADMIN_REFUND(RRN, amount, ecrRefNo, OriTID)
            if iRet == True:  # 成功
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                meta = {'status': '0', 'msg': 'Success'}
                data = Utility.getXmlResp(iRet[1], iRet[2], iRet[3])

            else:  # 失败
                status = iRet
                iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
                msg = iRet[4]
                meta = {'status': status, 'msg': msg}

    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)


@app.route("/<Till_Number>/<BatchFor>/Upload", methods=['POST'])
@jwt_required
def BatchFor(Till_Number, BatchFor):
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    f = request.files['file']
    filepath = os.path.join('Batch Process/', secure_filename(f.filename))
    f.save(filepath)
    IP = request.form['IP']
    Port = request.form['Port']
    TPDU = request.form['TPDU']
    COMMTYPE = request.form['COMMTYPE']
    Timeout = request.form['Timeout']
    ecrRefNo = request.form['ecrRefNo']
    xlsx = xlrd.open_workbook(filepath)
    table = xlsx.sheet_by_index(0)

    data = []
    if BatchFor == 'BatchForSale':
        meta = {'status': 0, 'msg': "All Account Activated"}
        amount = '10'
        barcode = '280000000000000000'
        for i in range(table.nrows):
            current_app.logger.info(table.row_values(i))
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
        ApprovalCode = ''
        meta = {'status': 0, 'msg': "All Transactions Refund Success"}
        for i in range(table.nrows):
            current_app.logger.info(table.row_values(i))
            if (i == 0):
                if Till_Number == 'CUP' or Till_Number == 'BoC':
                    data.append([table.row_values(i)[0],
                                 table.row_values(i)[1],
                                 table.row_values(i)[2],
                                 table.row_values(i)[3],
                                 table.row_values(i)[4],
                                 'Respond Code'])
                else:
                    data.append([table.row_values(i)[0],
                                 table.row_values(i)[1],
                                 table.row_values(i)[2],
                                 table.row_values(i)[3],
                                 'Respond Code'])
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
                Amount = str(int(round(float(table.cell_value(i, 2)*100),2)))
            else:
                Amount = round(float(table.cell_value(i, 2)*100),2)
            if table.cell(i, 3).ctype == 2:
                RRN = str(int(float(table.cell_value(i, 3))))
            else:
                RRN = table.cell_value(i, 3)
            if Till_Number == 'CUP' or Till_Number == 'BoC':
                if table.cell(i, 4).ctype == 2:
                    ApprovalCode = str(int(float(table.cell_value(i, 4))))
                else:
                    ApprovalCode = table.cell_value(i, 4)
            eft = EFTPaymentsServer()
            Transaction_resp = TransactionRecord()
            eft.initialize(Till_Number, MID, TID, IP, Port, TPDU, COMMTYPE, Timeout)
            iRet = eft.refund(RRN, Amount, ecrRefNo, ApprovalCode)
            if iRet == 0:
                iRet = eft.getSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    if iRet[1].respondCode != '00':
                        meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                    if Till_Number == 'CUP' or Till_Number == 'BoC':
                        data.append([MID, TID, round(float(int(Amount)/100),2), RRN, ApprovalCode, iRet[1].respondCode])
                    else:
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, iRet[1].respondCode])
            else:
                data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, iRet])
                meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/CUP/BatchForCardNo", methods=['POST'])
@jwt_required
def BatchForCardNo():
    current_app.logger.debug(request.headers)
    current_app.logger.debug("BODY: %s" % request.get_data())
    username = request.header.get("username")
    f = request.files['file']
    filepath = os.path.join('Batch Process/', secure_filename(f.filename))
    f.save(filepath)
    xlsx = xlrd.open_workbook(filepath)
    table = xlsx.sheet_by_index(0)
    meta = {'status': 1, 'msg': "Failed"}
    data = []
    for i in range(table.nrows):
        current_app.logger.info(table.row_values(i))
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
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/A8_Password", methods=['GET'])
@jwt_required
def A8_Password():
    current_app.logger.debug(request.headers)
    # current_app.logger.debug("BODY: %s" % request.get_data())
    #http://10.17.2.238/password/
    meta = {}
    data = {}
    username = request.headers.get("username")
    url = 'http://10.17.2.238/password/'
    response = requests.get(url)
    temp = response.text.find('pw')
    password = str(response.text)
    password = password[temp+3:9+temp]
    trainingmodePW = '80' + password
    data = {"password": password, "trainingmodePW": trainingmodePW}
    meta = {'status': 200, 'msg': 'success'}
    returnmessage = {'meta': meta, 'data':data }
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

@app.route("/Octopus/Report/<action>", methods=['POST'])
@jwt_required
def Octopus_Report(action):
    current_app.logger.debug(request.headers)
    # current_app.logger.debug("BODY: %s" % request.get_data())
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
        current_app.logger.debug(returnmessage)
        return jsonify(returnmessage)
    elif action == 'Download_SPID':
        SPID = request.json.get("SPID")
        DateFrom = request.json.get("DateFrom")
        DateTo = request.json.get("DateTo")
        temp = Octopus.Report()
        result = temp.Download_SPID(SPID, DateFrom, DateTo)
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
        current_app.logger.debug(returnmessage)
        return jsonify(returnmessage)
    elif action == 'UploadRawData':
        current_app.logger.debug(request.files)
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
        current_app.logger.debug(returnmessage)
        return jsonify(returnmessage)

@app.route("/download/<string:filename>", methods=['GET'])
def download(filename):
    currentlyPath = os.getcwd()
    if (os.path.isfile(os.path.join(currentlyPath,filename))):
        return send_from_directory(currentlyPath,filename, as_attachment=True)
    pass

@app.route("/VMP/<TransactionType>", methods=['POST'])
@jwt_required
def VMP_Transaction(TransactionType):
    current_app.logger.debug(request.headers)
    current_app.logger.debug("JSON: %s" % request.json)
    username = request.headers.get("username")
    service = request.json.get('service')
    User_Confirm_Key = request.json.get('User_Confirm_Key')
    PaymentType = request.json.get('PaymentType')
    wallet = request.json.get('wallet')
    amount = request.json.get('amount')
    SecretCode = request.json.get('SecretCode')
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
    iRet = -1
    meta = {}
    data = {}
    signStr = ''
    RawRequest = None
    RawResponse = None
    errormessage = ''
    EOPG_req = None
    VMP_req = None
    if APIType == 'EOPG': #EOPG 接口
        if str(TransactionType).upper() == 'SALE':
            URL += '/VMP/eopg/ForexTradeRecetion'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.fee_type = fee_type
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            EOPG_req.trans_amount = amount
            signStr = VMP.packSignStr(EOPG_req,SecretCode)
            current_app.logger.debug(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.return_url = return_url
            EOPG_req.goods_subject = subject
            EOPG_req.goods_body = body
            EOPG_req.notify_url = notify_url
            EOPG_req.wallet = wallet
            EOPG_req.wechatWeb = wechatWeb
            EOPG_req.tid = tid
            EOPG_req.active_time = active_time
            EOPG_req.api_version = '2.9.5'
            EOPG_req.lang = lang
            EOPG_req.reuse = reuse
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
        elif str(TransactionType).upper() == 'REFUND':
            URL += '/VMP/eopg/ForexRefundRecetion'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.refund_amount = amount
            EOPG_req.refund_reason = refund_reason
            EOPG_req.return_url = return_url
            EOPG_req.service = service
            EOPG_req.trans_amount = amount
            signStr = VMP.packSignStr(EOPG_req, SecretCode)
            current_app.logger.debug(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.merch_refund_id = refund_no
            EOPG_req.api_version = '2.9.5'
            EOPG_req.redirect = redirect
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
        elif str(TransactionType).upper() == 'QUERY':
            URL += '/VMP/eopg/ForexCheckQuery'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            signStr = VMP.packSignStr(EOPG_req, SecretCode)
            current_app.logger.debug(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.api_version = '2.9.5'
            EOPG_req.redirect = redirect
            EOPG_req.return_url = return_url
            RawRequest = VMP.packGetMsg(EOPG_req, URL)
        elif str(TransactionType).upper() == 'QUERYREFUND':
            URL += '/VMP/eopg/ForexCheckRefund'
            EOPG_req = VMP.EOPG_Request()
            EOPG_req.merch_ref_no = out_trade_no
            EOPG_req.merch_refund_id = refund_no
            EOPG_req.mid = User_Confirm_Key
            EOPG_req.payment_type = PaymentType
            EOPG_req.service = service
            signStr = VMP.packSignStr(EOPG_req, SecretCode)
            current_app.logger.debug(signStr)
            EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            EOPG_req.api_version = '2.9.5'
            EOPG_req.redirect = redirect
            EOPG_req.return_url = return_url
            RawRequest = VMP.packGetMsg(EOPG_req, URL)

    elif APIType == 'WEB':
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.active_time = active_time
            VMP_req.body = body
            VMP_req.buyerType = buyerType
            VMP_req.fee_type = fee_type
            VMP_req.lang = lang
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            VMP_req.payType = PaymentType
            if service == 'service.wechat.oauth2.Authorize':
                VMP_req.pay_scene = 'WXWEB'
            elif service == 'service.alipay.wap.PreOrder':
                VMP_req.pay_scene = 'WAP'
            else:
                VMP_req.pay_scene = 'WEB'
            VMP_req.return_url = return_url
            VMP_req.service = service
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
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.buyerType = buyerType
            VMP_req.eft_trade_no = eft_trade_no
            VMP_req.out_refund_no = refund_no
            VMP_req.out_trade_no = out_trade_no
            VMP_req.payType = PaymentType
            VMP_req.pay_scene = 'WEB'
            VMP_req.reason = body
            VMP_req.return_amount = amount
            VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.total_fee = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            if str(PaymentType).upper() == 'ALIPAY':
                VMP_req.wallet = 'ALIPAY' + wallet
            elif str(PaymentType).upper() == 'WECHAT':
                VMP_req.wallet = 'WECHAT' + wallet
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
    elif APIType == 'JSAPI':
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
            VMP_req.service = service
            VMP_req.sub_openid = sub_openid
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.total_fee = amount
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
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
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
    elif APIType == 'QRCode':
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
            VMP_req.service = service
            VMP_req.subject = subject
            VMP_req.tid = tid
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.transaction_amount = amount
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
        elif str(TransactionType).upper() == 'QUERY':
            VMP_req = VMP.VMP_Request()
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
            VMP_req.querytype = 'OUT_TRADE'
            VMP_req.refund_no = refund_no
            VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
    elif APIType == 'APP':
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
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
            current_app.logger.debug('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
        elif str(TransactionType).upper() == 'REFUND':
            VMP_req = VMP.VMP_Request()
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
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass
    elif APIType == 'Cashier':
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
            current_app.logger.debug('signStr: {0}'.format(signStr))
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            VMP_req.service = service
            VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
            VMP_req.user_confirm_key = User_Confirm_Key
            signStr = VMP.packSignStr(VMP_req, SecretCode)
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
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
            current_app.logger.debug(signStr)
            VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
            RawRequest = json.dumps(VMP.packJsonMsg(VMP_req))
            current_app.logger.debug('Request Message: {0}'.format(RawRequest))
            pass

    if APIType == 'EOPG':
        if (str(TransactionType).upper()) != 'SALE':
            resp = Utility.GetToHost(RawRequest, timeout=30)
            if resp.status_code == 200:
                current_app.logger.debug(resp.text)
                RawResponse = dict(x.split('=') for x in resp.text.split('&'))
    else:
        resp = Utility.PostToHost(URL, RawRequest, timeout=30)
        if resp.status_code == 200:
            current_app.logger.debug(resp.text.encode("utf8"))
            RawResponse = json.loads(resp.text.encode("utf8"))

    data = {'RawRequest': RawRequest, 'RawResponse': RawResponse}
    meta = {'status': 0, 'msg': 'Success'}
    returnmessage = {'meta': meta, 'data': data}
    current_app.logger.debug(returnmessage)
    return jsonify(returnmessage)

if __name__ == '__main__':
    Config = Configuration.loadConfig()
    app.run(host='0.0.0.0', port=5000)
