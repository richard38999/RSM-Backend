from flask import request, jsonify, json
from Logger import *
from flask_jwt_extended import jwt_required
from Utility import check_vmp_refund_txn, PostToHost, insert_VMP_Txn, GetToHost
import hashlib
import VMP
log = Log('Flask')
# @app.route("/VMP/<Gateway>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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
    app_link = request.json.get('app_link')
    browser = request.json.get('browser')
    pay_scene = request.json.get('pay_scene')
    scheme = request.json.get('scheme')
    packageName = request.json.get('packageName')
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
            Refund_Result = check_vmp_refund_txn(GateName=Gateway, user_confirm_key=User_Confirm_Key, out_trade_no=out_trade_no, eft_trade_no=eft_trade_no)
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
            return_url = f'{URL}/{Gateway}/returnSuccess'
        URL += f'/{Gateway}/Servlet/'
        if str(TransactionType).upper() == 'SALE':
            VMP_req = VMP.VMP_Request()
            URL = URL + 'JSAPIService.do'
            VMP_req.active_time = active_time
            VMP_req.app_link = app_link
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.billingAddress = str(billingAddress)
            VMP_req.body = body
            VMP_req.browser = browser
            VMP_req.buyerType = buyerType
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.customerInfo = str(customerInfo)
            VMP_req.fee_type = fee_type
            if str(PaymentType).upper() == 'ATOME':
                VMP_req.items = str(items)
            VMP_req.lang = lang
            VMP_req.notify_url = notify_url
            VMP_req.out_trade_no = out_trade_no
            VMP_req.packageName = packageName
            VMP_req.payType = PaymentType
            if pay_scene == None:
                if service == 'service.wechat.oauth2.Authorize':
                    VMP_req.pay_scene = 'WXWEB'
                elif service == 'service.alipay.wap.PreOrder':
                    VMP_req.pay_scene = 'WAP'
                elif service == 'service.unionpay.online.web.PreOrder':
                    VMP_req.pay_scene = 'ONLINE_WEB'
                elif service == 'service.jetco.wap.PreOrder':
                    VMP_req.pay_scene = 'WAP'
                elif service == 'service.bocpayupi.wap.PreOrder':
                    VMP_req.pay_scene = 'APP'
                else:
                    VMP_req.pay_scene = 'WEB'
            else:
                VMP_req.pay_scene = pay_scene
            VMP_req.return_url = return_url
            VMP_req.scheme = scheme
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
            else:
                VMP_req.wallet = wallet

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
            VMP_req.packageName = packageName
            VMP_req.payType = PaymentType
            if pay_scene == None:
                if service == 'service.alipay.wap.Refund':
                    VMP_req.pay_scene = 'WAP'
                elif service == 'service.unionpay.online.web.Refund':
                    VMP_req.pay_scene = 'ONLINE_WEB'
                elif service == 'service.jetco.wap.Refund':
                    VMP_req.pay_scene = 'WAP'
                elif service == 'service.bocpayupi.wap.Refund':
                    VMP_req.pay_scene = 'APP'
                else:
                    VMP_req.pay_scene = 'WEB'
            else:
                VMP_req.pay_scene = pay_scene
            VMP_req.reason = body
            VMP_req.return_amount = amount
            VMP_req.scheme = scheme
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
            elif str(PaymentType).upper() == 'BOCPAY':
                VMP_req.wallet = 'BOCPAYUPI'
            elif str(PaymentType).upper() == 'JETCO':
                VMP_req.wallet = 'JETCOHK'
            elif str(PaymentType).upper() == 'OCT':
                VMP_req.wallet = 'OCT'
            elif str(PaymentType).upper() == 'MPGS':
                VMP_req.wallet = 'MPGS'
            elif str(PaymentType).upper() == 'AE':
                VMP_req.wallet = 'AE'
            elif str(PaymentType).upper() == 'NUVEI':
                VMP_req.wallet = 'NUVEI'
            elif str(PaymentType).upper() == 'PAYME':
                VMP_req.wallet = 'PAYME'
            elif str(PaymentType).upper() == 'BOCVMP':
                VMP_req.wallet = 'BOCVMPUPW'
            elif str(PaymentType).upper() == 'FDMS':
                VMP_req.wallet = 'FDMS'
            elif str(PaymentType).upper() == 'ICBC':
                VMP_req.wallet = 'ICBCWAP'
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
            return_url = f'{URL}/{Gateway}/returnSuccess'
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
            return_url = f'{URL}/{Gateway}/returnSuccess'
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
                VMP_req.payment_type = PaymentType.upper()
                VMP_req.paytype = PaymentType
                # VMP_req.pay_scene = 'QRCODE'
            elif str(PaymentType).upper() == 'GBPAY':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ECNY':
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
                VMP_req.payment_type = PaymentType.upper()
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ECNY':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType

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
                VMP_req.payment_type = 'UNIONPAY'
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'GBPAY':
                VMP_req.payment_type = 'GBPAY'
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'ECNY':
                VMP_req.payment_type = PaymentType
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
                VMP_req.paytype = PaymentType
                VMP_req.payment_type = PaymentType
            elif str(PaymentType).upper() == 'ECNY':
                VMP_req.payment_type = PaymentType
                VMP_req.paytype = PaymentType

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
        elif str(TransactionType).upper() == 'CLOSE':
            VMP_req = VMP.VMP_Request()
            # if NewInterFace:
            #     URL = URL + 'CommonTradeQuery.do'
            # else:
            #     URL = URL + 'JSAPIService.do'
            URL = URL + 'JSAPIService.do'
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
                VMP_req.payment_type = 'UNIONPAY'
                VMP_req.paytype = PaymentType
            elif str(PaymentType).upper() == 'GBPAY':
                VMP_req.payment_type = 'GBPAY'
                VMP_req.paytype = PaymentType
            if NewInterFace and str(PaymentType).upper() == 'ALIPAY':
                VMP_req.service = 'service.alipayplus.qrcode.Close'
            else:
                VMP_req.service = service

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
            return_url = f'{URL}/{Gateway}/returnSuccess'
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
    log.info('URL: {0}'.format(URL))
    if APIType == 'EOPG':
        if (str(TransactionType).upper()) != 'SALE':
            resp = GetToHost(RawRequest, timeout=30)
            if resp.status_code == 200:
                log.info('RawResponse: {0}'.format(resp.text))
                RawResponse = str(resp.text)
                JSONMessage = dict(x.split('=') for x in resp.text.split('&'))
                insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Gateway, API_Type=APIType,
                                       PaymentType=PaymentType, TransType=str(TransactionType).upper(), Amount=amount,
                                       user_confirm_key=User_Confirm_Key,
                                       Secret_Code=SecretCode, out_trade_no=out_trade_no, eft_trade_no=eft_trade_no,
                                       Response_Code=JSONMessage['return_status'],
                                       Response_Text=JSONMessage['return_char'], Email_Subject=Email_Subject,
                                       Remark=Remark)
    else:
        resp = PostToHost(URL, RawRequest, timeout=30)
        if resp.status_code == 200:
            log.info('RawResponse: {0}'.format(resp.text.encode("utf8")))
            RawResponse = json.loads(resp.text.encode("utf8"))
            insert_VMP_Txn(DateTime=nowdatetime, username=username, GatewayName=Gateway, API_Type=APIType,
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