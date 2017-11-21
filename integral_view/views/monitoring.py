import django
import django.template
from django.http import HttpResponse
from django.http import JsonResponse

from integralstor import event_notifications, mail, audit, django_utils, inotify
from integralstor import system_info, remote_monitoring, config, command
from integral_view.forms import system_forms, monitoring_forms


def view_remote_monitoring_servers(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "updated":
                return_dict['ack_message'] = "Remote monitoring server successfully updated"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Remote monitoring server successfully deleted"

        servers, err = remote_monitoring.get_servers()
        if err:
            raise Exception(err)
        return_dict['servers'] = servers
        return django.shortcuts.render_to_response("view_remote_monitoring_servers.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'Remote server monitoring'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error loading remote monitoring server list'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_remote_monitoring_server(request):
    return_dict = {}
    try:
        if request.method == "GET":
            servers, err = remote_monitoring.get_servers()
            if err:
                raise Exception(err)
            req_ret, err = django_utils.get_request_parameter_values(request, [
                'view', 'ip'])
            if err:
                raise Exception(err)
            initial = {}
            if 'ip' in req_ret:
                ip = req_ret['ip']
                if ip in servers.keys():
                    initial['ip'] = ip
                    initial['name'] = servers[ip]['name']
                return_dict['action'] = 'update'
            else:
                return_dict['action'] = 'create'
            form = system_forms.RemoteMonitoringServerForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_remote_monitoring_server.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = system_forms.RemoteMonitoringServerForm(request.POST)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                res, err = remote_monitoring.update_server(
                    cd['ip'], cd['name'])
                if not res:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception(
                            'Error updating remote monitoring server list')
                audit_str = 'Updated the remote monitoring server with IP : %s and name : %s' % (
                    cd['ip'], cd['name'])
                audit.audit("update_remote_monitoring_server",
                            audit_str, request)
                return django.http.HttpResponseRedirect('/view_remote_monitoring_servers?ack=updated')
            else:
                # invalid form
                return django.shortcuts.render_to_response("update_remote_monitoring_server.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'Update remote server monitoring server'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error updating remote monitoring server'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_remote_monitoring_server(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
            'view', 'ip'])
        if err:
            raise Exception(err)
        if 'ip' not in req_ret:
            raise Exception('Invalid request, please use the menus.')
        ip = req_ret['ip']
        servers, err = remote_monitoring.get_servers()
        if err:
            raise Exception(err)
        if ip not in servers.keys():
            raise Exception(
                'Specified server is currently not being remote monitored.')
        name = servers[ip]['name']
        ret, err = remote_monitoring.delete_server(ip)
        if err:
            raise Exception(err)
        audit_str = 'Removed the remote monitoring server with IP : %s name : %s' % (
            ip, name)
        audit.audit("delete_remote_monitoring_server", audit_str, request)
        return django.http.HttpResponseRedirect('/view_remote_monitoring_servers?ack=deleted')

    except Exception, e:
        return_dict["page_title"] = 'Remove remote server monitoring server'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error removing remote monitoring server'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_remote_monitoring_server_status(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
            'view', 'ip'])
        if err:
            raise Exception(err)
        if 'ip' not in req_ret:
            raise Exception('Invalid request, please use the menus.')
        status, err = remote_monitoring.get_status(req_ret['ip'])
        if err:
            raise Exception(err)
        print status
        return_dict['status'] = status
        return django.shortcuts.render_to_response("view_remote_monitoring_server_status.html", return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict["page_title"] = 'View remote server monitoring server status'
        return_dict['tab'] = 'remote_monitoring_tab'
        return_dict["error"] = 'Error viewing remote monitoring server status'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_scheduled_notifications(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Scheduled notification successfully removed"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "Scheduled notification successfully created"

        ent_list, err = event_notifications.get_event_notification_triggers()
        # print ent_list
        if err:
            raise Exception(err)
        for ent in ent_list:
            if ent['notification_type_id'] == 1:
                enc, err = mail.get_event_notification_configuration(
                    ent['enc_id'])
                if err:
                    raise Exception(err)
                if enc:
                    ent['recipient_list'] = enc['recipient_list']

        return_dict['ent_list'] = ent_list
        return django.shortcuts.render_to_response("view_scheduled_notifications.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["page_title"] = 'View scheduled notifications'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error loading scheduled notifications list'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_scheduled_notification(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, [
            'event_type_id', 'scheduler'])
        if err:
            raise Exception(err)

        reference_table_entries, err = event_notifications.get_reference_table_entries(
            ['reference_event_types', 'reference_event_subtypes', 'reference_notification_types', 'reference_severity_types', 'reference_subsystem_types'])
        if err:
            raise Exception(err)
        if 'event_type_id' not in req_params or int(req_params['event_type_id']) not in reference_table_entries['reference_event_types'].keys():
            raise Exception('Invalid request. Please use the menus.')
        return_dict['event_type_id'] = req_params['event_type_id']
        event_type_id = int(req_params['event_type_id'])
        if request.method == "GET":
            if event_type_id == 1:
                form = monitoring_forms.AlertNotificationsForm(reference_subsystem_types=reference_table_entries['reference_subsystem_types'], reference_severity_types=reference_table_entries[
                                                               'reference_severity_types'], reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_alert_notification.html'
            elif event_type_id == 2:
                form = monitoring_forms.AuditNotificationsForm(
                    reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_audit_notification.html'
            elif event_type_id == 3:
                form = monitoring_forms.LogNotificationsForm(
                    reference_notification_types=reference_table_entries['reference_notification_types'], reference_event_subtypes=reference_table_entries['reference_event_subtypes'])
                template = 'create_report_notification.html'
            return_dict['form'] = form
            return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

        elif request.method == "POST":
            scheduler = req_params['scheduler']
            schedule = scheduler.split()
            if event_type_id == 1:
                form = monitoring_forms.AlertNotificationsForm(request.POST, reference_subsystem_types=reference_table_entries['reference_subsystem_types'], reference_severity_types=reference_table_entries[
                                                               'reference_severity_types'], reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_alert_notification.html'
            elif event_type_id == 2:
                form = monitoring_forms.AuditNotificationsForm(
                    request.POST, reference_notification_types=reference_table_entries['reference_notification_types'])
                template = 'create_audit_notification.html'
            elif event_type_id == 3:
                form = monitoring_forms.LogNotificationsForm(request.POST, reference_notification_types=reference_table_entries[
                                                             'reference_notification_types'], reference_event_subtypes=reference_table_entries['reference_event_subtypes'])
                template = 'create_report_notification.html'
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data

            psp, err = config.get_python_scripts_path()
            if err:
                raise Exception(err)
            if 'subsystem_type_id' in cd:
                subsystem_type_id = int(cd['subsystem_type_id'])
            else:
                subsystem_type_id = -1
            if 'event_subtype_id' in cd:
                event_subtype_id = int(cd['event_subtype_id'])
            else:
                event_subtype_id = -1
            if 'severity_type_id' in cd:
                severity_type_id = int(cd['severity_type_id'])
            else:
                severity_type_id = -1
            if int(cd['notification_type_id']) == 1:
                enc_id, err = mail.create_event_notification_configuration(
                    cd['recipient_list'])
                if err:
                    raise Exception(err)
            audit_str, err = event_notifications.create_event_notification(schedule, event_type_id, event_subtype_id, subsystem_type_id, int(
                cd['notification_type_id']), severity_type_id, enc_id, reference_table_entries=reference_table_entries)
            if err:
                if int(cd['notification_type_id']) == 1:
                    mail.delete_event_notification_configuration(enc_id)
                raise Exception(err)

            if int(cd['notification_type_id']) == 1:
                audit_str += " Emails will be sent to %s" % cd['recipient_list']

            if event_type_id == 1:
                audit.audit("create_alert_notification", audit_str, request)
            elif event_type_id == 2:
                audit.audit("create_audit_notification", audit_str, request)
            elif event_type_id == 3:
                audit.audit("create_report_notification", audit_str, request)

            return django.http.HttpResponseRedirect('/view_scheduled_notifications?ack=created')
    except Exception, e:
        return_dict["page_title"] = 'Crete scheduled notification'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error creating scheduled notification'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_scheduled_notification(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, [
            'ent_id'])
        if err:
            raise Exception(err)
        if 'ent_id' not in req_params:
            raise Exception('Invalid request, please use the menus.')
        ent_id = int(req_params['ent_id'])
        ent, err = event_notifications.get_event_notification_trigger(ent_id)
        # print ent
        if err:
            raise Exception(err)
        ret, err = event_notifications.delete_event_notification(ent_id)
        if err:
            raise Exception(err)
        audit_str = 'Removed the event notification: %s, that was scheduled for %s' % (
            ent['description'], ent['schedule_description'])
        if ent['event_type_id'] == 1:
            audit.audit("delete_alert_notification", audit_str, request)
        elif ent['event_type_id'] == 2:
            audit.audit("delete_audit_notification", audit_str, request)
        elif ent['event_type_id'] == 3:
            audit.audit("delete_report_notification", audit_str, request)
        return django.http.HttpResponseRedirect('/view_scheduled_notifications?ack=deleted')
    except Exception, e:
        return_dict["page_title"] = 'Remove scheduled notification'
        return_dict['tab'] = 'scheduled_notifications_tab'
        return_dict["error"] = 'Error removing scheduled notification'
        return_dict['base_template'] = "logging_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def api_get_status(request):
    si = {}
    err = None
    try:
        si, err = system_info.load_system_config()
        # print si
        if err:
            raise Exception(err)
    except Exception, e:
        # print str(e)
        return JsonResponse({'error': str(e)})
        # return django.http.HttpResponse({'error': str(e)}
        # ,content_type='application/json')
    else:
        return JsonResponse(si)
        # return django.http.HttpResponse(si,content_type='application/json')


def view_read_write_stats(request):
    return_dict = {}
    try:

        req_params, err = django_utils.get_request_parameter_values(
            request, ['last_x_seconds', 'refresh_interval'])
        if err:
            raise Exception(err)
        if 'refresh_interval' in req_params:
            return_dict['refresh_interval'] = req_params['refresh_interval']
        if 'last_x_seconds' in req_params:
            actions = ['access', 'modify', 'create', 'delete', 'move']
            count_dict = {}
            for action in actions:
                count, err = inotify.get_count(
                    action, int(req_params['last_x_seconds']))
                if err:
                    raise Exception(err)
                count_dict[action] = count
            # print count_dict
            return_dict['count_dict'] = count_dict
            return_dict['last_x_seconds'] = int(req_params['last_x_seconds'])
            return_dict['last_x_minutes'] = int(
                req_params['last_x_seconds']) / 60

        lines, err = command.get_command_output('/usr/bin/arc_summary.py -d')
        if not err:
            return_dict['arc_summary_lines'] = lines
        else:
            return_dict['arc_error'] = err

        lines, err = command.get_command_output('zpool iostat -T d -v')
        if not err:
            return_dict['zpool_iostat_lines'] = lines
        else:
            return_dict['zpool_iostat_error'] = err

        lines, err = command.get_command_output('iostat -dm')
        if not err:
            return_dict['iostat_lines'] = lines
        else:
            return_dict['iostat_error'] = err

        lines, err = command.get_command_output('iostat -c')
        if not err:
            return_dict['cpu_iostat_lines'] = lines
        else:
            return_dict['cpu_iostat_error'] = err

        lines, err = command.get_command_output('free -h')
        if not err:
            return_dict['mem_lines'] = lines
        else:
            return_dict['mem_error'] = err

        lines, err = command.get_command_output('free -h')
        if not err:
            return_dict['mem_lines'] = lines
        else:
            return_dict['mem_error'] = err

        if err:
            raise Exception(err)
        return django.shortcuts.render_to_response('view_read_write_stats.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Monitoring'
        return_dict['tab'] = 'dir_manager_tab'
        return_dict["error"] = 'Error loading read and write stats'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
