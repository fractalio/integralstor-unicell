#!/usr/bin/python
import sys
import time
import logging

from integralstor_utils import config, lock, db, logger
from integralstor import alerts, system_info

import atexit
import time
import datetime
atexit.register(lock.release_lock, 'integralstor_poll_for_alerts')


def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Poll for alerts', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)

        lck, err = lock.get_lock('integralstor_poll_for_alerts')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock. Exiting.')

        logger.log_or_print('Poll for alerts initiated.', lg, level='info')

        now = int(time.time())

        db_path, err = config.get_db_path()
        if err:
            raise Exception(err)

        tasks_query = "select * from tasks where last_run_time > '%d' and (status = 'error-retrying' or status = 'failed');" % (
            now - 110)
        # print "\ntasks_query: ", tasks_query
        rows, err = db.get_multiple_rows(db_path, tasks_query)
        # print "\nrows: ", rows
        if err:
            raise Exception(err)

        alert_list = None
        if rows:
            for row in rows:
                if row['status'] == 'error-retrying':
                    alert_list.append({ 'subsystem_type_id': 7, 'severity_type_id': 2, 'component' : row['description'], 'alert_str' : "Task: %s failed but will be retried." % row['description']})
                elif row['status'] == 'failed':
                    alert_list.append({ 'subsystem_type_id': 7, 'severity_type_id': 3, 'component' : row['description'], 'alert_str' : "Task: %s failed." % row['description']})

        # print "\nalert_list: ", alert_list

        hw_platform, err = config.get_hardware_platform()
        if hw_platform:
            if hw_platform == 'dell':
                from integralstor_utils.platforms import dell
                alerts_dict, err = dell.get_alert_logs()
                if alerts_dict:
                    current_time = int(time.time())
                    for time_stamp, alerts_list in alerts_dict.items():
                        for alert_dict in alerts_list:
                            if alert_dict['Severity'] == 'Critical':
                                if (current_time - time_stamp) < (60 * 60):
                                    alert_list.append({ 'subsystem_type_id': 5, 'severity_type_id': 3, 'component' : 'Dell Hardware component', 'alert_str' : alert_dict['description']})
                                    # print time_stamp, alert_dict
        if alert_list:
            alerts.record_alerts(alert_list)

        lock.release_lock('integralstor_poll_for_alerts')

    except Exception, e:
        print "Error generating alerts : %s ! Exiting." % str(e)
        logger.log_or_print('Error polling for alerts : %s' %
                            e, lg, level='critical')
        return -1
    else:
        logger.log_or_print(
            'Poll for alerts completed successfully.', lg, level='info')
        return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
