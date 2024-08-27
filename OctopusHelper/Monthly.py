import datetime
import os
from OctopusHelper.Index import Summary, SET111
from OctopusHelper.Util import findStr, writeSheet_ONE_Record, writeSheet_TWO_Record
from operator import itemgetter

zip_path = ''

def Download_MonthlyReport(str_Month):
    status = False
    currentlyPath = os.getcwd()  # 获取当前目录path
    Sheet_ONE = []
    Sheet_TWO = []
    i = 0
    startDate = str_Month + '01'
    addheader = False
    # print(str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d")))
    while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))
           [0:6]) == str_Month:
        with open(
                currentlyPath + '\\Octopus\\Parsefiles\\' + str
                    ((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime(
                    "%Y%m%d")) + '\\SET111csv.TXT', 'r', encoding='utf-8',
                errors='ignore') as f:
            lines = f.readlines()
            for j in range(len(lines)):
                Sheet_ONE_row = Summary()
                Sheet_TWO_row = SET111()
                if j == 0:
                    if not addheader:
                        Sheet_TWO_row = writeSheet_TWO_Record(Sheet_TWO_row, lines[j].split(','))
                        Sheet_TWO.append(Sheet_TWO_row)
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
                    Sheet_TWO_row = writeSheet_TWO_Record(Sheet_TWO_row, lines[j].split(','))
                    Sheet_TWO.append(Sheet_TWO_row)

                    if not any(Sheet_TWO_row[2] == x[0] for x in Sheet_ONE):
                        Sheet_ONE_row = writeSheet_ONE_Record(Sheet_ONE_row ,[Sheet_TWO_row[2], float(Sheet_TWO_row[5].replace(" ", "")), float(Sheet_TWO_row[4].replace(" ", ""))])
                        Sheet_ONE.append(Sheet_ONE_row)
                    else:
                        Sheet_ONE[next((idx for idx, val in enumerate(Sheet_ONE) if Sheet_TWO_row[2] in val), None)][1] += float(Sheet_TWO_row[5].replace(" ", ""))
                        Sheet_ONE[next((idx for idx, val in enumerate(Sheet_ONE) if Sheet_TWO_row[2] in val), None)][2] += float(Sheet_TWO_row[4].replace(" ", ""))
                        # Sheet_TWO[Sheet_TWO.index(Sheet_ONE_row[2])][1] += float(Sheet_ONE_row[5].replace(" ", ""))
                        # Sheet_TWO[Sheet_TWO.index(Sheet_ONE_row[2])][2] += float(Sheet_ONE_row[4].replace(" ", ""))
        i += 1
    lastSPID = None
    Sheet_ONE = sorted(Sheet_ONE, key=itemgetter(0))
    for sheet in Sheet_ONE:
        if lastSPID == None:
            lastSPID = int(sheet[0]) # 36001
            continue
        while int(sheet[0]) - lastSPID > 1:
            Sheet_ONE.append([str(lastSPID + 1), 0, 0])
            lastSPID = lastSPID + 1
        else:
            lastSPID = lastSPID + 1
    Sheet_ONE = sorted(Sheet_ONE, key=itemgetter(0))
    Sheet_ONE.insert(0, ['SPID', 'Sum_of_UsageAmount', 'Sum_of_UsageCount'])
    # for i in range(len(Sheet_ONE)):
    #     if i == 0:
    #         continue
    #     if lastSPID == None:
    #         lastSPID = int(Sheet_ONE[i][0])
    #         continue
    #
    #     if int(Sheet_ONE[i][0]) - lastSPID > 1:
    #         for j in range(1,(int(Sheet_ONE[i][0]) - lastSPID) + 1):
    #             Sheet_ONE.insert(i, [str(lastSPID + 1), 0, 0])
    #             lastSPID = int(Sheet_ONE[i + 1][0])
    #             # lastSPID = lastSPID + 1
    #     else:
    #         lastSPID = lastSPID + 1

    # if int(Sheet_ONE[i][0]) - lastSPID > 1:
    #     Sheet_ONE.insert(i,[str(lastSPID + 1), 0, 0])
    #     lastSPID = int(Sheet_ONE[i+1][0])
    # else:
    #     # lastSPID = int(Sheet_ONE[i][0])
    #     lastSPID = lastSPID + 1
    returnmessage = {'Sheet_ONE': Sheet_ONE, 'Sheet_TWO': Sheet_TWO}
    status = True
    return [status, returnmessage]

def Check_MonthlyReportStatus(Month):
    status = True
    currentlyPath = os.getcwd()  # 获取当前目录path
    startDate = Month + '01'
    date_DateFrom = datetime.datetime.strptime(startDate, '%Y%m%d')
    returnmessage = 'Some Data Not Exist: '
    i = 0
    while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))
           [0:6]) == Month:
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