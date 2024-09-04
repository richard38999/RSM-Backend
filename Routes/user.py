from flask import request, jsonify
from flask_jwt_extended import jwt_required
from Logger import *
from Utility import get_Menu, UpdatePassword, update_AccountStatus, userView, get_userlist, delete_Account
log = Log('Flask')

# @app.route("/ChangePassword", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def ChangePassword():
    log.start('ChangePassword')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.json.get("username")
    oldpassword = request.json.get("oldpassword")
    newpassword = request.json.get("newpassword")
    meta = {'status': 'Failed', 'msg': 'Password Not Match'}
    data = {}
    meta = UpdatePassword(username, oldpassword,newpassword)
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('ChangePassword')
    return jsonify(returnmessage)

# @app.route("/userView", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def userView():
    log.start('userView')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    viewUser = request.args.get("username")
    data = userView(viewUser)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('userView')
    return jsonify(returnmessage)

# @app.route("/menus", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def menus():
    log.start('menu')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    menuUser = request.args.get("username")
    data = get_Menu(menuUser)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('menu')
    return jsonify(returnmessage)

# @app.route("/userlist", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def userlist():
    log.start('userlist')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    pagenum = request.args.get('pagenum')
    pagesize = request.args.get('pagesize')
    data = get_userlist(int(pagenum), int(pagesize))
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('userlist')
    return jsonify(returnmessage)

# @app.route("/updateuserstatus", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def updateuserstatus():
    log.start('updateuserstatus')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    updateUsername = request.args.get('username')
    status = request.args.get('status')
    data = update_AccountStatus(updateUsername, status)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('updateuserstatus')
    return jsonify(returnmessage)

# @app.route("/deleteUser", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def deleteUser():
    log.start('deleteUser')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    deleteUsername = request.args.get('username')
    status = request.args.get('status')
    data = delete_Account(deleteUsername)
    meta = {'status': 200, 'msg': 'SUCCESS'}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    log.end('deleteUser')
    return jsonify(returnmessage)
