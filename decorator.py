from datetime import datetime
import traceback
from functools import wraps
import Logger
import Configuration
import Email
import Async
Email_info = Configuration.get_Email_info()
Sent_To = 'richardding@eftpay.com.hk'
log = None
# 异常输出
def except_output(Log_name, isSendEmail=False, Email_subject='', Email_from='RSM System'):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def execept_print(*args, **kwargs):
            sign = '*' * 100 + '\n'
            try:
                log = Logger.Log(Log_name)
                return func(*args, **kwargs)
            except Exception as ex:
                errorMessage = f'{sign}>>>Exception Time：\t{datetime.now()}\n>>>Exception def：\t{func.__name__}\n>>>Exception msg：\t{ex}\n{traceback.format_exc()}{sign}'
                log.error(errorMessage)
                if isSendEmail:
                    SendEmail(Email_from=Email_from, Email_subject=Email_subject, Email_attachement=log.log_full_name, Email_content=errorMessage)
                raise
        return execept_print
    return except_execute
@Async.async_call
def SendEmail(Email_content='', Email_subject='', Email_from='RSM System',Email_attachement=''):
    Email.sentEmail(Email_from=Email_from, Email_subject=Email_subject, Email_attachement=Email_attachement,
                    Email_content=Email_content)