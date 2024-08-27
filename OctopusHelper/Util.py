import os

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
def writeSheet_TWO_Record(Sheet_TWO, lines):
    temp = ''
    # Sheet_TWO.SettDate = lines[0]
    # Sheet_TWO.GroupID = lines[1]
    # Sheet_TWO.SPID = lines[2]
    if len(lines) > 11:
        for i in range(len(lines) - 10):
            temp += lines[3+i]
            if i != 0:
                lines.remove(lines[3])
    else:
        temp = lines[3]
    # Sheet_TWO.SPName = temp
    # Sheet_TWO.UsageCount = lines[4]
    # Sheet_TWO.UsageAmount = lines[5]
    # Sheet_TWO.FeeAmount = lines[6]
    # Sheet_TWO.FeePercentage = lines[7]
    # Sheet_TWO.SettTotal = lines[8]
    # Sheet_TWO.Late_ExpiredCount = lines[9]
    # Sheet_TWO.AccountNo = lines[10]
    returnmessage = [lines[0], lines[1],lines[2], temp, lines[4].replace(" ", ""), lines[5].replace(" ", ""), lines[6].replace(" ", ""),lines[7].replace(" ", ""), lines[8].replace(" ", ""), lines[9].replace(" ", ""), lines[10].replace(" ", "")]

    return returnmessage
def writeSheet_ONE_Record(Sheet_ONE, lines):
    Sheet_ONE.SPID = lines[0]
    Sheet_ONE.Sum_of_UsageAmount = lines[1]
    Sheet_ONE.Sum_of_UsageCount = lines[2]
    returnmessage = [lines[0], lines[1], lines[2]]
    return returnmessage
