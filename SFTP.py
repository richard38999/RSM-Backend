import pysftp
import Logger
log = None
class init():

    def __init__(self, LogName):
        global log
        log = Logger.Log(LogName)
    def getSftpFile(self, SFTP_info, remotepath=None, localpath=None):
        log.start('getSftpFile')
        log.info('start Connection')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
        log.info('end Connection')
        log.info('start get file, localpath: {0}'.format(localpath))
        log.info('start get file, remotepath: {0}'.format(remotepath))
        sftp.get(remotepath, localpath=localpath)
        log.info('end get file')
        log.info('start SFTP close')
        sftp.close()
        log.info('end SFTP close')
        log.end('getSftpFile')
    def putSftpFile(self, SFTP_info, localpath=None, remotepath=None):
        log.start('putSftpFile')
        log.info('start Connection')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
        log.info('end Connection')
        log.info('start put file, localpath: {0}'.format(localpath))
        log.info('start put file, remotepath: {0}'.format(remotepath))
        sftp.put(localpath, remotepath=remotepath)
        log.info('end put file')
        log.info('start SFTP close')
        sftp.close()
        log.info('end SFTP close')
        log.end('putSftpFile')
    def checkSftpFile(self, SFTP_info, remotepath=None):
        isExist = None
        log.start('checkSftpFile')
        log.info('start Connection')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(host=SFTP_info[0], port=SFTP_info[1], username=SFTP_info[2], password=SFTP_info[3], cnopts=cnopts)
        log.info('end Connection')
        log.info('start check file, remotepath: {0}'.format(remotepath))
        isExist = sftp.exists(remotepath)
        log.info('end check file')
        log.info(f'remote file isExist: {isExist}')
        log.info('start SFTP close')
        sftp.close()
        log.info('end SFTP close')
        log.end('checkSftpFile')
        return isExist