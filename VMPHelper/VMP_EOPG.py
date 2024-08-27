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