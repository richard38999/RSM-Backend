import os
import datetime as datetime
import sys
import SFTP
import Logger
import Configuration
import imaplib
import email
from email.header import decode_header
import decorator
import Email
import Utility

log = Logger.Log('SCB_FPS_Report')
AlertEmail = Configuration.get_Alert_Email()
Email_info = Configuration.get_Email_info()
SFTP_info = Configuration.get_SFTP_info()
sftp = SFTP.init('SCB_FPS_Report')
Settlement_Date = None
Transaction_Date = None
email_Transaction_date = None
Root_Folder = 'SCB_FPS_Report'
email_result = False
notify_email_content = ''
attachment_name = ''
extract_folder = ''
alert_email_to = '' # if None, default send to richardding@eftpay.com.hk
for i in AlertEmail:
    if i[1] == 'SCB_FPS_Report':  # i[1] == Project Name
        alert_email_to = i[0]  # i[0] == alert email address
Email_attachment = None
@decorator.except_output('SCB_FPS_Report',
                         isSendEmail=True,
                         Email_to=alert_email_to,
                         Email_subject=f'[{email_result}] SCB FPS Report Exception!!! ',
                         Email_from=Email_info[0][3],
                         Email_displayName='SCB FPS Report')
def main():
    global email_result
    global notify_email_content
    global alert_email_to
    global Settlement_Date
    global email_Transaction_date
    global Email_attachment
    # for .bat
    log.info(str(sys.argv))
    if len(sys.argv) == 2: # python SCB_FPS_Report.py YYYYMMDD
        Settlement_Date = sys.argv[1]
    else: # python SCB_FPS_Report.py
        Settlement_Date = datetime.datetime.now().strftime("%Y%m%d")
    # Settlement_Date = '20220318'
    Transaction_Date = (datetime.datetime.strptime(Settlement_Date,"%Y%m%d") + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    email_Transaction_date = (datetime.datetime.strptime(Settlement_Date, '%Y%m%d') + datetime.timedelta(days=-1)).strftime(
        "%d/%m/%Y")

    # get email attachment
    result, has_attachment = get_email_attachment()
    if not result:
        log.info(notify_email_content)
        return
    else:
        if not has_attachment:
            notify_email_content = 'Email existing...but no attachment...'
            log.info(notify_email_content)
            return
    # check SFTP file exist or not
    sftp_root_path = '/scbfps/'
    sftp_file_name = f'{Transaction_Date}_37182042233.csv'
    if sftp.checkSftpFile(SFTP_info[3], remotepath=sftp_root_path + sftp_file_name):
        notify_email_content = "Already uploaded the report, no need to upload again. if you want to re-upload, please delete the sftp report and then run this program again. Thanks."
        log.info(notify_email_content)
        return
    else:
        Email_attachment = os.path.join(extract_folder, f'{Transaction_Date}_HKD_TransactionInformation.csv')
        # upload file to SFTP
        sftp.putSftpFile(SFTP_info[3], localpath=Email_attachment, remotepath=sftp_root_path + sftp_file_name)
    # upload report success
    email_result = True
    notify_email_content = 'SCB FPS Report Upload Result Success'
    log.info(notify_email_content)
    return

def get_email_attachment():
    global notify_email_content
    result = False
    has_email = False
    has_attachment = False
    if Email_info[2][10] == 'Y': # Email_info[2][8] = imap SSL, "Y" = SSL, "N" == Non SSL
        imap = imaplib.IMAP4_SSL(host=Email_info[2][6], port=Email_info[2][7])
    else:
        imap = imaplib.IMAP4(host=Email_info[2][6], port=Email_info[2][7])
    # Email_info[2][8] = username, Email_info[2][9] = password
    imap.login(Email_info[2][8], Email_info[2][9])
    # choose inbox folder
    status, email_count = imap.select("INBOX")
    if status != 'OK':
        notify_email_content = 'search email Failed'
        return False
    # total number of emails
    email_count = int(email_count[0])
    exit_flag = False
    for i in range(email_count, 1, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            # Parse the raw email message in to a convenient object
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                log.info('===== Email details =====')
                email_From = msg["from"]
                log.info(f'From: {email_From}')
                email_To = msg["to"]
                log.info(f'To: {email_To}')
                email_Cc = msg["cc"]
                log.info(f'Cc: {email_Cc}')
                email_Bcc = msg["bcc"]
                log.info(f'Bcc: {email_Bcc}')
                index = msg["Subject"].find('=?')
                email_subject, encoding = decode_header(msg["Subject"][index:])[0]
                # email_subject, encoding = decode_header(msg["Subject"])
                if encoding:
                    email_subject = email_subject.decode(encoding,'ignore')

                log.info(f'Subject: {email_subject}')
                # check email subject
                search_subject = f'FPS Fund Collection Report - {email_Transaction_date}'
                log.info(f'search_subject: {search_subject}')
                if search_subject not in email_subject:
                    notify_email_content = "didn't found related email subject"
                    log.info('Not this email...Next')
                    continue
                # if the email message is multipart
                has_email = True
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
                        # check email attachment
                        if "attachment" in content_disposition:
                            # download attachment
                            attachment_name = part.get_filename()
                            attachment_filepath = os.path.join(Root_Folder, attachment_name)
                            log.info(f'attachment_name: {attachment_name}')
                            if attachment_name:
                                if not os.path.isdir(Root_Folder):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(Root_Folder)
                                # download attachment and save it
                                open(attachment_filepath, "wb").write(part.get_payload(decode=True))
                                # create extract folder
                                global extract_folder
                                extract_folder = os.path.join(Root_Folder, attachment_name.replace('.zip', ''))
                                if not os.path.exists(extract_folder):
                                    os.mkdir(extract_folder)
                                # unzip file attachment
                                if not Utility.unzip_file(file_path=attachment_filepath, extract_folder=extract_folder, password='62352233'):
                                    notify_email_content = 'unzip attachment failed'
                                    imap.close()
                                    imap.logout()
                                    return False
                                has_attachment = True
                    result = True
                    exit_flag = True
                    break
                else: # no attachment
                    result = True
                    exit_flag = True
                    has_attachment = False
                if exit_flag:
                    break
            if exit_flag:
                break
        if exit_flag:
            break
    # close the connection and logout
    imap.close()
    imap.logout()
    return result, has_attachment

if __name__ == '__main__': # program 入口
    log.start('SCB_FPS_Report')
    main()
    Email.sentEmail(Log_Name='SCB_FPS_Report',
                    Email_subject=f'[{email_result}] SCB FPS Report Checking Result({email_Transaction_date})',
                    Email_content=notify_email_content,
                    Email_to=alert_email_to,
                    Email_attachement=Email_attachment,
                    Email_from=Email_info[0][3],
                    Email_displayName='SCB FPS Report')
    log.end('SCB_FPS_Report')