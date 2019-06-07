from integralstor import event_notifications, audit, mail, logger, db, config, datetime_utils, remote_replication, system_info

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
        scripts_log, err = config.get_scripts_log_path()
        if err:
            raise Exception(err)
        lg, err = logger.get_script_logger(
            'Process report notifications', scripts_log, level=logging.DEBUG)
        num_args = len(sys.argv)
        if num_args != 2:
            raise Exception(
                'Usage : python process_report_notifications <event_notification_trigger_id>')
        else:
            ent_id = sys.argv[1]
        logger.log_or_print(
            'Processing report notifications initiated.', lg, level='info')

        status_reports_dir, err = config.get_staus_reports_dir_path()
        if err:
            raise Exception(err)
        urb_reports_dir, err = config.get_urbackup_reports_dir_path()
        if err:
            raise Exception(err)
        rr_reports_dir, err = config.get_remote_replication_reports_dir_path()
        if err:
            raise Exception(err)


        ent, err = event_notifications.get_event_notification_trigger(ent_id)
        # print ent, err
        if err:
            raise Exception(err)
        if not ent:
            raise Exception(
                'Could not find the specified event notification trigger')
        if ent['notification_type_id'] == 1:
            enc, err = mail.get_event_notification_configuration(ent['enc_id'])
            # print enc, err
            if err:
                raise Exception(err)
            org_info, err = system_info.get_org_info()
            if err:
                raise Exception(err)
            org_str = ''
            if org_info:
                if org_info['org_name']:
                    org_str = '%s' % org_info['org_name']
                if org_info['unit_name']:
                    org_str = '%s Unit: %s' % (org_str, org_info['unit_name'])
                if org_info['unit_id']:
                    org_str = '%s Unit ID: %s' % (org_str, org_info['unit_id'])
                if org_info['subunit_name']:
                    org_str = '%s Subunit name: %s' % (org_str, org_info['subunit_name'])
                if org_info['subunit_id']:
                    org_str = '%s Subunit ID: %s' % (org_str, org_info['subunit_id'])

            if ent['event_type_id'] == 3:
                attachment_location = None
                if ent['event_subtype_id'] == 1:
                    # System status report
                    # Find the latest system status report and mail it out
                    all_files = glob.glob('%s/*' % status_reports_dir)
                    latest_file = max(all_files, key=os.path.getctime)
                    attachment_location = latest_file
                    if org_str:
                        email_header = 'IntegralSTOR system status report from %s' % org_str
                    else:
                        email_header = 'IntegralSTOR system status report'
                    email_body = 'Please find the latest IntegralSTOR system status report'

                elif ent['event_subtype_id'] == 2:
                    # urbackup report processing here
                    if org_str:
                        email_header = 'IntegralSTOR backup status report from %s' % org_str
                    else:
                        email_header = 'IntegralSTOR backup status report'
                    email_body = 'Please find the latest IntegralSTOR backup status report'
                    all_files = glob.glob('%s/*' % urb_reports_dir)
                    latest_file = max(all_files, key=os.path.getctime)
                    attachment_location = latest_file

                elif ent['event_subtype_id'] == 3:
                    # remote replication report processing here
                    ret, err = remote_replication.generate_pdf_report()
                    if err:
                        raise exception(err)
                    if org_str:
                        email_header = 'IntegralSTOR remote replication status report from %s' % org_str
                    else:
                        email_header = 'IntegralSTOR remote replication status report'
                    email_body = 'Please find the latest IntegralSTOR remote replication status report'
                    all_files = glob.glob('%s/*' % rr_reports_dir)
                    latest_file = max(all_files, key=os.path.getctime)
                    attachment_location = latest_file

                processed_successfully, err = mail.enqueue(
                    enc['recipient_list'], email_header, email_body, attachment_file_location=attachment_location, delete_attachment_file=False)
                # print 'enqueue', processed_successfully, err
                if err:
                    raise Exception(err)
    except Exception, e:
        # print str(e)
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
