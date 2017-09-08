#!/usr/bin/python
import sys
from integralstor import remote_replication, datetime_utils, zfs


def run_zfs_remote_replication(remote_replication_id):
    try:
        rr, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception('Could not fetch replication details: %s' % err)
        replication = rr[0]
        mode = replication['mode']
        if mode == 'zfs':
            now_local_epoch, err = datetime_utils.get_epoch(when='now')
            if err:
                raise Exception(err)
            now_local_str, err = datetime_utils.convert_from_epoch(
                now_local_epoch, return_format='str', str_format='%Y%m%d%H%M', to='local')
            if err:
                raise Exception(err)

            source_dataset = replication['zfs'][0]['source_dataset']
            ret, err = zfs.create_snapshot(
                source_dataset, 'zrr_%s_%s' % (remote_replication_id, now_local_str))
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
