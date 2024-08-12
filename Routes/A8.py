import requests
from flask import request, jsonify
from Logger import *
from flask_jwt_extended import jwt_required
log = Log('Flask')

# @app.route("/A8_Password", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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