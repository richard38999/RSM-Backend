
class EOPG_Request():
    active_time = None # Mandatory=N, Sign=N
    api_version = None # Mandatory=Y, Sign=N
    app_pay = None # Mandatory=N, Sign=N
    fee_type = None # Mandatory=N, Sign=Y
    goods_body = None # Mandatory=Y, Sign=N
    goods_subject = None # Mandatory=Y, Sign=N
    lang = None # Mandatory=N, Sign=N
    merch_refund_id = None  # Mandatory=N, Sign=N
    merch_ref_no = None # Mandatory=Y, Sign=Y
    mid = None # Mandatory=Y, Sign=Y
    notify_url = None # Mandatory=N, Sign=N
    payment_type = None # Mandatory=Y, Sign=Y
    redirect = None # Mandatory=N, Sign=N
    refund_reason = None # Mandatory=Y, Sign=Y
    refund_amount = None # Mandatory=Y, Sign=Y
    return_url = None # Mandatory=Y, Sign=N
    reuse = None # Mandatory=N, Sign=N
    service = None # Mandatory=Y, Sign=Y
    signature = None # Mandatory=Y, Sign=N
    trans_amount = None # Mandatory=Y, Sign=Y
    tid = None # Mandatory=N, Sign=N
    wallet = None # Mandatory=N, Sign=N
    wechatWeb = None # Mandatory=Y, Sign=Y
    balance_ignore = None
    pass

class EOPG_Response():
    attach = None
    error = None
    service = None
    payment_type = None
    mid = None
    trans_return_time = None
    signature = None
    merch_ref_no = None
    order_id = None
    trade_no = None
    trans_status = None
    trans_amount = None
    tid = None
    trans_existed = None
    refund_amount = None
    refund_reason = None
    refund_result = None
    time = None
    merch_refund_id = None
    refund_status = None
    pass

class VMP_Request():
    service = None
    user_confirm_key = None
    transaction_amount = None
    out_trade_no = None
    payType = None
    buyerType = None
    subject = None
    time = None
    wallet = None
    body = None
    pay_scene = None
    fee_type = None
    tid = None
    notify_url = None
    return_url = None
    active_time = None
    lang = None
    return_amount = None
    total_fee = None
    reason = None
    out_refund_no = None
    eft_trade_no = None
    refund_no = None
    trans_status = None
    trans_amount = None
    querytype = None
    payment_type = None
    requestId = None
    paytype = None
    buyertype = None
    eftpay_trade_no = None
    is_notify = None
    notify_data = None
    openid = None
    sub_openid = None
    scene_type = None
    scene_info = None
    receipt = None
    goods_tag = None
    detail = None
    refund_desc = None
    sign = None
    billingAddress = None
    items = None
    shippingAddress = None
    customerInfo = None
    pass
class detail():
    cost_price = None
    receipt_id = None
    goods_detail = None
    pass

class goods_detail():
    goods_id = None
    wxpay_goods_id = None
    goods_name = None
    quantity = None
    price = None
    goods_detail = None
    pass

class VMP_Response():
    return_status = None
    return_char = None
    time = None
    sign = None
    pay_apptrade = None
    user_confirm_key = None
    out_trade_no = None
    payType = None
    buyerType = None
    wallet = None
    eft_trade_no = None
    fee_type = None
    transaction_amount = None
    tid = None
    notify_type = None
    trade_no = None
    total_fee = None
    currency = None
    trade_status = None
    transaction_id = None
    trade_type = None
    gmt_payment = None
    out_refund_no = None
    refund_time = None
    return_amount = None
    refund_no = None
    buyer_id = None
    original_amount = None
    payment_type = None
    trade_time = None
    qr_code = None
    eftpay_trade_no = None
    requestId = None
    paytype = None
    buyertype = None
    alipay_trade_no = None
    aplus_trade_no = None
    actual_payment_type = None
    eftpay_qr2_info = None
    extra_trade_no = None
    is_notify = None
    notify_url = None
    notify_send_data = None
    notify_return_data = None
    qr_code_address = None
    rate = None
    payPackage = None
    openid = None
    sub_openid = None
    scene_type = None
    pass


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
