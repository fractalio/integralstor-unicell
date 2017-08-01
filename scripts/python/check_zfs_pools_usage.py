from integralstor import alerts
from integralstor_utils import db, logger, command, zfs, lock

import logging
import sys

import atexit
atexit.register(lock.release_lock, 'check_zfs_pools_usage')

'''
Checks the space utilization of the ZFS pools and raises alerts based on the warning and critical percentages passed
'''

def main():
    lg = None
    try:
        stop_services = False
        lg, err = logger.get_script_logger(
            'ZFS pool usage check', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)

        lck, err = lock.get_lock('check_zfs_pools_usage')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print('ZFS pool usage check initiated.', lg, level='info')
        if len(sys.argv) != 3:
            raise Exception('Usage : python check_zfs_pools_usage.py <warning_percentage> <critical_percentage>')
        warning_percentage = int(sys.argv[1])
        critical_percentage = int(sys.argv[2])

        pool_list, err = zfs.get_pools()
        if err:
            raise Exception(err)
        alerts_list = []
        for pool_info in pool_list:
            percentage = float(pool_info['usage']['used_percent'])

            alert = False
            if percentage > critical_percentage:
                severity_str = 'CRITICAL'
                severity_type = 3
                alert = True
                print_percentage = critical_percentage
                logger.log_or_print('ZFS pool %s is %d%% full.' %(pool_info['pool_name'], int(percentage)), lg, level='critical')
            elif percentage > warning_percentage:
                severity_type = 2
                severity_str = 'warning'
                print_percentage = warning_percentage
                alert = True
            if alert:
                alert_str = 'ZFS pool %s has exceeded the %s threshold capacity of %d%% and is now %d%% full.'%(pool_info['pool_name'], severity_str, print_percentage, percentage)
                alerts_list.append({'subsystem_type_id': 6, 'severity_type_id': severity_type, 'component' : pool_info['pool_name'], 'alert_str' : alert_str})
        if alerts_list:
            retval, err = alerts.record_alerts(alerts_list)
            if err:
                raise Exception(err)
    except Exception, e:
        #print str(e)
        lock.release_lock('check_zfs_pools_usage')
        logger.log_or_print('Error checking ZFS pool usage: %s' %
                            e, lg, level='critical')
        return -1,  'Error checking ZFS pool usage : %s' % e
    else:
        lock.release_lock('check_zfs_pools_usage')
        logger.log_or_print(
            'ZFS pool usage check completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

