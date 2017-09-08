from integralstor import alerts, lock, services_management, disks, logger, db, command, config

import logging
import sys

import atexit
atexit.register(lock.release_lock, 'check_os_filesystems')

'''
Checks the OS filesystems usage and raises apropriate warnings.If it reaches the critical level then user data services are stopped.
'''

def main():
    lg = None
    try:
        stop_services = False
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'OS file system check', scripts_log, level=logging.DEBUG)

        lck, err = lock.get_lock('check_os_filesystems')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print('OS filesystem check initiated.', lg, level='info')

        if len(sys.argv) != 3:
            raise Exception('Usage : python check_os_filesystems.py <warning_percentage> <critical_percentage>')

        warning_percentage = int(sys.argv[1])
        critical_percentage = int(sys.argv[2])

        os_disk_stats, err = disks.get_os_partition_stats()
        if err:
            raise Exception(err)

        alerts_list = []
        for partition in os_disk_stats:
            fs_name = partition['fs_name']
            percentage_used = 100-partition['percentage_free']
            alert = False
            if percentage_used > critical_percentage:
                severity_str = 'CRITICAL'
                severity_type = 3
                alert = True
                print_percentage = critical_percentage
                if '/var' in fs_name: 
                    #print 'stopping services'
                    stop_services = True
                logger.log_or_print('OS filesystem %s full. Stopping all data services.' %fs_name, lg, level='critical')
            elif percentage_used > warning_percentage:
                severity_type = 2
                severity_str = 'warning'
                print_percentage = warning_percentage
                alert = True
            if alert:
                alert_str = 'Partition %s has exceeded the %s threshold capacity of %d%% and is now %d%% full.'%(fs_name, severity_str, print_percentage, percentage_used)
                if severity_type == 3:
                    alert_str += ' Stopping all data services now. Please clear up space before resuming these services.'
                alerts_list.append({'subsystem_type_id': 8, 'severity_type_id': severity_type, 'component' : fs_name, 'alert_str' : alert_str})
        if alerts_list:
            retval, err = alerts.record_alerts(alerts_list)
            if err:
                raise Exception(err)
        if stop_services:
            services = ['smb', 'winbind', 'nfs', 'vsftpd', 'urbackup-server']
            for service_name in services:
                services_management.update_service_status(service_name, 'stop')

    except Exception, e:
        #print str(e)
        lock.release_lock('check_os_filesystems')
        logger.log_or_print('Error checking OS filesystems : %s' %
                            e, lg, level='critical')
        return -1,  'Error checking OS filesystems : %s' % e
    else:
        lock.release_lock('check_os_filesystems')
        logger.log_or_print(
            'OS filesystems check completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

