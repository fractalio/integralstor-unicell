from integralstor import alerts, datetime_utils, audit, manifest_status
from integralstor_utils import db, logger, command, zfs, lock, disks, config

import logging
import sys
import shutil
import os
import glob

import atexit
atexit.register(lock.release_lock, 'generate_system_status_report')

'''
Generate a text report of the status of the IntegralSTOR system.
'''

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'System status report generation', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)

        lck, err = lock.get_lock('generate_system_status_report')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print('System status report generation initiated.', lg, level='info')
        if len(sys.argv) != 2:
            raise Exception('Usage : python generate_system_status_report.py <past_x_days>')
        past_x_days = int(sys.argv[1])
        start_time, err = datetime_utils.get_epoch(when='midnight', num_previous_days=past_x_days)
        if err:
            raise Exception(err)
        now, err = datetime_utils.get_epoch(when='now')
        if err:
            raise Exception(err)
        now_local_str, err = datetime_utils.convert_from_epoch(now, return_format='str', str_format = '%Y_%m_%d_%H_%M', to='local')
        if err:
            raise Exception(err)
        tmp_file_name = 'integralstor_status_%s'%now_local_str
        tmp_file_name_with_path = '/tmp/%s'%tmp_file_name
        with open(tmp_file_name_with_path, 'w') as f:
            ret, err = generate_global_header(f)
            f.write('\n')
            ret, err = generate_cpu_section(f)
            f.write('\n\n')
            ret, err = generate_memory_section(f)
            f.write('\n\n')
            ret, err = generate_dmidecode_section(f)
            print ret, err
            f.write('\n\n')
            hw_platform, err = config.get_hardware_platform()
            if hw_platform:
                if hw_platform == 'dell':
                    ret, err = generate_dell_hw_status(f)
                    f.write('\n\n')
            ret, err = generate_alerts_section(f, start_time)
            f.write('\n\n')
            ret, err = generate_audits_section(f, start_time)
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'nmcli con', 'Networking connections')
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'ip addr', 'IP addresses')
            f.write('\n\n')
            ret, err = generate_disks_status_section(f)
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'df -HT --exclude-type=devtmpfs --exclude-type=tmpfs --exclude-type=zfs', 'OS disk space usage')
            f.write('\n\n')
            ret, err = generate_zfs_info_section(f)
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'zpool list', 'ZFS pool space usage')
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'zfs list -t filesystem -o name,used,avail,refer,mountpoint,dedup,compression,quota,xattr,recordsize,acltype', 'ZFS datasets')
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'zfs list -t volume -o name,used,avail,refer,mountpoint,dedup,compression,volsize,volblocksize', 'ZFS zvols')
            f.write('\n\n')
            ret, err = generate_command_based_section(f, 'zpool status -v', 'ZFS pool status')
            f.write('\n\n')
        try:
            os.makedirs('/var/log/integralstor/reports/integralstor_status')
        except:
            pass
        shutil.move(tmp_file_name_with_path, '/var/log/integralstor/reports/integralstor_status/%s'%tmp_file_name)

    except Exception, e:
        #print str(e)
        lock.release_lock('generate_system_status_report')
        logger.log_or_print('Error generating system status report : %s' %
                            e, lg, level='critical')
        return -1,  'Error generating system status report : %s' % e
    else:
        lock.release_lock('generate_system_status_report')
        logger.log_or_print(
            'System status report generated successfully.', lg, level='info')
        return 0, None

def generate_global_header(f):
    try:
        ep, err = datetime_utils.get_epoch(when='now')
        if err:
            raise Exception(err)
        date_str, err = datetime_utils.convert_from_epoch(ep, return_format='str', str_format = '%Y/%m/%d %H:%M', to='local')
        if err:
            raise Exception(err)
        ver, err = config.get_version()
        if err:
            raise Exception(err)
        f.write('\n\n')
        f.write('################### IntegralSTOR system status report ####################\n\n')
        f.write('                    IntegralSTOR version : %s                                 \n\n'%ver)
        f.write('                    Report generated at : %s                                 \n\n'%date_str)
        f.write('##########################################################################\n\n')
        f.write('\n\n')
    except Exception, e:
        return False, 'Error generating global header : %s'%str(e)
    else:
        return True, None

def generate_cpu_section(f):
    try:
        cpu_info, err = manifest_status.get_cpu_model()
        if err:
            raise Exception(err)
        cpu_cores, err = manifest_status.get_cpu_cores()
        if err:
            raise Exception(err)
        f.write( '--------------------- CPU info BEGIN ------------------------\n\n')
        f.write( 'CPU Type : %s\n'%cpu_info)
        f.write( 'Number of cores : %s\n'%cpu_cores)
        f.write( '\n')
        f.write( '--------------------- CPU info END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating CPU section: %s'%str(e)
    else:
        return True, None

def generate_dell_hw_status(f):
    try:
        hw_platform, err = config.get_hardware_platform()
        if hw_platform:
            if hw_platform == 'dell':
                f.write( '--------------------- Dell hardware status BEGIN ------------------------\n\n')
                from integralstor_utils.platforms import dell
                psu_status, err = dell.get_psu_status()
                if err:
                    raise Exception(err)
                f.write( 'Number of PSUs detected : %d\n'%psu_status['psu_count'])
                f.write( 'PSU redundancy : ' + ('Redundancy present' if psu_status['redundancy'] else 'No redundancy') + '\n')
                for index, psu in enumerate(psu_status['psu_list']):
                    f.write( 'PSU %d prescence'%index + ('Present' if psu_psu['prescence'] else 'Not present') + '\n')
                    f.write( 'PSU %d switch on status'%index + ('On' if psu_psu['switch_on'] else 'Off') + '\n')
                    f.write( 'PSU %d status'%index + ('Failed' if psu_psu['failure'] else 'OK') + '\n')
                    f.write( '\n')
                f.write( '--------------------- Dell hardware status END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating Dell hardware statussection: %s'%str(e)
    else:
        return True, None

def generate_memory_section(f):
    try:
        mem_info, err = manifest_status.get_mem_info()
        if err:
            raise Exception(err)
        f.write( '--------------------- RAM info BEGIN ------------------------\n\n')
        f.write( 'Total memory : %3.2f %s\n'%(mem_info['mem_total']['value'], mem_info['mem_total']['unit']))
        f.write( 'Free memory : %3.2f %s\n'%(mem_info['mem_free']['value'], mem_info['mem_free']['unit']))
        f.write( '\n')
        f.write( '--------------------- RAM info END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating CPU section: %s'%str(e)
    else:
        return True, None

def generate_zfs_info_section(f):
    try:
        zfs_ver, err = manifest_status.get_zfs_version()
        if err:
            raise Exception(err)
        f.write( '--------------------- ZFS info BEGIN ------------------------\n\n')
        f.write( 'ZFS version : %s\n'%zfs_ver)
        count, err = _get_count('filesystem')
        if err:
            raise Exception(err)
        f.write( 'Number of ZFS datasets: %d\n'%count)
        count, err = _get_count('volume')
        if err:
            raise Exception(err)
        f.write( 'Number of ZFS zvols: %d\n'%count)
        count, err = _get_count('snapshot')
        if err:
            raise Exception(err)
        f.write( 'Number of ZFS snapshots: %d\n'%count)
        f.write( '\n')
        f.write( '--------------------- ZFS info END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating CPU section: %s'%str(e)
    else:
        return True, None

def _get_count(type):
    ret = -1
    try:
        if type not in ['filesystem', 'volume', 'snapshot']:
            raise Exception('Invalid zfs type specified : %s'%type)
        lines, err = command.get_command_output('zfs list -H -t %s | wc -l'%type, shell=True)
        if err:
            raise Exception(err)
        ret = int(lines[0].strip())
    except Exception, e:
        return None, 'Error generating ZFS count : %s'%str(e)
    else:
        return ret, None

def generate_alerts_section(f, start_time):
    try:
        alerts_list, err = alerts.get_alerts(start_time = start_time)
        if err:
            raise Exception(err)
        #print alerts_list
        f.write( '--------------------- Recent alerts BEGIN ------------------------\n\n')
        for al in alerts_list:
            f.write( 'Subsystem : %s\n'%al['subsystem'])
            f.write( 'Severity : %s\n'%al['severity'])
            f.write( 'Alert message : %s\n'%al['alert_str'])
            f.write( 'First reported at : %s\n'%al['first_alert_time'])
            f.write( 'Last reported at : %s\n'%al['last_update_time'])
            f.write( 'Repeated  %d times in the last 15 minutes.\n'%al['repeat_count'])
            f.write( '\n')
        f.write( '--------------------- Recent alerts END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating alerts section: %s'%str(e)
    else:
        return True, None

def generate_audits_section(f, start_time):
    try:
        audit_list, err = audit.get_entries(start_time = start_time)
        if err:
            raise Exception(err)
        #print audit_list
        f.write( '--------------------- Recent audited actions BEGIN ------------------------\n\n')
        for au in audit_list:
            f.write( 'Action performed : %s\n'%au['action'])
            f.write( 'Action performed by : %s\n'%au['username'])
            f.write( 'Action performed at : %s\n'%au['time'])
            f.write( 'Action details : %s\n'%au['action_str'])
            f.write( '\n')
        f.write( '--------------------- Recent audited actions END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating audit section: %s'%str(e)
    else:
        return True, None

def generate_disks_status_section(f):
    try:
        disk_names, err = disks.get_all_disks_by_name()
        if err:
            raise Exception(err)
        #print audit_list
        f.write( '--------------------- Disk status BEGIN ------------------------\n\n')
        for dn_dict in disk_names:
            cmd = 'smartctl --all %s'%dn_dict['full_path']
            #print cmd
            ret, err = command.execute(cmd)
            if err:
                raise Exception(err)
            lines, err = command.get_output_list(ret)
            if err:
                raise Exception(err)
            f.write( '\n'.join(lines))
            f.write( '\n')
        f.write( '--------------------- Disk status END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating disk status section: %s'%str(e)
    else:
        return True, None

def generate_command_based_section(f, cmd, section_name):
    try:
        lines, err = command.get_command_output(cmd)
        if err:
            raise Exception(err)
        f.write( '--------------------- %s BEGIN ------------------------\n\n'%section_name)
        f.write( '\n'.join(lines))
        f.write( '\n')
        f.write( '--------------------- %s END ------------------------\n\n'%section_name)
    except Exception, e:
        return False, 'Error generating %s section: %s'%(section_name, str(e))
    else:
        return True, None

def generate_dmidecode_section(f):
    try:
        f.write( '--------------------- Hardware information BEGIN------------------------\n\n')
        lines, err = command.get_command_output('dmidecode -s system-manufacturer')
        f.write( 'System manufacturer : %s\n'%lines[0])
        lines, err = command.get_command_output('dmidecode -s system-product-name')
        f.write( 'System product name : %s\n'%lines[0])
        lines, err = command.get_command_output('dmidecode -s system-version')
        f.write( 'System version : %s\n'%lines[0])
        lines, err = command.get_command_output('dmidecode -s system-serial-number')
        f.write( 'System serial number (service tag) : %s\n'%lines[0])
        f.write( '\n')
        f.write( '--------------------- Hardware information END ------------------------\n\n')
    except Exception, e:
        return False, 'Error generating hardware information section: %s'%(str(e))
    else:
        return True, None

if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

