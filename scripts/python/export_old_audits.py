from integralstor import audit
from integralstor_utils import db, logger

import logging
import sys
import datetime

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Export old audit messages', '/var/log/integralstor/scripts.log', level=logging.DEBUG)
        logger.log_or_print('Processing export of old audits initiated.', lg, level='info')

        if len(sys.argv) != 3:
            raise Exception('Usage : python export_old_audits.py <min_to_export(default 1000)> <export_count(default 500)>')
        min_to_export = int(sys.argv[1])
        export_count = int(sys.argv[2])
        ret, err = audit.export_old_audits(min_to_export, export_count)
        if err:
            raise Exception(err)

    except Exception, e:
        #print str(e)
        logger.log_or_print('Error exporting old audits: %s' %
                            e, lg, level='critical')
        return -1,  'Error exporting old audits : %s' % e
    else:
        logger.log_or_print(
            'Processing export of old audits completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab

