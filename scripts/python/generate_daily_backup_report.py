#!/usr/bin/python
from integralstor import lock, logger, config, urbackup

import sys
import logging
import atexit
atexit.register(lock.release_lock, 'generate_backup_report')

'''
Generate a PDF report of UrBackup backups of IntegralSTOR system.
'''

def main():
    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'IntegralSTOR backup report generation', scripts_log, level=logging.DEBUG)
        urb_reports_dir, err = config.get_urbackup_reports_dir_path()
        if err:
            raise Exception(err)

        lck, err = lock.get_lock('generate_backup_report')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print('IntegralSTOR backup report generation initiated.', lg, level='info')
        ret, err = urbackup.generate_todays_pdf_report()
        if err:
            raise Exception(err)

    except Exception, e:
        #print str(e)
        lock.release_lock('generate_backup_report')
        logger.log_or_print('Error generating IntegralSTOR backup report: %s' %
                            e, lg, level='critical')
        return -1,  'Error generating IntegralSTOR backup report : %s' % e
    else:
        lock.release_lock('generate_urbackup_report')
        logger.log_or_print(
            'IntegralSTOR backup report generated successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

