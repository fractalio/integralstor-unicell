#!/usr/bin/python
import sys
import time

from integralstor_utils import config, lock, db
from integralstor import alerts

import atexit
import time
import datetime
atexit.register(lock.release_lock, 'integralstor_poll_for_alerts')


def main():
    try:
        lck, err = lock.get_lock('integralstor_poll_for_alerts')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock. Exiting.')

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
        if alert_list:
            alerts.record_alerts(alert_list)

        lock.release_lock('integralstor_poll_for_alerts')

    except Exception, e:
        print "Error generating alerts : %s ! Exiting." % str(e)
        sys.exit(-1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
