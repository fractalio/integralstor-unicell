from integralstor import alerts, audit, mail
from integralstor_utils import db, logger, lock

import logging
import sys
import datetime

import atexit
atexit.register(lock.release_lock, 'purge_db')

'''
Purge the DB of all old unwanted entries based on certain criteria
'''

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Purge database', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)

        logger.log_or_print('Database purge initiated.', lg, level='info')
        if len(sys.argv) != 4:
            raise Exception('Usage : python purge_db.py <alerts_older_than_x_days> <min_audits_to_export> <audit_export_count')
        lck, err = lock.get_lock('purge_db')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock. Exiting.')
        alerts_days = sys.argv[1]
        audit_min_to_export = int(sys.argv[1])
        audit_export_count = int(sys.argv[2])

        ret, err = alerts.export_old_alerts(int(alerts_days))
        if err:
            raise Exception(err)

        ret, err = audit.export_old_audits(audit_min_to_export, audit_export_count)
        if err:
            raise Exception(err)

        ret, err = mail.purge_email_queue(7)
        if err:
            raise Exception(err)

    except Exception, e:
        #print str(e)
        logger.log_or_print('Error purging database: %s' %
                            e, lg, level='critical')
        lock.release_lock('purge_db')
        return -1,  'Error purging database : %s' % e
    else:
        logger.log_or_print(
            'Database purge completed successfully.', lg, level='info')
        lock.release_lock('purge_db')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

