#!/usr/bin/python
from integralstor import zfs, audit
import sys

''' Used to run a ZFS pool scrub from a shell script '''

def main():
    if len(sys.argv) != 2:
        print 'Usage : python run_zfs_scrub.py pool_name'
        sys.exit(0)
    pool_name = sys.argv[1]
    ret, err = zfs.scrub_pool(pool_name)
    if err:
        print err
        sys.exit(-1)
    audit_str = "ZFS pool scrub initiated on pool %s" % pool_name
    audit.audit("scrub_zfs_pool", audit_str, None, system_initiated=True)
    sys.exit(0)

if __name__ == '__main__':
    main()


