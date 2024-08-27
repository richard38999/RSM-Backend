import datetime
import os
from OctopusHelper.Index import Summary, SET111
from OctopusHelper.Util import findStr, writeSheet_ONE_Record, writeSheet_TWO_Record
from operator import itemgetter
zip_path = ''
def Check_YearlyReportStatus(Year):
    status = True
    currentlyPath = os.getcwd()  # 获取当前目录path
    startDate = Year + '0101'
    date_DateFrom = datetime.datetime.strptime(startDate, '%Y%m%d')
    returnmessage = 'Some Data Not Exist: '
    i = 0
    while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))
           [0:4]) == Year:
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
def Download_YearlyReport(Year):
    status = False
    currentlyPath = os.getcwd()  # 获取当前目录path
    Year_Summary = []
    Sheet_TWO = []
    Month_Summary = []
    i = 0
    m = 1
    startDate = Year + '0101'
    Month = Year + str(m).zfill(2)
    addheader = False
    # print(str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d")))
    while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))
           [0:4]) == Year:
        Month_Summary = []
        while (str((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime("%Y%m%d"))
               [0:6]) == Month:
            with open(
                    currentlyPath + '\\Octopus\\Parsefiles\\' + str
                        ((datetime.datetime.strptime(startDate, '%Y%m%d') + datetime.timedelta(days=+i)).strftime(
                        "%Y%m%d")) + '\\SET111csv.TXT', 'r', encoding='utf-8',
                    errors='ignore') as f:
                lines = f.readlines()
                for j in range(len(lines)):
                    Sheet_ONE_row = Summary()
                    Sheet_Three_row = SET111()
                    if j == 0:
                        if not addheader:
                            Sheet_Three_row = writeSheet_TWO_Record(Sheet_Three_row, lines[j].split(','))
                            Sheet_TWO.append(Sheet_Three_row)
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
                        Sheet_Three_row = writeSheet_TWO_Record(Sheet_Three_row, lines[j].split(','))
                        Sheet_TWO.append(Sheet_Three_row)

                        if not any(Sheet_Three_row[2] == x[0] for x in Month_Summary):
                            Sheet_ONE_row = writeSheet_ONE_Record(Sheet_ONE_row ,[Sheet_Three_row[2], float
                                (Sheet_Three_row[5].replace(" ", "")), float(Sheet_Three_row[4].replace(" ", ""))])
                            Month_Summary.append(Sheet_ONE_row)
                        else:
                            Month_Summary[next((idx for idx, val in enumerate(Month_Summary) if Sheet_Three_row[2] in val), None)][1] += float(Sheet_Three_row[5].replace(" ", ""))
                            Month_Summary[next((idx for idx, val in enumerate(Month_Summary) if Sheet_Three_row[2] in val), None)][2] += float(Sheet_Three_row[4].replace(" ", ""))
                        # Sheet_ONE_row = Summary()
                        # if not any(Sheet_Three_row[2] == x[0] for x in Year_Summary):
                        #     Sheet_ONE_row = writeSheet_ONE_Record(Sheet_ONE_row,[Sheet_Three_row[2], float(Sheet_Three_row[5].replace(" ", "")), float(Sheet_Three_row[4].replace(" ", ""))])
                        #     Year_Summary.append(Sheet_ONE_row)
                        # else:
                        #     Year_Summary[next((idx for idx, val in enumerate(Year_Summary) if Sheet_Three_row[2] in val), None)][1] += float(Sheet_Three_row[5].replace(" ", ""))
                        #     Year_Summary[next((idx for idx, val in enumerate(Year_Summary) if Sheet_Three_row[2] in val), None)][2] += float(Sheet_Three_row[4].replace(" ", ""))
            i += 1
        temp = Summary()
        log.info(Month_Summary)
        for j in Month_Summary:
            if not any(j[0] == x[0] for x in Year_Summary):
                Year_Summary.append(writeSheet_ONE_Record(temp ,[j[0], float(j[1]), float(j[2])]))
            else:
                Year_Summary[next((idx for idx, val in enumerate(Year_Summary) if j[0] in val), 0)][1] += float(j[1])
                Year_Summary[next((idx for idx, val in enumerate(Year_Summary) if j[0] in val), 0)][2] += float(j[2])
        m += 1
        Month = Year + str(m).zfill(2)

    lastSPID = None
    Year_Summary = sorted(Year_Summary, key=itemgetter(0))
    Year_Summary.insert(0 ,['SPID', 'Sum_of_UsageAmount', 'Sum_of_UsageCount'])
    for i in range(len(Year_Summary)):
        if i == 0:
            continue
        if lastSPID == None:
            lastSPID = int(Year_Summary[i][0])
            continue
        if int(Year_Summary[i][0]) - lastSPID > 1:
            Year_Summary.insert(i ,[str(lastSPID + 1), 0, 0])
            lastSPID = int(Year_Summary[ i +1][0])
        else:
            lastSPID = int(Year_Summary[i][0])
    returnmessage = {'Sheet_ONE': Year_Summary, 'Sheet_TWO': Sheet_TWO}
    status = True
    return [status, returnmessage]