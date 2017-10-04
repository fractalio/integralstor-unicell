#!/usr/bin/python
import os.path
import sys
import glob
import logging

from integralstor import datetime_utils, lock, logger, config

import atexit
atexit.register(lock.release_lock, 'remove_old_files')

'''
Remove all files that are older than the specified number of days that match the glob patterns given below.
'''


def remove_old_files(lg=None, older_than_days=7):
    try:
        lck, err = lock.get_lock('remove_old_files')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')
        exported_logs_dir, err = config.get_exported_logs_dir_path()
        if err:
            raise Exception(err)
        status_report_dir, err = config.get_status_reports_dir_path()
        if err:
            raise Exception(err)
        patterns = [exported_logs_dir + '/alerts_*', status_report_dir + '/*']
        now, err = datetime_utils.get_epoch()
        # print now
        for pattern in patterns:
            list = glob.glob(pattern)
            for f in list:
                # print f
                ctime = os.path.getctime(f)
                # print os.path.getctime(f)
                if (now - ctime) > (60 * 60 * 24 * older_than_days):
                    # print 'removing %s'%f
                    os.remove(f)
                else:
                    # print 'not removing %s'%f
                    pass
    except Exception, e:
        logger.log_or_print('Error removing old files: %s' %
                            e, lg, level='critical')
        lock.release_lock('remove_old_files')
        return -1,  str(e)
    else:
        lock.release_lock('remove_old_files')
        return 0, None


def main():
    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Remove old files', scripts_log, level=logging.DEBUG)

        logger.log_or_print('Old file removal initiated.', lg, level='info')
        if len(sys.argv) != 2:
            raise Exception(
                'Usage : python remove_old_files.py <older_than_days>')
        older_than_days = int(sys.argv[1])
        ret, err = remove_old_files(lg, older_than_days)
        if err:
            raise Exception(err)
    except Exception, e:
        str = "Error removing old files: %s" % e
        print str
        logger.log_or_print(str, lg, level='critical')
        sys.exit(-1)
    else:
        logger.log_or_print(
            'Old file removal completed successfully.', lg, level='info')
        sys.exit(0)


if __name__ == "__main__":
    main()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
