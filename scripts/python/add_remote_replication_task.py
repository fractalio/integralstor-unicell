#!/usr/bin/python
import sys
from integralstor_utils import remote_replication, zfs
from datetime import datetime


def add_remote_replication_task(remote_replication_id):
    try:
        rr, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception('Could not fetch replication details: %s' % err)
        replication = rr[0]
        mode = replication['mode']

        if mode == 'zfs':
            zfs_entries = replication['zfs'][0]
            source_dataset = zfs_entries['source_dataset']
            target_ip = zfs_entries['target_ip']
            target_pool = zfs_entries['target_pool']
            target_user_name = zfs_entries['target_user_name']
            description = replication['description']
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d-%H-%M')
            ret, err = zfs.create_snapshot(
                source_dataset, 'remote_repl_snap_%s' % now_str)
            if err:
                raise Exception(err)

            ret, err = remote_replication.schedule_remote_replication(
                description, mode, {'source_dataset': source_dataset, 'target_ip': target_ip, 'target_user_name': target_user_name, 'target_pool': target_pool})
            if err:
                raise Exception(err)

        elif mode == 'rsync':
            rsync_entries = replication['rsync'][0]
            rsync_type = rsync_entries['rsync_type']
            source_path = rsync_entries['source_path']
            target_path = rsync_entries['target_path']
            short_switches = rsync_entries['short_switches']
            long_switches = rsync_entries['long_switches']
            target_user_name = rsync_entries['target_user_name']
            target_ip = rsync_entries['target_ip']
            description = replication['description']

            ret, err = remote_replication.schedule_remote_replication(
                description, mode, {'rsync_type': rsync_type, 'source_path': source_path, 'target_path': target_path, 'short_switches': short_switches, 'long_switches': long_switches, 'target_ip': target_ip, 'target_user_name': target_user_name})
            if err:
                raise Exception(err)
    except Exception, e:
        return False, 'Error adding a remote replication task : %s' % e
    else:
        return True, None


if __name__ == '__main__':
    # print sys.argv
    if len(sys.argv) != 2:
        print 'Usage : python add_remote_replication_task.py remote_replication_id'
        sys.exit(-1)
    ret, err = add_remote_replication_task(sys.argv[1])
    print ret, err
    if err:
        sys.exit(-1)
    sys.exit(0)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
