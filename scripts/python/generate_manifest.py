#!/usr/bin/python

import json
import os
import datetime
import shutil
import sys
import logging
from integralstor import manifest_status, lock, logger, config


def gen_manifest(path):
    try:
        lck, err = lock.get_lock('generate_manifest')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock.')
        ret, err = manifest_status.generate_manifest_info(rescan_for_disks = True)
        if not ret:
            if err:
                raise Exception(err)
            else:
                raise Exception('No manifest info obtained')
        else:
            fullpath = os.path.normpath("%s/master.manifest" % path)
            fulltmppath = "/tmp/master.manifest.tmp"
            fullcopypath = os.path.normpath(
                "%s/master.manifest.%s" % (path, datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S")))
            # Generate into a tmp file
            with open(fulltmppath, 'w') as fd:
                json.dump(ret, fd, indent=2)
            # Copy original to a backup
            if os.path.isfile(fullpath):
                shutil.copyfile(fullpath, fullcopypath)
            # Now move the tmp to the actual manifest file name
            shutil.move(fulltmppath, fullpath)
    except Exception, e:
        lock.release_lock('generate_manifest')
        return -1, 'Error generating manifest : %s' % str(e)
    else:
        lock.release_lock('generate_manifest')
        return 0, None


import atexit
atexit.register(lock.release_lock, 'generate_manifest')


def main():

    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Generate manifest', scripts_log, level=logging.DEBUG)
        logger.log_or_print('Generate manifest initiated.', lg, level='info')

        num_args = len(sys.argv)
        if num_args > 1:
            path = sys.argv[1]
        else:
            path, err = config.get_system_status_path()
            if err:
                raise Exception(err)
            if not path:
                path = '/tmp'
        logger.log_or_print("Generating the manifest in %s" %
                            path, lg, level='info')
        rc, err = gen_manifest(path)
        if err:
            raise Exception(err)
        # print rc
    except Exception, e:
        str = "Error generating manifest file : %s" % e
        logger.log_or_print(str, lg, level='critical')
        return -1
    else:
        logger.log_or_print(
            'Generate manifest completed successfully', lg, level='info')
        return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
