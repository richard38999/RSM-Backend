

class Request():
    clientId = None
    merchantRef = None
    cmd = None
    type = None
    amt = None
    goodsName = None
    goodsDesc = None
    channel = None
    cardToken = None
    cardTokenSrc = None
    successUrl = None
    failureUrl = None
    webhookUrl = None
    metadata = None
    duration = None
    orderId = None
    durationHr = None

class Response():
    clientId = None
    merchantRef = None
    cmd = None
    orderId = None
    type = None
    txnId = None
    txnType = None
    merchantId = None
    hostId = None
    card = None
    status = None
    amt = None
    resp = None
    hostTime = None
    appCode = None
    pan = None
    expDate = None
    respMsg = None
    goodsName = None
    cardToken = None
    cardTokenSrc = None
    metadata = None
    paidAmt = None
    orderAmt = None
    paymentLinkUrl = None
    approvedTxnId = None
    pass

def packJsonMsg(obj):
    retuenStr = {}
    for name, value in vars(obj).items():
        if value != None and value != '':
        # if value != None:
            retuenStr[name] = value
            # retuenStr.append({name: value})
    return retuenStr

def packRequest(
                clientId='',
                merchantRef='',
                cmd='',
                type='',
                amt='',
                goodsName='',
                goodsDesc='',
                channel='',
                cardToken='',
                cardTokenSrc='',
                successUrl='',
                failureUrl='',
                webhookUrl='',
                duration='',
                orderId='',
                durationHr=''):
    Spiral_Request = Request()
    Spiral_Request.clientId = clientId
    Spiral_Request.merchantRef = merchantRef
    Spiral_Request.cmd = cmd
    Spiral_Request.type = type
    Spiral_Request.amt = amt
    Spiral_Request.goodsName = goodsName
    Spiral_Request.goodsDesc = goodsDesc
    Spiral_Request.channel = channel
    Spiral_Request.cardToken = cardToken
    Spiral_Request.cardTokenSrc = cardTokenSrc
    Spiral_Request.successUrl = successUrl
    Spiral_Request.failureUrl = failureUrl
    Spiral_Request.webhookUrl = webhookUrl
    Spiral_Request.duration = duration
    Spiral_Request.orderId = orderId
    Spiral_Request.durationHr = durationHr
    return Spiral_Request