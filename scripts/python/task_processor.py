from integralstor import tasks_utils, lock, logger, config
import logging
import sys
import atexit

atexit.register(lock.release_lock, 'task_processor')

def main():

    lg = None
    try:
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Task processor', scripts_log, level=logging.DEBUG)

        lck, err = lock.get_lock('task_processor')
        if err:
            raise Exception(err)
        if not lck:
            raise Exception('Could not acquire lock. Exiting.')

        logger.log_or_print(
            'Task processor execution initiated.', lg, level='info')

        db_path, err = config.get_db_path()
        if err:
            raise Exception(err)
        ret, err = tasks_utils.process_tasks()
        if err:
            raise Exception(err)
    except Exception, e:
        str = 'Error running the task processor : %s' % e
        lock.release_lock('task_processor')
        logger.log_or_print(str, lg, level='critical')
        return -1
    else:
        lock.release_lock('task_processor')
        str = 'Task processor completed successfully.'
        logger.log_or_print(str, lg, level='info')
        return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
