import django
import django.template
import os

from integralstor import local_users, audit, vsftp, zfs, pki
from integral_view.forms import ftp_management_forms


def view_ftp_configuration(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "dirs_created":
                return_dict['ack_message'] = "FTP user home directories successfully created"
            elif request.GET["ack"] == "saved":
                return_dict['ack_message'] = "FTP configuration successfully updated"

        config, err = vsftp.get_ftp_config()
        if err:
            raise Exception(err)

        return_dict['config'] = config
        return django.shortcuts.render_to_response('view_ftp_configuration.html', return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'View FTP service configuration'
        return_dict['tab'] = 'ftp_service_settings'
        return_dict["error"] = 'Error retrieving the FTP service configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_ftp_configuration(request):
    return_dict = {}
    try:
        config, err = vsftp.get_ftp_config()
        if err:
            raise Exception(err)
        pools, err = zfs.get_pools()
        ds_list = []
        for pool in pools:
            for ds in pool["datasets"]:
                if ds['properties']['type']['value'] == 'filesystem':
                    ds_list.append(ds["name"])
        cert_list, err = pki.get_ssl_certificates()
        if err:
            raise Exception(err)
        cert_name_list = []
        for cert in cert_list:
            cert_name_list.append(cert['name'])
        # print ds_list
        if not ds_list:
            raise Exception(
                'No ZFS datasets available. Please create a dataset before configuring the FTP service.')

        if request.method == 'GET':
            initial = {}
            if config:
                for key in config.keys():
                    initial[key] = config[key]
            form = ftp_management_forms.ConfigureFTPForm(
                datasets=ds_list, cert_names=cert_name_list, initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response('update_ftp_configuration.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = ftp_management_forms.ConfigureFTPForm(
                request.POST, cert_names=cert_name_list, datasets=ds_list)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_ftp_configuration.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            ret, err = vsftp.update_ftp_config(cd)
            if err:
                raise Exception(err)
            users, err = local_users.get_local_users()
            if err:
                raise Exception(err)
            ret, err = vsftp.create_ftp_user_dirs(cd['dataset'], users)
            if err:
                raise Exception(err)
            audit_str = 'Updated FTP configuration.'
            if cd['ssl_enabled']:
                audit_str = audit_str + \
                    ' SSL enabled with certificate %s' % cd['cert_name']
            else:
                audit_str = audit_str + ' SSL disabled.'
            ret, err = audit.audit("update_ftp_config",
                                   audit_str, request)
            return django.http.HttpResponseRedirect('/view_ftp_configuration?ack=saved')
    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'Configure FTP service'
        return_dict['tab'] = 'ftp_service_settings'
        return_dict["error"] = 'Error configuring the FTP service '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_ftp_user_dirs(request):
    return_dict = {}
    try:
        config, err = vsftp.get_ftp_config()
        if err:
            raise Exception(err)
        if 'dataset' not in config:
            raise Exception(
                'No home dataset has been configured for the FTP service. Please do that before creating FTP home directories')
        users, err = local_users.get_local_users()
        if err:
            raise Exception(err)
        res, err = vsftp.create_ftp_user_dirs(config['dataset'], users)
        if err:
            raise Exception(err)

        audit.audit("create_ftp_dir",
                    'Created FTP user directories', request)
        return django.http.HttpResponseRedirect('/view_ftp_configuration?ack=dirs_created')

    except Exception, e:
        return_dict['base_template'] = "services_base.html"
        return_dict["page_title"] = 'Create FTP user directories'
        return_dict['tab'] = 'ftp_service_settings'
        return_dict["error"] = 'Error creating FTP user directories '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
