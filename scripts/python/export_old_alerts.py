from integralstor import alerts, logger, db, config

import logging
import sys
import datetime


def main():
    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Export old alert', scripts_log, level=logging.DEBUG)

        logger.log_or_print(
            'Processing export of old alerts initiated.', lg, level='info')
        if len(sys.argv) != 2:
            raise Exception(
                'Usage : python export_old_alerts.py <older_than_x_days>')
        else:
            days = sys.argv[1]

        ret, err = alerts.export_old_alerts(int(days))
        if err:
            raise Exception(err)

    except Exception, e:
        # print str(e)
        logger.log_or_print('Error exporting old alerts: %s' %
                            e, lg, level='critical')
        return -1,  'Error exporting old alerts : %s' % e
    else:
        logger.log_or_print(
            'Processing export of old alerts alerts completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
