import datetime
import os
import time
from main import current_app
import shutil
from operator import itemgetter

class SET111():
    SettDate = ''
    GroupID = ''
    SPID = ''
    SPName = ''
    UsageCount = 0
    UsageAmount = 0
    FeeAmount = 0
    FeePercentage = 0
    SettTotal = 0
    Late_ExpiredCount = 0
    AccountNo = ''


class MonthlySum():
    SPID = ''
    Sum_of_UsageAmount = 0
    Sum_of_UsageCount = 0


class Report():
    zip_path = ''

    def Check_SPIDStatus(self, SPID, str_DateFrom, str_DateTo):
        try:
            status = True
            currentlyPath = os.getcwd()  # 获取当前目录path
            allFileName = os.listdir(currentlyPath + '\\Octopus\\Parsefiles')
            date_DateFrom = datetime.datetime.strptime(str_DateFrom, '%Y%m%d')
            date_DateTo = datetime.datetime.strptime(str_DateTo, '%Y%m%d')
            current_app.logger.debug(str_DateFrom)
            current_app.logger.debug(str_DateTo)
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
        except Exception as e:
            current_app.logger.debug(e)
            status = False
            return [status, e]

    # check SPID
    def Download_SPID(self, SPID, str_DateFrom, str_DateTo):
        status = False
        currentlyPath = os.getcwd()  # 获取当前目录path
        allFileName = os.listdir(currentlyPath + '\\Octopus\\Parsefiles')
        date_DateFrom = datetime.datetime.strptime(str_DateFrom, '%Y%m%d')
        date_DateTo = datetime.datetime.strptime(str_DateTo, '%Y%m%d')
        current_app.logger.debug(str_DateFrom)
        current_app.logger.debug(str_DateTo)
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
        zipPassword = 'eftPay@{0}!'.format(time.strftime("%Y", time.localtime()))
        # print('Zip Password: {0}'.format(zipPassword))
        # zipDir(zip_path,dir_path,zipPassword)
        enCrypt(origin_dir, origin_folderName, zip_dir, zipName, zipPassword, deleteSource=True)
        status = True
        return [status, zip_path]

    def Download_MonthlyReport(self, str_Month):
        status = False
        currentlyPath = os.getcwd()  # 获取当前目录path
        Sheet_ONE = []
        Sheet_TWO = []
        i = 0
        startDate = str_Month + '01'
        addheader = False
        # print(str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d")))
        while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))[0:6]) == str_Month:
            with open(
                    currentlyPath + '\\Octopus\\Parsefiles\\' + str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime(
                            "%Y%m%d")) + '\\SET111csv.TXT', 'r', encoding='utf-8',
                 errors='ignore') as f:
                lines = f.readlines()
                for j in range(len(lines)):
                    Sheet_ONE_row = SET111()
                    Sheet_TWO_row = MonthlySum()
                    if j == 0:
                        if not addheader:
                            Sheet_ONE_row = writeSheet_ONE_Record(Sheet_ONE_row, lines[j].split(','))
                            Sheet_ONE.append(Sheet_ONE_row)
                            addheader = True
                    else:
                        if lines[j].count(',') > 10:
                            leng = lines[j].count(',')
                            lefttemp = findStr(lines[j], ',', 3)
                            righttemp = findStr(lines[j], ',', 5)
                            a = lines[j]
                            b = '"'
                            str_list = list(a)
                            str_list.insert(lefttemp + 1, b)
                            str_list.insert(righttemp + 1, b)
                            a_b = ''.join(str_list)
                            lines[j] = a_b
                        Sheet_ONE_row = writeSheet_ONE_Record(Sheet_ONE_row, lines[j].split(','))
                        Sheet_ONE.append(Sheet_ONE_row)

                        if not any(Sheet_ONE_row[2] == x[0] for x in Sheet_TWO):
                            Sheet_TWO_row = writeSheet_TWO_Record(Sheet_TWO_row,[Sheet_ONE_row[2], float(Sheet_ONE_row[5].replace(" ", "")), float(Sheet_ONE_row[4].replace(" ", ""))])
                            Sheet_TWO.append(Sheet_TWO_row)
                        else:
                            Sheet_TWO[next((idx for idx, val in enumerate(Sheet_TWO) if Sheet_ONE_row[2] in val), None)][1] += float(Sheet_ONE_row[5].replace(" ", ""))
                            Sheet_TWO[next((idx for idx, val in enumerate(Sheet_TWO) if Sheet_ONE_row[2] in val), None)][2] += float(Sheet_ONE_row[4].replace(" ", ""))
                            # Sheet_TWO[Sheet_TWO.index(Sheet_ONE_row[2])][1] += float(Sheet_ONE_row[5].replace(" ", ""))
                            # Sheet_TWO[Sheet_TWO.index(Sheet_ONE_row[2])][2] += float(Sheet_ONE_row[4].replace(" ", ""))
            i += 1

        lastSPID = None
        Sheet_TWO = sorted(Sheet_TWO, key=itemgetter(0))
        Sheet_TWO.insert(0,['SPID', 'Sum_of_UsageAmount', 'Sum_of_UsageCount'])
        for i in range(len(Sheet_TWO)):
            if i == 0:
                continue
            if lastSPID == None:
                lastSPID = int(Sheet_TWO[i][0])
                continue
            if int(Sheet_TWO[i][0]) - lastSPID > 1:
                Sheet_TWO.insert(i,[str(lastSPID + 1), 0, 0])
                lastSPID = int(Sheet_TWO[i+1][0])
            else:
                lastSPID = int(Sheet_TWO[i][0])
        returnmessage = {'Sheet_ONE': Sheet_ONE, 'Sheet_TWO': Sheet_TWO}
        status = True
        return [status, returnmessage]

    def Check_MonthlyReportStatus(self, Month):
        status = True
        currentlyPath = os.getcwd()  # 获取当前目录path
        startDate = Month + '01'
        date_DateFrom = datetime.datetime.strptime(startDate, '%Y%m%d')
        returnmessage = 'Some Data Not Exist: '
        i = 0
        while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))[0:6]) == Month:
            if not os.path.exists(currentlyPath + '\\Octopus\\Parsefiles' + '\\' + (
                    date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d")):
                returnmessage += (date_DateFrom + datetime.timedelta(days=+i)).strftime("%Y%m%d") + '; \r\n'
                status = False
                i += 1
                continue
            i += 1
        if status == True:
            returnmessage = 'Success'
            return [status, returnmessage]
        else:
            return [status, returnmessage]

def writeSheet_ONE_Record(Sheet_ONE, lines):
    temp = ''
    # Sheet_ONE.SettDate = lines[0]
    # Sheet_ONE.GroupID = lines[1]
    # Sheet_ONE.SPID = lines[2]
    if len(lines) > 11:
        for i in range(len(lines) - 10):
            temp += lines[3+i]
            if i != 0:
                lines.remove(lines[3])
    else:
        temp = lines[3]
    # Sheet_ONE.SPName = temp
    # Sheet_ONE.UsageCount = lines[4]
    # Sheet_ONE.UsageAmount = lines[5]
    # Sheet_ONE.FeeAmount = lines[6]
    # Sheet_ONE.FeePercentage = lines[7]
    # Sheet_ONE.SettTotal = lines[8]
    # Sheet_ONE.Late_ExpiredCount = lines[9]
    # Sheet_ONE.AccountNo = lines[10]
    returnmessage = [lines[0], lines[1],lines[2], temp, lines[4].replace(" ", ""), lines[5].replace(" ", ""), lines[6].replace(" ", ""),lines[7].replace(" ", ""), lines[8].replace(" ", ""), lines[9].replace(" ", ""), lines[10].replace(" ", "")]

    return returnmessage

def writeSheet_TWO_Record(Sheet_TWO, lines):
    Sheet_TWO.SPID = lines[0]
    Sheet_TWO.Sum_of_UsageAmount = lines[1]
    Sheet_TWO.Sum_of_UsageCount = lines[2]
    returnmessage = [lines[0], lines[1], lines[2]]
    return returnmessage

def enCrypt(origin_dir, origin_folderName, zip_dir, zipName, passwd, deleteSource=False):
    """
        压缩加密，并删除原数据
        window系统调用rar程序
        linux等其他系统调用内置命令 zip -P123 tar source

		filepathname：文件名（绝对路径）
		passwd：加密密码
		deleteSource：是否删除原数据，默认不删除原文件

    """
    cmd = 'cd %s && C:\\"Program Files"\\WinRAR\\WinRAR.exe a -p%s %s %s' % (
    origin_dir, passwd, zip_dir + '\\' + zipName, origin_folderName)
    # print(cmd)
    os.system(cmd)
    # if deleteSource:
    #     os.remove(origin_dir + '\\' + origin_folderName)


def findStr(str, subStr, findCnt):
    listStr = str.split(subStr, findCnt)
    # print (listStr)
    if len(listStr) <= findCnt:
        return -1
    return len(str) - len(listStr[-1]) - len(subStr)
