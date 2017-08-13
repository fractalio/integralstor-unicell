#!/usr/bin/python
import sys
from integralstor_utils import zfs
from integralstor import remote_replication
from datetime import datetime


def run_zfs_remote_replication(remote_replication_id):
    try:
        rr, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception('Could not fetch replication details: %s' % err)
        replication = rr[0]
        mode = replication['mode']
        if mode == 'zfs':
            source_dataset = replication['zfs'][0]['source_dataset']
            now = datetime.now()
            now_str = now.strftime('%Y-%m-%d-%H-%M')
            ret, err = zfs.create_snapshot(
                source_dataset, 'zfs_remote_repl_%s' % now_str)
            if err:
                raise Exception(err)
            ret, err = remote_replication.run_zfs_remote_replication(
                remote_replication_id)
            if err:
                raise Exception(err)
        else:
            raise Exception('Invalid remote replication mode')

    except Exception, e:
        return False, 'Error adding ZFS remote replication task : %s' % e
    else:
        return True, None


if __name__ == '__main__':
    # print sys.argv
    if len(sys.argv) != 2:
        print 'Usage : python run_zfs_remote_replication.py remote_replication_id'
        sys.exit(-1)
    ret, err = run_zfs_remote_replication(sys.argv[1])
    print ret, err
    if err:
        sys.exit(-1)
    sys.exit(0)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
