
import django.template
import django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from integralstor_utils import ntp, services_management, django_utils
from integralstor import system_info

import integral_view
from integral_view.forms import common_forms
from integral_view.utils import iv_logging


@login_required
def view_ntp_settings(request):
    return_dict = {}
    try:
        ntp_servers, err = ntp.get_ntp_servers()
        if err:
            raise Exception(err)
        return_dict["ntp_servers"] = ntp_servers

        req_ret, err = django_utils.get_request_parameter_values(
            request, ['ack', 'server_used'])
        if err:
            raise Exception(err)
        if 'ack' in req_ret and req_ret['ack'] == 'saved':
            return_dict["ack_message"] = 'NTP settings have successfully been updated.'
        elif 'ack' in req_ret and req_ret['ack'] == 'ntp_synced':
            if 'server_used' in req_ret:
                return_dict["ack_message"] = 'One time ntp sync with server %s successfully completed.' % req_ret['server_used']
        return django.shortcuts.render_to_response('view_ntp_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'View NTP settings'
        return_dict['tab'] = 'ntp_settings_tab'
        return_dict["error"] = 'Error retrieving NTP settings'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def update_ntp_settings(request):

    return_dict = {}
    try:
        if request.method == "GET":
            ntp_servers, err = ntp.get_ntp_servers()
            if err:
                raise Exception(err)
            if not ntp_servers:
                form = common_forms.ConfigureNTPForm()
            else:
                form = common_forms.ConfigureNTPForm(
                    initial={'server_list': ','.join(ntp_servers)})
            url = "update_ntp_settings.html"
        else:
            form = common_forms.ConfigureNTPForm(request.POST)
            if form.is_valid():
                iv_logging.debug("Got valid request to change NTP settings")
                cd = form.cleaned_data
                server_list = cd["server_list"]
                if ',' in server_list:
                    slist = server_list.split(',')
                else:
                    slist = server_list.split(' ')
                ret, err = ntp.update_integralstor_ntp_servers(slist)
                print ret, err
                if err:
                    raise Exception(err)
                return django.http.HttpResponseRedirect("/view_ntp_settings?ack=saved")
            else:
                # invalid form
                iv_logging.debug("Got invalid request to change NTP settings")
                url = "update_ntp_settings.html"
        return_dict["form"] = form
        return django.shortcuts.render_to_response(url, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'Modify NTP notifications settings'
        return_dict['tab'] = 'ntp_settings_tab'
        return_dict["error"] = 'Error modifying NTP notifications settings'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def sync_ntp(request):
    return_dict = {}
    try:
        output, err = ntp.sync_ntp()
        if err:
            raise Exception(err)
        else:
            if 'ntp_sync' in output and output['ntp_sync'] == True and 'server_used' in output:
                return django.http.HttpResponseRedirect("/view_ntp_settings?ack=ntp_synced&server_used=%s" % output['server_used'])
            else:
                raise Exception("NTP sync failed")
    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'View NTP settings'
        return_dict['tab'] = 'ntp_settings_tab'
        return_dict["error"] = 'Error retrieving syncing with ntp servers'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
