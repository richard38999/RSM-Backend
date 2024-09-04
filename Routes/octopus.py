from flask import request, jsonify, send_file
from Logger import *
from flask_jwt_extended import jwt_required
from zipfile import ZipFile
from werkzeug.utils import secure_filename
from OctopusHelper.SPID import Check_SPIDStatus, Download_SPID
from OctopusHelper.Monthly import Check_MonthlyReportStatus, Download_MonthlyReport
from OctopusHelper.Yearly import Check_YearlyReportStatus, Download_YearlyReport
log = Log('Flask')
# @app.route("/Octopus/Report/<action>", methods=['POST'])
@jwt_required()
# @decorator.except_output('Flask', isSendEmail=Config.isSentEmail, Email_subject='RSM System Alert!')
def Octopus_Report(action):
    log.start('Octopus_Report')
    log.info(request.headers)
    # log.info()()("BODY: %s" % request.get_data())
    username = request.headers.get("username")
    meta = {}
    data = {}
    # try:
    if action == 'Check_SPIDStatus':
        SPID = request.json.get("SPID")
        DateFrom = request.json.get("DateFrom")
        DateTo = request.json.get("DateTo")
        result = Check_SPIDStatus(SPID, DateFrom, DateTo)
        if result[0] == True:
            meta = {'status': 0, 'msg': '{0}'.format(result[1])}
        else:
            meta = {'status': 1, 'msg': '{0}'.format(result[1])}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'Download_SPID':
        SPID = request.json.get("SPID")
        DateFrom = request.json.get("DateFrom")
        DateTo = request.json.get("DateTo")
        result = Download_SPID(SPID, DateFrom, DateTo)
        log.end('Octopus_Report')
        return send_file(result[1], as_attachment=True)
    elif action == 'Download_MonthlyReport':
        Month = request.json.get("Month")
        Monthly_Report_Status = Check_MonthlyReportStatus(Month)
        if Monthly_Report_Status[0] == True:
            result = Download_MonthlyReport(Month)
            if result[0] == True:
                meta = {'status': 0, 'msg': 'Success'}
                data = result[1]
            else:
                meta = {'status': 1, 'msg': 'Failed'}
        else:
            meta = {'status': 1, 'msg': Monthly_Report_Status[1]}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'Download_YearlyReport':
        Year = request.json.get("Year")
        Yearly_Report_Status = Check_YearlyReportStatus(Year)
        if Yearly_Report_Status[0] == True:
            result = Download_YearlyReport(Year)
            if result[0] == True:
                meta = {'status': 0, 'msg': 'Success'}
                data = result[1]
            else:
                meta = {'status': 1, 'msg': 'Failed'}
        else:
            meta = {'status': 1, 'msg': Yearly_Report_Status[1]}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)
    elif action == 'UploadRawData':
        log.info(request.files)
        files = request.files.getlist("files")
        # files = files.split(",")
        # files = list(filter(None, files))
        for f in files:
            # f = request.files[file]
            # namefile = secure_filename(file)
            pass
            # f = request.files['files']
            filepath = os.path.join(os.getcwd(),'Octopus/Rawfiles/', secure_filename(f.filename))
            directory = str(f.filename).split('.')
            unzipPath = os.path.join(os.getcwd(),'Octopus/Parsefiles/', '')
            # unzipPath = os.path.join('Octopus/Parsefiles/', secure_filename(directory[0]))
            f.save(filepath)
            with ZipFile(filepath, 'r') as zipObj:
                zipObj.extractall(unzipPath)
        meta = {'status': 0, 'msg': '{}'.format('Upload Success')}
        returnmessage = {'meta': meta, 'data': data}
        log.info(returnmessage)
        log.end('Octopus_Report')
        return jsonify(returnmessage)