import os
import datetime as datetime
import SFTP
import Logger
import Configuration
import imaplib
import email
from email.header import decode_header
import decorator
import Email
import time
import Utility

log = Logger.Log('SCB_FPS_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
sftp = SFTP.init('SCB_FPS_Report')
emailContent = ''
Settlement_Date = datetime.datetime.now().strftime("%Y%m%d")
Transaction_Date = (datetime.datetime.strptime(Settlement_Date,'%Y%m%d') + datetime.timedelta(days=-1)).strftime("%d/%m/%Y")
Root_Folder = 'SCB_FPS_Report'
email_result = False
notify_email_content = ''
attachment_name = ''
alert_email_to = None # if None, default send to richardding@eftpay.com.hk
@decorator.except_output('SCB_FPS_Report', isSendEmail=True, Email_to=alert_email_to, Email_subject=f'[{email_result}] SCB FPS Report Checking Result({Transaction_Date})')
def main():
    global email_result
    global notify_email_content
    global alert_email_to
    for i in AlertEmail:
        if i[1] == 'SCB_FPS_Report':  # i[1] == Project Name
            alert_email_to = i[0]  # i[0] == alert email address
    if not get_email_attachment():
        return
    # unzip attachment
    if not unzip_attachement(attachment_path=attachment_name):
        return
    # check SFTP file exist or not
    sftp_root_path = '/scbfps/'
    sftp_remote_path = sftp_root_path + attachment_name.replace('zip', 'csv')
    if sftp.checkSftpFile(SFTP_info[3], remotepath=sftp_remote_path):
        notify_email_content = "Already uploaded the report, no need to upload again. if you want to re-upload, please delete the sftp report and then run this program again. Thanks."
        log.info(notify_email_content)
        return

    if not sftp.putSftpFile(SFTP_info[3], localpath=, remotepath=sftp_remote_path):
        notify_email_content = "upload SFTP report failed."
        log.info(notify_email_content)
        return
    # upload report success
    email_result = True
    notify_email_content += 'upload to sftp success'
    log.info('upload to sftp success')
    return
def unzip_attachement(attachment_path=''):
    result = False
    pass
    return result

def get_email_attachment():
    global notify_email_content
    result = False
    if Email_info[2][10] == 'Y': # Email_info[2][8] = imap SSL, "Y" = SSL, "N" == Non SSL
        imap = imaplib.IMAP4_SSL(host=Email_info[2][6], port=Email_info[2][7])
    else:
        imap = imaplib.IMAP4(host=Email_info[2][6], port=Email_info[2][7])
    # Email_info[2][8] = username, Email_info[2][9] = password
    imap.login(Email_info[2][8], Email_info[2][9])
    # choose inbox folder
    status, email_count = imap.select("INBOX")
    # search all email count
    # status, email_count = imap.search(None, 'ALL')
    # check search email count status
    if status != 'OK':
        emailContent = 'search email Failed'
        # sent alert email
        Email.sentEmail(Log_Name='SCB_FPS_Report',
                           Email_subject=f'[{email_result}] SCB FPS Report Checking Result({Transaction_Date})',
                           Email_content=emailContent,
                           Email_to=alert_email_to,
                           Email_from=Email_info[0][3])
        return
    # number of top emails to fetch
    N = 20
    # total number of emails
    email_count = int(email_count[0])

    for i in range(email_count, email_count-N, -1): # only check recent 20 email
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            # Parse the raw email message in to a convenient object
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                log.info('===== Email details =====')
                email_subject, encoding = decode_header(msg["Subject"])[0] # 防止乱码
                if isinstance(email_subject, bytes):
                    # if it's a bytes, decode to str
                    email_subject = email_subject.decode(encoding)
                log.info(f'Subject: {email_subject}')
                # check email subject
                search_subject = f'FPS Fund Collection Report - {Transaction_Date}'
                log.info(f'search_subject: {search_subject}')
                if search_subject not in email_subject:
                    notify_email_content = "didn't found email, please check yesterday transaction count. \r\n" \
                                    "if yesterday transaction count > 1, please check with SCB."
                    log.info('Not this email...Next')
                    continue
                email_From = msg["from"]
                log.info(f'From: {email_From}')
                notify_email_content += f'From: {email_From}\r\n'
                email_To = msg["to"]
                log.info(f'To: {email_To}')
                notify_email_content += f'To: {email_To}\r\n'
                email_Cc = msg["cc"]
                log.info(f'Cc: {email_Cc}')
                notify_email_content += f'Cc: {email_Cc}\r\n'
                email_Bcc = msg["bcc"]
                log.info(f'Bcc: {email_Bcc}')
                notify_email_content += f'Bcc: {email_Bcc}\r\n'
                # if the email message is multipart

                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        charset = part.get_charset()
                        log.info(f'charset: {charset}')
                        # extract content type of email
                        content_type = part.get_content_type()
                        log.info(f'content_type: {content_type}')
                        content_disposition = str(part.get("Content-Disposition"))
                        log.info(f'content_disposition: {content_disposition}')
                        try:
                            # get the email body
                            email_body = part.get_payload(decode=True).decode()
                        except:
                            pass

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            log.info(f'email_body: {email_body}')
                        elif "attachment" in content_disposition:
                            # download attachment
                            attachment_name = part.get_filename()
                            log.info(f'attachment_name: {attachment_name}')
                            if attachment_name:
                                if not os.path.isdir(Root_Folder):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(Root_Folder)
                                attachment_filepath = os.path.join(Root_Folder, attachment_name)
                                # download attachment and save it
                                open(attachment_filepath, "wb").write(part.get_payload(decode=True))
                            break

    # close the connection and logout
    imap.close()
    imap.logout()
    return result

if __name__ == '__main__': # program 入口
    log.start('SCB_FPS_Report')
    main()
    Email.sentEmail(Log_Name='SCB_FPS_Report',
                    Email_subject=f'[{email_result}] SCB FPS Report Checking Result({Transaction_Date})',
                    Email_content=emailContent,
                    Email_to=alert_email_to,
                    Email_from=Email_info[0][3])
    log.end('SCB_FPS_Report')