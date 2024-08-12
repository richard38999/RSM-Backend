
from flask_jwt_extended import JWTManager, jwt_required
from flask import request, jsonify, json
import requests
from Logger import *
import datetime
from Utility import rsa_encrypt_data, local_to_utc
from werkzeug.utils import secure_filename
import Spiral.Spiral
log = Log('Flask')
# @app.route("/Spiral", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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
    utcTime = local_to_utc()
    log.info(f'utcTime: {utcTime}')
    Payload = clientId + merchantRef + utcTime
    log.info(f'Payload: {Payload}')
    currentlyPath = os.getcwd()
    cert_path = f'{currentlyPath}\\cert\\Spiral\\{privateKey}'
    if not os.path.exists(cert_path):
        meta = {'status': -1, 'msg': 'Certificate Not Exist'}
        returnmessage = {'meta': meta, 'data': data}
        return jsonify(returnmessage)
    Signature = str(rsa_encrypt_data(data=Payload, Key_path=cert_path))
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

# @app.route("/Spiral/Certificate/<action>", methods=['GET', 'POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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
