import decorator
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import Configuration
from Logger import *
import time
from Routes.login import login
from Routes.user import ChangePassword
from Routes.user import userView
from Routes.user import menus
from Routes.user import userlist
from Routes.user import updateuserstatus
from Routes.user import deleteUser
from Routes.spiral import Spiral_Transaction
from Routes.spiral import Spiral_Certificate
from Routes.A8 import A8_Password
from Routes.server import Server_Managment
from Routes.batch_process import BatchFor
from Routes.batch_process import BatchForCardNo
from Routes.vmp import VMP_Transaction
from Routes.octopus import Octopus_Report
from Routes.paob import PAOB_Report
from Routes.offline_txn import offline_Transaction
from Routes.offline_txn import Offline_Refund
from Routes.config import set_config
from Routes.config import load_config
from Routes.config import delete_config

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

CORS(app, supports_credentials=True)

# def after_request(resp):
#     resp.headers['Access-Control-Allow-Origin'] = '*'
#     resp.headers['Access-Control-Allow-Headers'] = '*'
#     resp.headers['Access-Control-Allow-Credentials'] = True
#     resp.headers['Access-Control-Allow-Methods'] = 'HEAD, OPTIONS, GET, POST, DELETE, PUT'
#     return resp
#
# app.after_request(after_request)

app.add_url_rule('/login',
                 view_func=login,
                 methods=['POST'])
app.add_url_rule('/ChangePassword',
                 view_func=ChangePassword,
                 methods=['POST'])
app.add_url_rule('/userView',
                 view_func=userView,
                 methods=['GET'])
app.add_url_rule('/menus',
                 view_func=menus,
                 methods=['GET'])
app.add_url_rule('/userlist',
                 view_func=userlist,
                 methods=['GET'])
app.add_url_rule('/updateuserstatus',
                 view_func=updateuserstatus,
                 methods=['GET'])
app.add_url_rule('/deleteUser',
                 view_func=deleteUser,
                 methods=['GET'])
app.add_url_rule('/ChangePassword',
                 view_func=ChangePassword,
                 methods=['POST'])
app.add_url_rule('/Spiral',
                 view_func=Spiral_Transaction,
                 methods=['POST'])
app.add_url_rule('/Spiral/Certificate/<action>',
                 view_func=Spiral_Certificate,
                 methods=['POST'])
app.add_url_rule('/A8_Password',
                 view_func=A8_Password,
                 methods=['GET'])
app.add_url_rule('/Server_Management/<action>',
                 view_func=Server_Managment,
                 methods=['GET'])
app.add_url_rule('/<Till_Number>/<BatchFor>/Upload',
                 view_func=BatchFor,
                 methods=['POST'])
app.add_url_rule('/CUP/BatchForCardNo',
                 view_func=BatchForCardNo,
                 methods=['POST'])
app.add_url_rule('/VMP/<Gateway>',
                 view_func=VMP_Transaction,
                 methods=['POST'])
app.add_url_rule('/Octopus/Report/<action>',
                 view_func=Octopus_Report,
                 methods=['POST'])
app.add_url_rule('/PAOB/Report/<action>',
                 view_func=PAOB_Report,
                 methods=['POST'])
app.add_url_rule('/<Till_Number>/<TransactionType>',
                 view_func=offline_Transaction,
                 methods=['POST'])
app.add_url_rule('/Offline_Refund/<action>',
                 view_func=Offline_Refund,
                 methods=['POST'])
app.add_url_rule('/setconfig/<Till_Number>/<TransactionType>',
                 view_func=set_config,
                 methods=['POST'])
app.add_url_rule('/loadconfig/<Till_Number>',
                 view_func=load_config,
                 methods=['POST'])
app.add_url_rule('/deleteconfig/<Till_Number>/<Tag>',
                 view_func=delete_config,
                 methods=['POST'])

if __name__ == '__main__':
    log.start('Flask')
    app.run(host='0.0.0.0', port=5000)
    log.end('Flask')
