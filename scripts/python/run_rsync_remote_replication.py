#!/usr/bin/python
import sys
from integralstor import remote_replication
# from datetime import datetime


def run_rsync_remote_replication(remote_replication_id):
    try:
        rr, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception('Could not fetch replication details: %s' % err)
        replication = rr[0]
        mode = replication['mode']

        if mode == 'rsync':
            rsync_entries = replication['rsync'][0]
            rsync_type = rsync_entries['rsync_type']
            source_path = rsync_entries['source_path']
            target_path = rsync_entries['target_path']
            short_switches = rsync_entries['short_switches']
            long_switches = rsync_entries['long_switches']
            target_user_name = rsync_entries['target_user_name']
            target_ip = rsync_entries['target_ip']
            description = replication['description']

            ret, err = remote_replication.run_rsync_remote_replication(
                description, {'rsync_type': rsync_type, 'source_path': source_path, 'target_path': target_path, 'short_switches': short_switches, 'long_switches': long_switches, 'target_ip': target_ip, 'target_user_name': target_user_name})
            if err:
                raise Exception(err)
        else:
            raise Exception('Invalid replication mode')

    except Exception, e:
        return False, 'Error adding rsync remote replication task : %s' % e
    else:
        return True, None


if __name__ == '__main__':
    # print sys.argv
    if len(sys.argv) != 2:
        print 'Usage : python run_rsync_remote_replication.py remote_replication_id'
        sys.exit(-1)
    ret, err = run_rsync_remote_replication(sys.argv[1])
    print ret, err
    if err:
        sys.exit(-1)
    sys.exit(0)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
