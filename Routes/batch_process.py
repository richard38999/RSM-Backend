from flask import request, jsonify, json
from Logger import *
from flask_jwt_extended import jwt_required
import datetime
from werkzeug.utils import secure_filename
from Utility import (getResultMessage, insert_Offline_Txn, convertToCardNo, check_offline_refund_txn,
                     check_vmp_refund_txn, PostToHost, insert_VMP_Txn, GetToHost)
import xlrd
import hashlib
import clr
from VMPHelper import VMP, Util, VMP_EOPG
clr.FindAssembly('DLL\\EFTPaymentsServer.dll')
clr.AddReference('DLL\\EFTPaymentsServer')
log = Log('Flask')
from EFTSolutions import *
# @app.route("/<Till_Number>/<BatchFor>/Upload", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def BatchFor(Till_Number, BatchFor):
    log.start('BatchFor')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    f = request.files['file']
    datetime_f = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filepath = os.path.join('Batch Process/', '{0}_'.format(datetime_f) + secure_filename(f.filename))
    f.save(filepath)
    URL = request.form['URL']
    IP = request.form['IP']
    Port = int(request.form['Port'])
    # return_url = request.form['return_url']
    TPDU = request.form['TPDU']
    COMMTYPE = request.form['COMMTYPE']
    if COMMTYPE == 'TLS':
        COMMTYPE = 2
    elif COMMTYPE == 'PlainText':
        COMMTYPE = 1
    COMMTYPE = int(COMMTYPE)
    Timeout = int(request.form['Timeout'])
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
                User_Confirm_Key = str(table.cell_value(i, 0)).replace(' ', '').strip()
                SecretCode = str(table.cell_value(i, 1)).replace(' ', '').strip()
                if table.cell(i, 2).ctype == 2:
                    amount = str(round(float(table.cell_value(i, 2)),2)).strip()
                else:
                    amount = str(round(float(table.cell_value(i, 2)), 2)).strip()
                # amount = str(table.cell_value(i, 2)).replace(' ', '')
                APIType = str(table.cell_value(i, 3)).replace(' ', '').upper().strip()
                PaymentType = str(table.cell_value(i, 4)).replace(' ', '').upper().strip()
                out_trade_no = str(table.cell_value(i, 5)).strip()
                eft_trade_no = str(table.cell_value(i, 6)).strip()
                Email_Subject = str(table.cell_value(i, 7))
                Remark = str(table.cell_value(i, 8))
                if Remark == '' or Remark == None:
                    Remark = 'Refund on ' + time.strftime("%d %b %Y", time.localtime())
                URL = request.form['URL']
                if APIType.upper() == 'WEB':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    VMP_req.out_trade_no = out_trade_no
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.payType = 'Alipay'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.payType = 'WeChat'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.payType = 'ATOME'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.payType = 'UnionPay'
                    elif str(PaymentType).upper() == 'BOCPAY':
                        VMP_req.payType = 'BOCPay'
                    elif str(PaymentType).upper() == 'JETCO':
                        VMP_req.payType = 'Jetco'
                    elif str(PaymentType).upper() == 'OCT':
                        VMP_req.payType = 'OCT'
                    elif str(PaymentType).upper() == 'MPGS':
                        VMP_req.payType = 'Mpgs'
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
                    elif str(PaymentType).upper() == 'BOCPAY':
                        VMP_req.service = 'service.bocpayupi.wap.Refund'
                    elif str(PaymentType).upper() == 'JETCO':
                        VMP_req.service = 'service.jetco.wap.Refund'
                    elif str(PaymentType).upper() == 'OCT':
                        VMP_req.service = 'service.oct.online.Refund'
                    elif str(PaymentType).upper() == 'MPGS':
                        VMP_req.service = 'service.mpgs.web.Refund'
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
                    elif str(PaymentType).upper() == 'BOCPAY':
                        VMP_req.wallet = 'BOCPAYUPI'
                    elif str(PaymentType).upper() == 'JETCO':
                        VMP_req.wallet = 'JETCOHK'
                    elif str(PaymentType).upper() == 'OCT':
                        VMP_req.wallet = 'OCT'
                    elif str(PaymentType).upper() == 'MPGS':
                        VMP_req.wallet = 'MPGS'
                    signStr = Util.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(Util.packJsonMsg(VMP_req))
                    pass
                elif APIType.upper() == 'EOPG':
                    return_url = URL + f'/{Till_Number}/EOPG/eopg_return_addr'
                    URL += f'/{Till_Number}/eopg/ForexRefundRecetion'
                    EOPG_req = VMP_EOPG.EOPG_Request()
                    EOPG_req.merch_ref_no = out_trade_no
                    EOPG_req.mid = User_Confirm_Key
                    EOPG_req.payment_type = PaymentType
                    EOPG_req.refund_amount = amount
                    EOPG_req.refund_reason = 'Refund'
                    EOPG_req.return_url = ''
                    EOPG_req.service = 'REFUND'
                    EOPG_req.trans_amount = amount
                    signStr = Util.packSignStr_EOPG(EOPG_req, SecretCode)
                    log.info(signStr)
                    EOPG_req.signature = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    EOPG_req.merch_refund_id = 'Refund_' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                    EOPG_req.api_version = '2.9'
                    EOPG_req.redirect = 'N'
                    EOPG_req.balance_ignore = 'N'
                    RawRequest = Util.packGetMsg(EOPG_req, URL)
                elif APIType.upper() == 'JSAPI':
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
                    VMP_req.refund_no = 'Refund_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.service = 'service.alipay.jsapi.Refund'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.service = 'service.wechat.jsapi.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.total_fee = amount
                    VMP_req.transaction_amount = amount
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = Util.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(Util.packJsonMsg(VMP_req))
                    pass
                elif APIType.upper() == 'APP':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'AppTradeRefund.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    VMP_req.out_trade_no = out_trade_no
                    VMP_req.reason = 'Refund'
                    VMP_req.return_amount = amount
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = Util.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(Util.packJsonMsg(VMP_req))
                    pass
                elif APIType.upper() == 'QRCODE':
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
                        VMP_req.paytype = 'UnionPay'
                    VMP_req.refund_no = 'Refund_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    if str(PaymentType).upper() == 'ALIPAY':
                        VMP_req.service = 'service.alipay.qrcode.Refund'
                    elif str(PaymentType).upper() == 'WECHAT':
                        VMP_req.service = 'service.wechat.qrcode.Refund'
                    elif str(PaymentType).upper() == 'ATOME':
                        VMP_req.service = 'service.atome.v1.qrcode.Refund'
                    elif str(PaymentType).upper() == 'UNIONPAY':
                        VMP_req.service = 'service.unionpay.qrcode.csb.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.transaction_amount = amount
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = Util.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(Util.packJsonMsg(VMP_req))
                    pass
                elif APIType.upper() == 'CASHIER':
                    URL += f'/{Till_Number}/Servlet/'
                    VMP_req = VMP.VMP_Request()
                    URL = URL + 'JSAPIService.do'
                    VMP_req.buyerType = 'other'
                    VMP_req.eft_trade_no = eft_trade_no
                    VMP_req.out_refund_no = 'Refund_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    VMP_req.out_trade_no = out_trade_no
                    VMP_req.pay_scene = 'WAP'
                    VMP_req.reason = 'Refund'
                    VMP_req.return_amount = amount
                    VMP_req.service = 'service.united.wap.Refund'
                    VMP_req.time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                    VMP_req.user_confirm_key = User_Confirm_Key
                    signStr = Util.packSignStr(VMP_req, SecretCode)
                    log.info(signStr)
                    VMP_req.sign = hashlib.sha256(signStr.encode('utf-8')).hexdigest()
                    RawRequest = json.dumps(Util.packJsonMsg(VMP_req))
                    pass
                Refund_Result = check_vmp_refund_txn(GateName=Till_Number, user_confirm_key=User_Confirm_Key,
                                                             out_trade_no=out_trade_no, eft_trade_no=eft_trade_no)
                if Refund_Result != []:
                    data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, f'This transaction already did the refund by "{Refund_Result[0][1]}" on {Refund_Result[0][0]}. Not allow to use Batch Refund. Please use manual refund!', Refund_Result[0][13], Refund_Result[0][14]])
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                    continue
                log.info(f'URL: {URL}')
                log.info(f'RawRequest: {RawRequest}')
                resp = PostToHost(URL, RawRequest, timeout=30)
                if resp.status_code == 200:
                    log.info('RawResponse: {0}'.format(resp.text.encode("utf8")))
                    RawResponse = json.loads(resp.text.encode("utf8"))
                    if RawResponse['return_status'] == '00':
                        data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, RawResponse['return_status'], Email_Subject, Remark])
                    else:
                        meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                        data.append([User_Confirm_Key, SecretCode, amount, APIType, PaymentType, out_trade_no, eft_trade_no, f"{RawResponse['return_status']}[{RawResponse['return_char']}]", Email_Subject, Remark])
                    insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Till_Number, API_Type=APIType,
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
                    MID = str(int(float(table.cell_value(i, 0)))).strip()
                else:
                    MID = str(table.cell_value(i, 0)).strip()
                if table.cell(i, 1).ctype == 2:
                    TID = str(int(float(table.cell_value(i, 1)))).strip()
                else:
                    TID = str(table.cell_value(i, 1)).strip()
                if table.cell(i, 2).ctype == 2:
                    Amount = str(int(round(float(table.cell_value(i, 2) * 100),2))).strip()
                else:
                    Amount = str(int(round(float(table.cell_value(i, 2)) * 100, 2))).strip()
                if table.cell(i, 3).ctype == 2:
                    RRN = str(int(float(table.cell_value(i, 3)))).strip()
                else:
                    RRN = str(table.cell_value(i, 3)).strip()

                if Till_Number == 'CUP' or Till_Number == 'BOC':
                    if table.cell(i, 4).ctype == 2:
                        ApprovalCode = str(int(float(table.cell_value(i, 4)))).strip()
                    else:
                        ApprovalCode = str(table.cell_value(i, 4)).strip()
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
                Refund_Result = check_offline_refund_txn(GateName=Till_Number, MID=MID, RRN=RRN)
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
                iRet = eft.refund(RRN, int(Amount), ecrRefNo, ApprovalCode)
                if iRet == 0:
                    iRet = eft.getSaleResponse(Transaction_resp)
                    if iRet[0] == 0:
                        insert_Offline_Txn(DateTime=nowdatetime,username=username, GatewayName=Till_Number,MID=MID, TID=TID, TransactionType='REFUND', Amount=Amount, RRN=RRN, approvalCode=ApprovalCode, respondCode=iRet[1].respondCode, respondText=iRet[1].respondText,Email_Subject=Email_Subject, Remark=Remark)
                        if iRet[1].respondCode != '00':
                            meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
                        if Till_Number == 'CUP' or Till_Number == 'BOC':
                            data.append([MID, TID, round(float(int(Amount)/100),2), RRN, ApprovalCode, f'{iRet[1].respondCode}[{iRet[1].respondText}]', Email_Subject, Remark])
                        else:
                            data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, f'{iRet[1].respondCode}[{iRet[1].respondText}]', Email_Subject, Remark])
                else:
                    if Till_Number == 'CUP' or Till_Number == 'BOC':
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN, ApprovalCode, f'{iRet}[{getResultMessage(iRet)}]', Email_Subject, Remark])
                    else:
                        data.append([MID, TID, round(float(int(Amount) / 100), 2), RRN,
                                     f'{iRet}[{getResultMessage(iRet)}]', Email_Subject, Remark])
                    meta = {'status': 1, 'msg': "Some Transactions Refund Failed"}
    os.remove(filepath)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('BatchFor')
    return jsonify(returnmessage)

# @app.route("/CUP/BatchForCardNo", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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
        rowData.append(convertToCardNo(table.cell_value(i,18)))
        data.append(rowData)
    meta = {'status': 0, 'msg': "Success"}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('BatchForCardNo')
    return jsonify(returnmessage)