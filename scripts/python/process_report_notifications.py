
from integralstor import event_notifications, audit, mail, logger, db

import logging
import sys
import datetime
import os.path
import glob

'''
Process all events that match the specified report notification
'''

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Process report notifications', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)
        num_args = len(sys.argv)
        if num_args != 2:
            raise Exception('Usage : python process_report_notifications <event_notification_trigger_id>')
        else:
            ent_id = sys.argv[1]

        logger.log_or_print('Processing report notifications initiated.', lg, level='info')

        ent, err = event_notifications.get_event_notification_trigger(ent_id)
        #print ent, err
        if err:
            raise Exception(err)
        if not ent:
            raise Exception('Could not find the specified event notification trigger')
        if ent['notification_type_id'] == 1:
            enc, err = mail.get_event_notification_configuration(ent['enc_id'])
            #print enc, err
            if err:
                raise Exception(err)
            if ent['event_type_id'] == 3:
                attachment_location = None
                if ent['event_subtype_id'] == 1:
                    #System status repor
                    #Find the latest system status report and mail it out
                    all_files = glob.glob('/var/log/integralstor/reports/integralstor_status/*') 
                    latest_file = max(all_files, key=os.path.getctime)
                    attachment_location = latest_file
                    email_header = 'IntegralSTOR system status report'
                    email_body = 'Please find the latest IntegralSTOR system status report'

                elif ent['event_subtype_id'] == 2:
                    #urbackup report processing here
                    #attachment_location = ''
                    #email_header = 'IntegralSTOR backup status report'
                    #email_body = 'Please find the latest IntegralSTOR backup status report'
                    pass
                processed_successfully, err = mail.enqueue(enc['recipient_list'], email_header, email_body, attachment_file_location = attachment_location, delete_attachment_file = False)
                #print 'enqueue', processed_successfully, err
                if err:
                    raise Exception(err)
    except Exception, e:
        #print str(e)
        logger.log_or_print('Error processing report notifications : %s' %
                            e, lg, level='critical')
        return -1,  'Error processing report notifications : %s' % e
    else:
        logger.log_or_print(
            'Processing report notifications completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
