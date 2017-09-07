
from integralstor import event_notifications, audit, mail, logger, db

import logging
import sys
import datetime

'''
Process all events that match the specified audit notification
'''

def main():
    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Process audit events', '/var/log/integralstor/logs/scripts.log', level=logging.DEBUG)
        num_args = len(sys.argv)
        if num_args != 2:
            raise Exception('Usage : python process_audit_notifications <event_notification_trigger_id>')
        else:
            ent_id = sys.argv[1]

        logger.log_or_print('Processing audit notifications initiated.', lg, level='info')

        enh_list, err = event_notifications.get_event_notification_holdings(ent_id, 'by_event_notification_trigger_id')
        if err:
            raise Exception(err)
        ent, err = event_notifications.get_event_notification_trigger(ent_id)
        #print ent, err
        if err:
            raise Exception(err)
        if not ent:
            raise Exception('Could not find the specified event notification trigger')
        if enh_list:
            processed_successfully = False
            if ent['notification_type_id'] == 1:
                msg_list = []
                for enh in enh_list:
                    #print enh
                    #Need to generate an email into the email_queue
                    msg, err = audit.generate_audit_email_body(enh['event_id'])
                    #print msg, err
                    if err:
                        raise Exception(err)
                    msg_list.append(msg)
                if msg_list:
                    #Now generate ONE email for all the messages corresponding to that trigger..
                    final_msg = '\n\n------------------------------------------------------\n\n'.join(msg_list)
                    #print 'final msg - ', final_msg
                    enc, err = mail.get_event_notification_configuration(ent['enc_id'])
                    #print enc, err
                    if err:
                        raise Exception(err)
                    processed_successfully, err = mail.enqueue(enc['recipient_list'], "Audit message from IntegralSTOR storage system", final_msg)
                    #print 'enqueue', processed_successfully, err
                    if err:
                        raise Exception(err)
            else:
                raise Exception('Unknown event notification type.')
            if processed_successfully:
                #Successfully enqueued so now remove them all from the holding table
                for enh in enh_list:
                    r, err = event_notifications.delete_event_notification_holding(enh['enh_id'])
                    if err:
                        raise Exception(err)
    except Exception, e:
        #print str(e)
        logger.log_or_print('Error processing audit notifications : %s' %
                            e, lg, level='critical')
        return -1,  'Error processing audit notifications : %s' % e
    else:
        logger.log_or_print(
            'Processing audit notifications completed successfully.', lg, level='info')
        return 0, None


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
