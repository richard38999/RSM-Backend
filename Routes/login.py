from Logger import *
import datetime
from flask import request, jsonify
from Utility import get_login_account, update_lastlogindatetime
from flask_jwt_extended import create_access_token
import Configuration
ENVIRONMENT = 'DEV'
# ENVIRONMENT = 'PROD'
Config = Configuration.Flask_Config.get(ENVIRONMENT)
log = Log('Flask')
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
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
    login_account = get_login_account()
    if Config.FrontEndVersion == FrontEndVersion:
        for i in login_account:
            if i[1] == username:
                if i[2] == password:
                    if i[4] == 1:
                        access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(minutes=60*12))
                        meta = {'status': 'SUCCESS', 'msg': 'LOGIN SUCCESS'}
                        data = {'username': username, 'password': password, 'token': access_token}
                        nowdatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        update_lastlogindatetime(nowdatetime,username)
                    else:
                        meta = {'status': 'Failed', 'msg': 'Account Status was closed'}
                        data = {'username': username}
                else:
                    meta = {'status': 'Failed', 'msg': 'PASSWORD NOT MATCH'}
                    data = {'username': username}
                break
    else:
        meta = {'status': 'Failed', 'msg': 'Version Not Updated, please press F5 to refresh browser'}
        data = {'username': username}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('login')
    return jsonify(returnmessage)