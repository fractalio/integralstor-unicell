from integralstor import alerts, datetime_utils, audit, manifest_status, lock, logger, db, command, config

import logging
import sys
import os
import zipfile

import atexit
atexit.register(lock.release_lock, 'generate_current_logs_archive')

'''
Generates a zip file of all the files in the /var/log/integralstor directory except for the archive directory.
'''

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Current logs archive generation', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)

        lck, err = lock.get_lock('generate_current_logs_archive')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print('Current logs archive generation initiated.', lg, level='info')

        now_local_epoch, err = datetime_utils.get_epoch(when='now')
        if err:
            raise Exception(err)
        now_local_str, err = datetime_utils.convert_from_epoch(now_local_epoch, return_format='str', str_format = '%Y_%m_%d_%H_%M', to='local')
        if err:
            raise Exception(err)

        zf_name = 'IntegralSTOR_system_logs_%s.zip'%now_local_str
        try:
            os.makedirs('/var/log/integralstor/archives/log_archives/')
        except:
            pass

        zf = zipfile.ZipFile('/var/log/integralstor/archives/log_archives/%s'%zf_name, 'w')
        for root, dirs, files in os.walk('/var/log/integralstor'):
            if root.startswith('/var/log/integralstor/archives'):
                continue
            for file in files:
                #print '%s/%s'%(root[len('/var/log/integralstor/'):], file)
                zf.write(os.path.join(root, file), '%s/%s'%(root[len('/var/log/integralstor/'):], file))
        zf.close()
    except Exception, e:
        #print str(e)
        lock.release_lock('generate_current_logs_archive')
        logger.log_or_print('Error generating current logs archive : %s' %
                            e, lg, level='critical')
        return -1,  'Error generating current logs archive: %s' % e
    else:
        lock.release_lock('generate_current_logs_archive')
        logger.log_or_print(
            'Current logs archive generated successfully.', lg, level='info')
        return 0, None

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

