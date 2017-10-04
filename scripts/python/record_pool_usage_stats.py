from integralstor import alerts, datetime_utils, audit, manifest_status, lock, logger, zfs, db, command, config

import logging
import sys
import shutil
import os
import glob

import atexit
atexit.register(lock.release_lock, 'record_pool_usage_stats')

'''
Record the pool usage stats for the current time.
'''


def main():
    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Pool usage stats record', scripts_log, level=logging.DEBUG)

        lck, err = lock.get_lock('record_pool_usage_stats')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')

        logger.log_or_print(
            'Pool usage stats collection initiated.', lg, level='info')
        ret, err = _record_pool_usage_stats()
        if err:
            raise Exception(err)

    except Exception, e:
        # print str(e)
        lock.release_lock('record_pool_usage_stats')
        logger.log_or_print('Error collecting pool usage stats : %s' %
                            e, lg, level='critical')
        return -1,  'Error collecting pool usage stats : %s' % e
    else:
        lock.release_lock('record_pool_usage_stats')
        logger.log_or_print(
            'Pool usage stats collection completed successfully.', lg, level='info')
        return 0, None


def _record_pool_usage_stats():
    try:
        pool_list, err = zfs.get_pools()
        if err:
            raise Exception(err)
        if pool_list:
            midnight, err = datetime_utils.get_epoch(when='midnight')
            if err:
                raise Exception(err)
            db_path, err = config.get_db_path()
            if err:
                raise Exception(err)
            for pool_info in pool_list:
                cmd_list = []
                cmd_list.append(["insert into pool_usage_stats(pool_name, date, used_bytes, available_bytes) values (?,?,?,?)", (
                    pool_info['pool_name'], midnight, pool_info['usage']['total_space_used_bytes'], pool_info['usage']['total_space_avail_bytes'],)])
                # Run multiple times as a duplicate entry will cause other
                # inserts to fail otherwise..
                ret, err = db.execute_iud(db_path, cmd_list)
            # Best effort.. continue if duplicate dates cause a problem when rerunning
            # print ret, err
    except Exception, e:
        # print str(e)
        return False, "Error recording ZFS pool usage statistics : %s" % str(e)
    else:
        return True, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
