def packSignStr(obj, secretcode):
    retuenStr = secretcode
    for name, value in vars(obj).items():
        if value != None and value != '':
            # print('%s=%s' % (name, value))
            retuenStr += '%s=%s&' % (name, value)
    retuenStr = retuenStr[:(len(retuenStr) - 1)]
    return retuenStr

def packSignStr_EOPG(obj, secretcode):
    retuenStr = secretcode
    for name, value in vars(obj).items():
        if value != None:
            # print('%s=%s' % (name, value))
            retuenStr += '%s=%s&' % (name, value)
    retuenStr = retuenStr[:(len(retuenStr) - 1)]
    return retuenStr

def packJsonMsg(obj):
    retuenStr = {}
    for name, value in vars(obj).items():
        if value != None and value != '':
        # if value != None:
            retuenStr[name] = value
            # retuenStr.append({name: value})
    return retuenStr

def packGetMsg(obj, url):
    retuenURL = url
    retuenURL += '?'
    for name, value in vars(obj).items():
        if not value == None:
            # print('%s=%s' % (name, value))
            retuenURL += '%s=%s&' % (name, value)

    retuenURL = retuenURL[:(len(retuenURL) - 1)]
    return retuenURL
