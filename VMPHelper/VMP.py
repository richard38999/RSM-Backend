

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
    scheme = None
    packageName = None
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
