from flask import request, jsonify
from Logger import *
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
log = Log('Flask')
import csv

# @app.route("/PAOB/Report/<action>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def PAOB_Report(action):
    log.start('PAOB_Report')
    log.info(request.headers)
    # log.info()()("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    meta = {}
    data = {}
    if action == 'UploadRawData':
        log.info(request.files)
        files = request.files.getlist("files")
        data = []
        for f in files:
            filepath = os.path.join('PAOB/', secure_filename(f.filename))
            f.save(filepath)
            vlookupFile = ''
            i = 1
            with open(os.path.join('PAOB/','temp.txt')) as temp:
                vlookupFile = temp.read().splitlines()
                # log.info(vlookupFile)
            with open(filepath, newline='') as csvfile:
                rows = csv.reader(csvfile)
                addHeader = False
                for row in rows:
                    # log.info(f'{i}: {row}')
                    # log.info(row[0])
                    # i += 1
                    if addHeader == False:
                        data.append(row)
                        addHeader = True
                    if len(row) != 0:
                        if row[0] in vlookupFile:
                            if row[8] == 'SALE ADVICE':
                                row[8] = 'SALE'
                            data.append(row)
            os.remove(filepath)
        meta = {'status': 0, 'msg': '{}'.format('Upload Success')}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('PAOB_Report')
        return jsonify(returnmessage)
