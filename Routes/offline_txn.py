from flask import request, jsonify, send_file
from Logger import *
from flask_jwt_extended import jwt_required
import clr
from Utility import (check_offline_refund_txn, getTransactionRecord,
                     insert_Offline_Txn, getResultMessage,
                     SQL_script, getXmlResp)
import datetime
clr.FindAssembly('DLL\\EFTPaymentsServer.dll')
clr.AddReference('DLL\\EFTPaymentsServer')
clr.FindAssembly('DLL\\XML_InterFace.dll')
clr.AddReference('DLL\\XML_InterFace')
from EFTSolutions import EFTPaymentsServer, TransactionRecord
from XML_InterFace import *

log = Log('Flask')
# @app.route("/<Till_Number>/<TransactionType>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def offline_Transaction(Till_Number, TransactionType):
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
    if ApprovalCode == None:
        ApprovalCode = ''
    # TransactionType = request.json.get('TransactionType')
    RRN = request.json.get('RRN')
    Refund_RRN = request.json.get('Refund_RRN')
    IP = request.json.get('IP')
    Port = int(request.json.get('Port'))
    TPDU = request.json.get('TPDU')
    COMMTYPE = request.json.get('COMMTYPE')
    if COMMTYPE == 'TLS':
        COMMTYPE = 2
    elif COMMTYPE == 'PlainText':
        COMMTYPE = 1
    Timeout = int(request.json.get('Timeout'))
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
            Refund_Result = check_offline_refund_txn(GateName=Till_Number, MID=MID, TID=TID, RRN=RRN)
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
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'VOID':
            iRet = eft.voidSale(amount, barcode, TraceNo)
            if iRet == 0:
                iRet = eft.getVoidSaleResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'QUERY':
            iRet = eft.query(RRN, ApprovalCode)
            if iRet == 0:
                iRet = eft.getQueryResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
        elif TransactionType == 'QUERY_REFUND':
            iRet = eft.query_refund(RRN, ApprovalCode, TraceNo)
            if iRet == 0:
                iRet = eft.getQueryRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
        elif TransactionType == 'REFUND':
            iRet = eft.refund(RRN, amount, ecrRefNo, ApprovalCode)
            if iRet == 0:
                iRet = eft.getRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'SALEADVICE':
            iRet = eft.SaleAdvice(RRN, ecrRefNo, amount, ApprovalCode)
            if iRet == 0:
                iRet = eft.getSaleAdviceResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'REVERSAL':
            iRet = eft.Reversal(RRN, barcode, amount, TraceNo)
            if iRet == 0:
                iRet = eft.getReversalResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'AUTH':
            iRet = eft.AUTH(amount)
            if iRet == 0:
                iRet = eft.getAUTHResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'], approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=None,
                                           respondCode=iRet, respondText=meta['msg'], Email_Subject=Email_Subject, Remark=Remark)
        elif TransactionType == 'ADMINREFUND':
            iRet = eft.adminRefund(RRN, OriTID, amount, ecrRefNo)
            if iRet == 0:
                iRet = eft.getRefundResponse(Transaction_resp)
                if iRet[0] == 0:
                    meta = {'status': str(iRet[0]), 'msg': getResultMessage(str(iRet[0]))}
                    data = getTransactionRecord(iRet[1])
                    insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=OriTID, TransactionType=TransactionType, Amount=amount, RRN=RRN, approvalCode=data['approvalCode'], respondCode=data['respondCode'], respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                meta = {'status': iRet, 'msg': getResultMessage(str(iRet))}
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
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
        elif TransactionType == 'QUERY_REFUND':
            iRet = XML.QUERY_REFUND(RRN, ApprovalCode, TraceNo)
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
        elif TransactionType == 'GET_TOTAL':
            iRet = XML.GET_TOTAL()
        elif TransactionType == 'TWO_SETTLE':
            iRet = XML.TWO_SETTLE()

        if iRet == True:  # 成功
            iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
            meta = {'status': '0', 'msg': 'Success'}
            data = getXmlResp(iRet[1], iRet[2], iRet[3])
            if TransactionType == 'REFUND':
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                           respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)
            elif TransactionType == 'ADMINREFUND':
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                           TID=OriTID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                           approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                           respondText=data['respondText'],Email_Subject=Email_Subject, Remark=Remark)
            else:
                insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                   TID=TID, TransactionType=TransactionType, Amount=amount, RRN=data['RRN'],
                                   approvalCode=data['approvalCode'], respondCode=data['respondCode'],
                                   respondText=data['respondText'], Email_Subject=Email_Subject, Remark=Remark)

        else:  # 失败
            status = iRet
            iRet = XML.GetResponse(XML_resp, RawRequest, RawResponse, errormessage)
            msg = iRet[4]
            meta = {'status': status, 'msg': msg}
            insert_Offline_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, MID=MID,
                                       TID=TID, TransactionType=TransactionType, Amount=amount, RRN=RRN,
                                       approvalCode=None,
                                       respondCode=None, respondText=meta['msg'])

    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('Transaction')
    return jsonify(returnmessage)

# @app.route("/Offline_Refund/<action>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Offline_Refund(action):
    log.start('Offline_Refund')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    MID = request.json.get('MID')
    TID = request.json.get('TID')
    PayType = request.json.get('PayType')
    amount = request.json.get('amount')
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
    # Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
    iRet = -1
    msg = ''
    meta = {}
    data = []
    RawRequest = ''
    RawResponse = ''
    errormessage = ''
    nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    confirm_Refund_Request = request.json.get('confirm_Refund_Request')
    BatchNo = '#' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    # check refund record

    if action == 'Refund_Request':
        if confirm_Refund_Request != 'Y':
            Refund_Result = check_offline_refund_txn(GateName=PayType, MID=MID, TID=TID, RRN=RRN, check_ResponseCode=False)
            if Refund_Result != []:
                for i in range(len(Refund_Result)):
                    data.append({'ID': i, 'DateTime': Refund_Result[i][0], 'UserName': Refund_Result[i][1],
                                 'MID': Refund_Result[i][3], 'TID': Refund_Result[i][4],
                                 'Amount': Refund_Result[i][6], 'RRN': Refund_Result[i][7],
                                 'ResponseCode': f'{Refund_Result[i][9]}({Refund_Result[i][10]})',
                                 'Email_Subject': Refund_Result[i][11], 'Remark': Refund_Result[i][12],
                                'Requested_by': Refund_Result[i][13], 'Approved_by': Refund_Result[i][14],
                                'Requested_time': Refund_Result[i][15], 'Approved_time': Refund_Result[i][16],
                                 'Approved_status': Refund_Result[i][17], 'BatchNo': Refund_Result[i][18]})
                meta = {'status': 'confirm_Refund_Request', 'msg': msg}
                returnmessage = {'meta': meta, 'data': data}
                log.info(returnmessage)
                log.end('Offline_Refund')
                return jsonify(returnmessage)
        insert_Offline_Txn(DateTime=nowdatetime,
                                   username=username,
                                   GatewayName=PayType,
                                   MID=MID, TID=TID,
                                   TransactionType='REFUND',
                                   Amount=amount, RRN=RRN,
                                   Email_Subject=Email_Subject, Remark=Remark,
                                   Requested_by=username,
                                   Requested_time=nowdatetime,
                                   Approved_status='Pending',
                                   BatchNo=BatchNo)
        meta = {'status': 0, 'msg': 'Request Refund Success, Wait for Supervisor review and approve'}
        data = {'BatchNo': BatchNo}
    elif action == 'send_notify_email':
        result = SQL_script(f'select * FROM Offline_Txn_DB where BatchNo="{BatchNo}";')
        email_content = ''
        for i in result:
            pass

    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('Offline_Refund')
    return jsonify(returnmessage)