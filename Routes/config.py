from flask import request, jsonify, send_file
from Logger import *
from flask_jwt_extended import jwt_required
from zipfile import ZipFile
from werkzeug.utils import secure_filename
from Utility import (deleteconfig, setconfig_Spiral,
                     setconfig_VMP, loadconfig, setconfig_Offline)
log = Log('Flask')

# @app.route("/setconfig/<Till_Number>/<TransactionType>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def set_config(Till_Number,TransactionType):
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
    app_link = request.json.get('app_link')
    browser = request.json.get('browser')
    pay_scene = request.json.get('pay_scene')
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
        meta = setconfig_VMP(username=username, Tag=Tag, User_Confirm_Key=User_Confirm_Key,
                                     SecretCode=SecretCode, Amount=Amount, Service=Service, out_trade_no=out_trade_no, TransactionType=TransactionType,
                                     PaymentType=PaymentType, eft_trade_no=eft_trade_no, refund_no=refund_no, Wallet=Wallet, APIType=APIType,
                                     Gateway_Name=Gateway_Name, buyerType=buyerType, subject=subject, body=body, fee_type=fee_type, tid=tid,
                                     scene_type=scene_type, openid=openid, sub_openid=sub_openid, wechatWeb=wechatWeb, active_time=active_time, URL=URL, notify_url=notify_url,
                                     return_url=return_url, app_pay=app_pay, lang=lang, goods_body=goods_body, goods_subject=goods_subject,
                                     reuse=reuse, redirect=redirect, refund_reason=refund_reason, reason=reason, mobileNumber=mobileNumber,
                                     fullName=fullName, shippingAddress_countryCode=shippingAddress_countryCode, shippingAddress_postCode=shippingAddress_postCode, shippingAddress_lines=shippingAddress_lines, billingAddress_countryCode=billingAddress_countryCode, billingAddress_postCode=billingAddress_postCode, billingAddress_lines=billingAddress_lines,
                                     browser=browser, app_link=app_link, pay_scene=pay_scene)
    elif Till_Number == 'SpiralHelper':
        meta = setconfig_Spiral(username=username,Tag=Tag, clientId=clientId, merchantRef=merchantRef, cmd=cmd, amount=amount, type=type, goodsName=goodsName, Flow=Flow, orderId=orderId, URL=URL, goodsDesc=goodsDesc, channel=channel, cardToken=cardToken, cardTokenSrc=cardTokenSrc, successUrl=successUrl, failureUrl=failureUrl, webhookUrl=webhookUrl, duration=duration, durationHr=durationHr, privateKey=privateKey, publicKey=publicKey, JavaScriptLibrary=JavaScriptLibrary, locale=locale)
    else:
        meta = setconfig_Offline(username=username,Gateway_Name=Till_Number, Tag=Tag, MID=MID, TID=TID, TransactionType=TransactionType, PaymentType=PayType, amount=amount, barcode=barcode, ApprovalCode=ApprovalCode, RRN=RRN, TraceNo=TraceNo, OriTID=OriTID, URL=URL, IP=IP, Port=Port, TPDU=TPDU, Timeout=Timeout, MsgType=MsgType, COMMTYPE=COMMTYPE)
    returnmessage = {'meta': meta, 'data': data}
    return jsonify(returnmessage)

# @app.route("/loadconfig/<Till_Number>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def load_config(Till_Number):
    log.start('loadconfig')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    iRet = -1
    data = loadconfig(username=username,Gateway_Name=Till_Number)
    meta = {'status': 0, 'msg': 'Success'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    return jsonify(returnmessage)

# @app.route("/deleteconfig/<Till_Number>/<Tag>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def delete_config(Till_Number, Tag):
    log.start('deleteconfig')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    iRet = -1
    data = {}
    meta = deleteconfig(username=username,Gateway_Name=Till_Number, Tag=Tag)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    return jsonify(returnmessage)
