# Integral View's internal logging module that is an extention to the
# python/django loggin module

from integralstor import db, config


import logging
logger = logging.getLogger(__name__)


def set_log_level(level):
    try:
        db_path, err = config.get_db_path()
        if err:
            raise Exception(err)
        if level not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            logger.setLevel(logging.INFO)
        else:
            d1, err = db.get_single_row(
                db_path, "select * from global_params")
            if err:
                raise Exception(err)
            cmd_list = []
            if d1:
                cmd = [
                    "update global_params set logging_level=? where id = ?", (level, 1,)]
            else:
                cmd = [
                    "insert into global_params (logging_level, id) values(?,?)", (level, 1,)]
            cmd_list.append(cmd)
            ret, err = db.execute_iud(db_path, cmd_list)
            if err:
                raise Exception(err)
            logger.setLevel(level)
    except Exception, e:
        return False, 'Error setting log level : %s' % str(e)
    else:
        return True, None


def get_log_level_str():
    try:
        level, err = get_log_level()
        if err:
            raise Exception(err)
        if level == logging.DEBUG:
            return 'Debug'
        elif level == logging.WARNING:
            return 'Warnings'
        elif level == logging.INFO:
            return 'Information'
        elif level == logging.ERROR:
            return 'Errors'
        else:
            return 'Unknown'
    except Exception, e:
        return False, 'Error getting log level string: %s' % str(e)
    else:
        return True, None


def get_log_level():
    d = None
    conn = None
    log_level = None
    try:
        d, err = db.get_single_row(
            db_path, "select * from global_params where id=1")
        if err:
            raise Exception(err)
        if d and "logging_level" in d:
            log_level = d["logging_level"]
        else:
            # Not yet set so insert the default and return it
            cmd_list = []
            cmd = [
                "insert into global_params (logging_level, id) values(?,?)", (logging.INFO, 1,)]
            cmd_list.append(cmd)
            ret, err = db.execute_iud(db_path, cmd_list)
            if err:
                raise Exception(err)
            log_level = logging.INFO
    except Exception, e:
        return None, "Error getting log level : %s" % str(e)
    else:
        return log_level, None


def info(msg):
    try:
        logger.setLevel(get_log_level())
        logger.info(msg)
    except Exception, e:
        return False, 'Error logging info : %s' % str(e)
    else:
        return True, None


def debug(msg):
    try:
        logger.setLevel(get_log_level())
        logger.debug(msg)
    except Exception, e:
        return False, 'Error logging debug : %s' % str(e)
    else:
        return True, None


def critical(msg):
    try:
        logger.setLevel(get_log_level(logger))
        logger.critical(msg)
    except Exception, e:
        return False, 'Error logging critical : %s' % str(e)
    else:
        return True, None


def warn(msg):
    try:
        logger.setLevel(get_log_level(logger))
        logger.warn(msg)
    except Exception, e:
        return False, 'Error logging warning : %s' % str(e)
    else:
        return True, None


def error(msg):
    try:
        logger.setLevel(get_log_level(logger))
        logger.error(msg)
    except Exception, e:
        return False, 'Error logging error : %s' % str(e)
    else:
        return True, None

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
