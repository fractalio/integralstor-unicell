import django
import django.template
import django.utils.timezone
import time
import datetime
from django.http import HttpResponse
from django.http import JsonResponse

from integralstor_utils import django_utils, config, inotify, system_date_time, command, audit
from integralstor import system_info, remote_monitoring
from integral_view.forms import system_forms


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
        return_dict['base_template'] = "dashboard_base.html"
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
                    initial['name'] = servers[ip]
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
        return_dict['base_template'] = "dashboard_base.html"
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
        return_dict['base_template'] = "dashboard_base.html"
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
        return_dict['base_template'] = "dashboard_base.html"
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

        '''
        local_timezone, err = system_date_time.get_current_timezone()
        if err:
            raise Exception(err)
        if 'timezone_str' not in local_timezone:
            timezone_str = 'UTC'
        else:
            timezone_str = local_timezone['timezone_str']

        tz = pytz.timezone(timezone_str)
        django.utils.timezone.activate(tz)
        now_local = datetime.datetime.now(tz)

        now = int(now_local.strftime('%s'))
        '''
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
