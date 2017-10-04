from integralstor import alerts, datetime_utils, audit, manifest_status, lock, logger, db, command, config

import logging
import sys
import zipfile
import os

import atexit
atexit.register(lock.release_lock, 'generate_current_config_archive')

'''
Generate a zip file of all the configuration related files.
'''


def main():
    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Current configuration archive generation', scripts_log, level=logging.DEBUG)
        config_archives_dir, err = config.get_config_archives_dir_path()
        if err:
            raise Exception(err)

        lck, err = lock.get_lock('generate_current_config_archive')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print(
            'Current config archive generation initiated.', lg, level='info')
        db_path, err = config.get_db_path()
        if err:
            raise Exception(err)
        pki_dir, err = config.get_pki_dir()
        if err:
            raise Exception(err)
        config_file_list = [('/etc/samba/smb.conf', 'smb.conf'), ('/etc/krb5.conf', 'krb5.conf'), (db_path, 'integral_view_config.db'), ('/etc/exports', 'exports'), ('/etc/vsftpd/vsftpd.conf',
                                                                                                                                                                      'vsftpd.conf'), ('/etc/tgt/targets.conf', 'targets.conf'), ('/etc/resolv.conf', 'resolv.conf'), ('/etc/hosts', 'hosts'), ('/etc/passwd', 'passwd'), ('/etc/group', 'group')]
        config_dir_list = [(pki_dir, 'pki')]

        now_local_epoch, err = datetime_utils.get_epoch(when='now')
        if err:
            raise Exception(err)
        now_local_str, err = datetime_utils.convert_from_epoch(
            now_local_epoch, return_format='str', str_format='%Y_%m_%d_%H_%M', to='local')
        if err:
            raise Exception(err)

        zf_name = 'IntegralSTOR_system_configuration_%s.zip' % now_local_str
        try:
            os.makedirs(config_archives_dir)
        except:
            pass

        try:
            zf = zipfile.ZipFile('%s/%s' % (config_archives_dir, zf_name), 'w')
            for entry in config_file_list:
                if os.path.exists(entry[0]):
                    zf.write(entry[0], arcname=entry[1])
            for entry in config_dir_list:
                if os.path.exists(entry[0]):
                    if entry[0][-1] == '/':
                        path = entry[0][:-1]
                    else:
                        path = entry[0]
                    for root, dirs, files in os.walk(path):
                        base = root[len(path) + 1:]
                        for file in files:
                            if base:
                                zf.write(os.path.join(root, file),
                                         '%s/%s/%s' % (entry[1], base, file))
                            else:
                                zf.write(os.path.join(root, file),
                                         '%s/%s' % (entry[1], file))
            zf.close()
        except Exception as e:
            raise Exception(
                "Error compressing log file : %s" % str(e))
    except Exception, e:
        # print str(e)
        lock.release_lock('generate_current_config_archive')
        logger.log_or_print('Error generating current config archive : %s' %
                            e, lg, level='critical')
        return -1,  'Error generating current config archive: %s' % e
    else:
        lock.release_lock('generate_current_conig_archive')
        logger.log_or_print(
            'Current configuration archive generated successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
