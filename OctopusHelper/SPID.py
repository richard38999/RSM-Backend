import datetime
import time
import os
import shutil
from OctopusHelper.Util import enCrypt
import Logger
log = Logger.Log('Octopus')
zip_path = ''
def Check_SPIDStatus(SPID, str_DateFrom, str_DateTo):
    status = True
    currentlyPath = os.getcwd()  # 获取当前目录path
    allFileName = os.listdir(currentlyPath + '\\Octopus\\Parsefiles')
    date_DateFrom = datetime.datetime.strptime(str_DateFrom, '%Y%m%d')
    date_DateTo = datetime.datetime.strptime(str_DateTo, '%Y%m%d')
    log.debug(str_DateFrom)
    log.debug(str_DateTo)
    returnmessage = 'Some Data Not Exist: '
    for i in range((date_DateTo - date_DateFrom).days + 1):
        if not os.path.exists(currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d")):
            returnmessage += (date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '; \r\n'
            status = False
            continue
        if not os.path.exists(currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.051'):
            returnmessage += (date_DateFrom + datetime.timedelta(days=+i)).strftime(
                "%Y%m%d") + '\\' + SPID + '.051' + '; \r\n'
            status = False
            continue
        if not os.path.exists(currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.052'):
            returnmessage += (date_DateFrom + datetime.timedelta(days=+i)).strftime(
                "%Y%m%d") + '\\' + SPID + '.052' + '; \r\n'
            status = False
            continue
        if not os.path.exists(currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.csv'):
            returnmessage += (date_DateFrom + datetime.timedelta(days=+i)).strftime(
                "%Y%m%d") + '\\' + SPID + '.csv' + '; \r\n'
            status = False
            continue
    if status == True:
        returnmessage = 'Success'
        return [status, returnmessage]
    else:
        return [status, returnmessage]
def Download_SPID(SPID, str_DateFrom, str_DateTo):
    status = False
    currentlyPath = os.getcwd()  # 获取当前目录path
    allFileName = os.listdir(currentlyPath + '\\Octopus\\Parsefiles')
    date_DateFrom = datetime.datetime.strptime(str_DateFrom, '%Y%m%d')
    date_DateTo = datetime.datetime.strptime(str_DateTo, '%Y%m%d')
    log.debug(str_DateFrom)
    log.debug(str_DateTo)
    masterFileName = time.strftime("%Y%m%d%H%M%S", time.localtime())
    Path_SPID = currentlyPath + '\\Octopus\\Merchant_Report\\' + masterFileName
    if str_DateFrom == str_DateTo:
        zipName = SPID + '({0}).zip'.format(str_DateFrom)
        dirName = SPID + '({0})'.format(str_DateFrom)
    else:
        zipName = SPID + '({0}-{1}).zip'.format(str_DateFrom, str_DateTo)
        dirName = SPID + '({0}-{1})'.format(str_DateFrom, str_DateTo)
    for i in range((date_DateTo - date_DateFrom).days + 1):
        if not os.path.exists(Path_SPID):
            os.mkdir(Path_SPID)
        if not os.path.exists(Path_SPID + '\\' + dirName):
            os.mkdir(Path_SPID + '\\' + dirName)
        if not os.path.exists(
                Path_SPID + '\\' + dirName + '\\' + (date_DateFrom + datetime.timedelta(days=+i)).strftime(
                    "%Y%m%d")):
            os.mkdir(Path_SPID + '\\' + dirName + '\\' + (date_DateFrom + datetime.timedelta(days=+i)).strftime(
                "%Y%m%d"))
        origin_path = currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.051'
        new_file_name = Path_SPID + '\\' + dirName + '\\' + (date_DateFrom + datetime.timedelta(days=+i)).strftime(
            "%Y%m%d") + '\\' + SPID + '.051'
        shutil.copyfile(origin_path, new_file_name)
        origin_path = currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.052'
        new_file_name = Path_SPID + '\\' + dirName + '\\' + (date_DateFrom + datetime.timedelta(days=+i)).strftime(
            "%Y%m%d") + '\\' + SPID + '.052'
        shutil.copyfile(origin_path, new_file_name)
        origin_path = currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '\\' + SPID + '.csv'
        new_file_name = Path_SPID + '\\' + dirName + '\\' + (date_DateFrom + datetime.timedelta(days=+i)).strftime(
            "%Y%m%d") + '\\' + SPID + '.csv'
        shutil.copyfile(origin_path, new_file_name)

    origin_dir = Path_SPID
    origin_folderName = dirName
    zip_dir = Path_SPID
    zip_path = Path_SPID + '\\' + zipName
    zipPassword = 'EFT{0}'.format(str(SPID)[1:])
    # print('Zip Password: {0}'.format(zipPassword))
    # zipDir(zip_path,dir_path,zipPassword)
    enCrypt(origin_dir, origin_folderName, zip_dir, zipName, zipPassword, deleteSource=True)
    status = True
    return [status, zip_path]