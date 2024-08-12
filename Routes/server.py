from flask import request, jsonify, send_file
from Logger import *
from flask_jwt_extended import jwt_required
log = Log('Flask')
# @app.route("/Server_Management/<action>", methods=['GET'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Server_Managment(action):
    log.start('Server_Management')
    log.info(request.headers)
    log.info("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    iRet = -1
    data = {}
    meta = {}
    File_Name = request.args.get('File_Name')
    Existing_File_Name = request.args.get('Existing_File_Name')
    New_File_Name = request.args.get('New_File_Name')
    Current_Path = request.args.get('Current_Path')
    if Current_Path == '' or Current_Path == None:
        Current_Path = os.getcwd()
    Current_Path_FilesList = []
    if action == 'getFileslist':
        # Current_Path_FilesList = os.listdir(Current_Path)
        for file in os.scandir(Current_Path):
            Current_Path_FilesList.append({'file_name': file.name, 'is_dir': file.is_dir(), 'file_size': str(format(file.stat().st_size/1024, '.2f')) + ' KB', 'last_modify_time': time.ctime(file.stat().st_mtime), 'create_file_time': time.ctime(file.stat().st_ctime)})
        meta = {'status': 0, 'msg': 'Success'}
    elif action == 'Download':
        return send_file(os.path.join(Current_Path, File_Name), as_attachment=True)
    elif action == 'LastFolder':
        Current_Path = os.path.abspath(os.path.join(Current_Path, ".."))
        for file in os.scandir(Current_Path):
            Current_Path_FilesList.append({'file_name': file.name, 'is_dir': file.is_dir(), 'file_size': str(format(file.stat().st_size/1024, '.2f')) + ' KB', 'last_modify_time': time.ctime(file.stat().st_mtime), 'create_file_time': time.ctime(file.stat().st_ctime)})
        meta = {'status': 0, 'msg': 'Success'}
    elif action == 'EnterFolder':
        Current_Path = os.path.join(Current_Path, File_Name)
        for file in os.scandir(Current_Path):
            Current_Path_FilesList.append({'file_name': file.name, 'is_dir': file.is_dir(), 'file_size': str(format(file.stat().st_size/1024, '.2f')) + ' KB', 'last_modify_time': time.ctime(file.stat().st_mtime), 'create_file_time': time.ctime(file.stat().st_ctime)})
        meta = {'status': 0, 'msg': 'Success'}
    elif action == 'Delete':
        os.remove(os.path.join(Current_Path, File_Name))
        meta = {'status': 0, 'msg': 'Success'}
    elif action == 'Rename':
        try:
            os.rename(os.path.join(Current_Path, Existing_File_Name), os.path.join(Current_Path, New_File_Name))
            meta = {'status': 0, 'msg': 'Success'}
        except Exception as err:
            meta = {'status': 1, 'msg': err.args[1]}
    data = {'Current_Path': Current_Path, 'Files_List': Current_Path_FilesList}
    returnmessage = {'meta': meta, 'data': data}
    log.info(returnmessage)
    return jsonify(returnmessage)