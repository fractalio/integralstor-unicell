import zipfile
import os
import io
import shutil

import django
import django.template
from django.contrib import auth
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required

from integralstor import alerts, audit, datetime_utils, django_utils, config, db

import integral_view
from integral_view.forms import log_management_forms, common_forms
from integral_view.utils import iv_logging


def _handle_uploaded_file(f):
    with open('/tmp/upload.zip', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True, "/tmp/upload.zip"


def _copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)
    return True


def _copy_file_and_overwrite(from_path, to_path):
    shutil.copyfile(from_path, to_path)
    return True


def view_audits(request):
    return_dict = {}
    try:
        return_dict['base_template'] = "logging_base.html"
        return_dict['tab'] = 'audits_tab'
        return_dict["page_title"] = 'Audit trail'
        al, err = audit.get_entries()
        if err:
            raise Exception(err)
        return_dict["audit_list"] = al
        return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'Audit trail'
        return_dict['tab'] = 'view_logs_tab'
        return_dict["error"] = 'Error loading audit trail'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_alerts(request):
    return_dict = {}
    try:
        return_dict['base_template'] = "logging_base.html"
        return_dict['tab'] = 'alerts_tab'
        return_dict["page_title"] = 'Alerts'
        alerts_list, err = alerts.get_alerts()
        if err:
            raise Exception(err)
        ret, err = alerts.update_last_view_time(request)
        return_dict['alerts_list'] = alerts_list
        return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'System alerts'
        return_dict['tab'] = 'view_logs_tab'
        return_dict["error"] = 'Error loading system alerts'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_hardware_logs(request):
    return_dict = {}
    try:
        hw_platform, err = config.get_hardware_platform()
        if err:
            raise Exception(err)
        if hw_platform or hw_platform != 'dell':
            raise Exception('Unknown hardware platform')
        return_dict['hw_platform'] = hw_platform
        if hw_platform == 'dell':
            from integralstor.platforms import dell
            logs_dict, err = dell.get_alert_logs()
            if logs_dict:
                return_dict['logs_dict'] = logs_dict
        return django.shortcuts.render_to_response('view_hardware_logs.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'View and download logs'
        return_dict['tab'] = 'logs_tab'
        return_dict["error"] = 'Error loading hardware logs'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def download_log(request):
    """ Download the system log of the type specified in log_type POST param 
    This calls the /sys_log via an http request on that node to get the info"""

    return_dict = {}
    try:
        hw_platform, err = config.get_hardware_platform()
        if err:
            raise Exception(err)
        if hw_platform and hw_platform != 'dell':
            raise Exception('Unknown hardware platform')
        return_dict['hw_platform'] = hw_platform

        form = log_management_forms.DownloadLogsForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                cd = form.cleaned_data
                log_type = cd['log_type']

                if log_type in ['alerts', 'audit', 'hardware']:
                    response = django.http.HttpResponse()
                    if log_type == 'alerts':
                        response['Content-disposition'] = 'attachment; filename=alerts_log.txt'
                        all_alerts, err = alerts.get_alerts()
                        if err:
                            raise Exception(err)
                        for alert in all_alerts:
                            if int(alert['repeat_count']) > 1:
                                response.write('Last alert time %s\nAlert message: %s\nRepeated count: %d\n\n' %
                                               (alert['last_update_time'], alert['alert_str'], int(alert['repeat_count'])))
                            else:
                                response.write('Last alert time %s\nAlert message: %s\n\n' %
                                               (alert['last_update_time'], alert['alert_str']))
                            response.flush()
                    elif log_type == 'audit':
                        response['Content-disposition'] = 'attachment; filename=audit_log.txt'
                        all_audits, err = audit.get_entries()
                        if err:
                            raise Exception(err)
                        for audit_info in all_audits:
                            response.write('Time : %s \n' % audit_info['time'])
                            response.write('Source IP : %s \n' %
                                           audit_info['ip'])
                            response.write('Action : %s \n' %
                                           audit_info['action_str'])
                            response.write('\n')
                            response.flush()
                    elif log_type == 'hardware':
                        response['Content-disposition'] = 'attachment; filename=hardware_logs.txt'
                        hw_platform, err = config.get_hardware_platform()
                        if not hw_platform or hw_platform != 'dell':
                            raise Exception('Unknown hardware platform')
                        if hw_platform == 'dell':
                            from integralstor.platforms import dell
                            logs_dict, err = dell.get_alert_logs()
                            if err:
                                raise Exception(err)
                            if not logs_dict:
                                raise Exception('No logs detected!')
                            for timestamp, log_list in logs_dict.items():
                                for log in log_list:
                                    response.write('Time : %s\n' %
                                                   log['date_time'])
                                    response.write(
                                        'Severity : %s\n' % log['Severity'])
                                    response.write(
                                        'Description : %s\n' % log['description'])
                                    response.write('\n')
                                    response.flush()
                        else:
                            raise Exception('Unknown platform')
                else:
                    scripts_log, err = config.get_scripts_log_path()
                    if err:
                        raise Exception(err)

                    system_logs = [('/var/log/boot.log', 'boot.log'), ('/var/log/dmesg', 'dmesg'), ('/var/log/messages', 'messages'),
                                   ('/var/log/smblog.vfs', 'samba'), ('/var/log/samba/log.winbindd', 'winbind'), (scripts_log, 'scripts')]

                    now_local_epoch, err = datetime_utils.get_epoch(when='now')
                    if err:
                        raise Exception(err)
                    now_local_str, err = datetime_utils.convert_from_epoch(
                        now_local_epoch, return_format='str', str_format='%Y_%m_%d_%H_%M', to='local')
                    if err:
                        raise Exception(err)

                    zf_name = 'IntegralSTOR_system_logs_%s.zip' % now_local_str

                    try:
                        out = io.BytesIO()
                        zf = zipfile.ZipFile(out, 'w')
                        for entry in system_logs:
                            zf.write(entry[0], arcname=entry[1])
                            #zf.write(file_name, arcname=display_name)
                        zf.close()
                    except Exception as e:
                        raise Exception(
                            "Error compressing log file : %s" % str(e))

                    response = django.http.HttpResponse(
                        out.getvalue(), content_type='application/x-compressed')
                    response['Content-disposition'] = 'attachment; filename=%s' % (
                        zf_name)

                return response

        # either a get or an invalid form so send back form
        return_dict['form'] = form
        return django.shortcuts.render_to_response('download_log_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'Download system logs'
        return_dict['tab'] = 'logs_tab'
        return_dict["error"] = 'Error downloading system logs'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def download_sys_info(request):
    return_dict = {}
    try:
        display_name, err = config.get_config_dir()
        if err:
            raise Exception(err)
        zf_name = "system_info.zip"
        try:
            zf = zipfile.ZipFile(zf_name, 'w')
            abs_src = os.path.abspath(display_name)
            for dirname, subdirs, files in os.walk(display_name):
                if not(("logs" in dirname) or ("ntp" in dirname) or ("rc_local" in dirname) or ("samba" in dirname) or ("status" in dirname)):
                    for filename in files:
                        absname = os.path.abspath(
                            os.path.join(dirname, filename))
                        arcname = absname[len(abs_src) + 1:]
                        zf.write(absname, arcname)
            logs = {'smb_conf': '/etc/samba/smb.conf', 'ntp_conf': '/etc/ntp.conf', 'krb5_conf': '/etc/krb5.conf', 'nfs': '/etc/exports',
                    'ftp': '/etc/vsftpd/vsftpd.conf', 'master.status': display_name + "/status/master.status", 'master.manifest': display_name + "/status/master.manifest"}
            for key, value in logs.iteritems():
                if os.path.isfile(value):
                    zf.write(value, key)
            zf.close()
        except Exception as e:
            raise Exception("Error compressing remote log file : %s" % str(e))
        response = django.http.HttpResponse()
        response['Content-disposition'] = 'attachment; filename=system_info.zip'
        response['Content-type'] = 'application/x-compressed'
        with open(zf_name, 'rb') as f:
            byte = f.read(1)
            while byte:
                response.write(byte)
                byte = f.read(1)
        response.flush()
        return response
    except Exception as e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'Download system information'
        return_dict['tab'] = 'node_info_tab'
        return_dict["error"] = 'Error downloading system information'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_sys_info(request):
    return_dict = {}
    try:
        if request.method == "POST":
            status, path = _handle_uploaded_file(request.FILES['file_field'])
            display_name, err = config.get_config_dir()
            if err:
                raise Exception(err)
            if path:
                zip = zipfile.ZipFile(path, 'r')
                data = zip.namelist()
                move = zip.extractall("/tmp/upload/")
               # logs = {'smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf','nfs':'/etc/exports','ftp':'/etc/vsftpd/vsftpd.conf'}
                logs = {'smb_conf': '/etc/samba/smb.conf', 'ntp_conf': '/etc/ntp.conf', 'krb5_conf': '/etc/krb5.conf', 'nfs': '/etc/exports',
                        'ftp': '/etc/vsftpd/vsftpd.conf', 'master.status': display_name + "/status/master.status", 'master.manifest': display_name + "/status/master.manifest"}
                for key, value in logs.iteritems():
                    if key and os.path.isfile("/tmp/upload/" + key):
                        _copy_file_and_overwrite("/tmp/upload/" + key, value)
                for dir in os.listdir("/tmp/upload"):
                    if dir and os.path.isdir("/tmp/upload/" + dir):
                        _copy_and_overwrite(
                            "/tmp/upload/" + dir, config.get_config_dir()[0] + "/" + dir)
                return django.http.HttpResponseRedirect("/view_system_info/")
        else:
            form = common_forms.FileUploadForm()
            return_dict["form"] = form
            return django.shortcuts.render_to_response("upload_sys_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["error"] = 'Error displaying rotated log list'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def refresh_alerts(request, random=None):
    try:
        new_alerts_present, err = alerts.new_alerts_present(
            request.user.username)
        if err:
            raise Exception(err)
        if new_alerts_present:
            import json
            new_alerts = json.dumps(new_alerts_present)
            return django.http.HttpResponse(new_alerts, content_type='application/json')
        else:
            clss = "btn btn-default btn-sm"
            message = "View alerts"
            return django.http.HttpResponse("No New Alerts")
    except Exception, e:
        return django.http.HttpResponse("Error loading alerts : %s" % str(e))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
