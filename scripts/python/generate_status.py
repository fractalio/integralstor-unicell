#!/usr/bin/python

from integralstor import alerts, manifest_status, lock, logger, config
import json
import os
import shutil
import datetime
import sys
import re
import logging
import pprint


def gen_status(path, lg=None):
    try:
        lck, err = lock.get_lock('generate_status')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Generate Status : Could not acquire lock.')
        fullmanifestpath = os.path.normpath("%s/master.manifest" % path)
        ret, err = manifest_status.generate_status_info(fullmanifestpath)
        if not ret:
            if err:
                raise Exception(err)
            else:
                raise Exception('No status info obtained')
        if ret and ('errors' in ret) and ret['errors']:
            retval, err = alerts.record_alerts(ret['errors'])
            #print retval, err
        fullpath = os.path.normpath("%s/master.status" % path)
        fulltmppath = "/tmp/master.status.tmp"
        # Generate into a tmp file
        with open(fulltmppath, 'w') as fd:
            json.dump(ret, fd, indent=2)
        # Now move the tmp to the actual manifest file name
        # print 'fullpath is ', fullpath
        shutil.move(fulltmppath, fullpath)
    except Exception, e:
        logger.log_or_print('Error generating status : %s' %
                            e, lg, level='critical')
        lock.release_lock('generate_status')
        return -1,  'Error generating status : %s' % e
    else:
        lock.release_lock('generate_status')
        return 0, None


import atexit
atexit.register(lock.release_lock, 'generate_status')


def main():

    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Generate status', scripts_log, level=logging.DEBUG)

        logger.log_or_print('Generate status initiated.', lg, level='info')

        platform, err = config.get_platform()
        if err:
            raise Exception(err)

        default_path = False

        num_args = len(sys.argv)

        if num_args > 1:
            path = sys.argv[1]
        else:
            default_path = True
            path, err = config.get_system_status_path()
            if err:
                raise Exception(err)
            if not path:
                path = '/tmp'
        # print platform, path

        logger.log_or_print("Generating the status in %s" %
                            path, lg, level='info')
        rc, err = gen_status(path, lg)
        if err:
            raise Exception(err)
        # print rc
    except Exception, e:
        str = "Error generating status file : %s" % e
        logger.log_or_print(str, lg, level='critical')
        sys.exit(-1)
    else:
        logger.log_or_print(
            'Generate status completed successfully.', lg, level='info')
        sys.exit(0)


if __name__ == "__main__":
    main()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
