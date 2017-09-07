import django
import django.template
import os

import urllib

from integralstor import local_users, audit, services_management


def view_services(request):
    return_dict = {}
    try:
        template = 'logged_in_error.html'

        if "ack" in request.GET:
            if request.GET["ack"] == "start_success":
                return_dict['ack_message'] = "Service start successful. Please wait for a few seconds for the status below to be updated."
            elif request.GET["ack"] == "stop_success":
                return_dict['ack_message'] = "Service stop successful. Please wait for a few seconds for the status below to be updated."
            elif request.GET["ack"] == "stop_fail":
                return_dict['ack_message'] = "Service stop failed"
            elif request.GET["ack"] == "start_fail":
                return_dict['ack_message'] = "Service start failed"
        if 'service_change_status' in request.GET:
            if request.GET['service_change_status'] != 'none':
                return_dict['ack_message'] = 'Service status change initiated. Output : %s' % urllib.quote(
                    request.GET['service_change_status'])
            else:
                return_dict['ack_message'] = 'Service status change initiated'

        return_dict["services"], err = services_management.get_sysd_services_status()
        if err:
            raise Exception(err)
        return django.shortcuts.render_to_response('view_services.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'System services'
        return_dict['tab'] = 'view_services_tab'
        return_dict["error"] = 'Error loading system services status'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_service_status(request):
    return_dict = {}
    try:
        if request.method == "GET":
            raise Exception("Invalid request. Please use the menus")
        if 'service' not in request.POST:
            raise Exception("Invalid request. Please use the menus")
        if 'action' not in request.POST or request.POST['action'] not in ['start', 'stop', 'restart', 'enable', 'disable']:
            raise Exception("Invalid request. Please use the menus")

        service = request.POST['service']
        action = request.POST['action']

        if 'action' == 'start' and service == 'vsftpd':
            # Need to make sure that all local users have their directories
            # created so do it..
            config, err = vsftp.get_ftp_config()
            if err:
                raise Exception(err)
            users, err = local_users.get_local_users()
            if err:
                raise Exception(err)
            ret, err = create_ftp_user_dirs(config['dataset'], users)
            if err:
                raise Exception(err)

        audit_str = "Service status change of %s initiated to %s state." % (
            service, action)
        audit.audit("change_service_status", audit_str, request)

        out, err = services_management.update_service_status(service, action)
        if err:
            raise Exception(err)

        if out:
            return django.http.HttpResponseRedirect('/view_services?&service_change_status=%s' % ','.join(out))
        else:
            return django.http.HttpResponseRedirect('/view_services?service_change_status=none')

    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'Modify system service state'
        return_dict['tab'] = 'view_services_tab'
        return_dict["error"] = 'Error modifying system services state'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


if __name__ == '__main__':
    print _get_service_status(('ntpd', 'NTP'))
    print _get_service_status(('network', 'networking'))
    print _get_service_status(('salt-minion', 'salt-minion'))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
