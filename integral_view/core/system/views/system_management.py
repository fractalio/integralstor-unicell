import django
import django.template
from django.contrib.auth.decorators import login_required

import zipfile
import os
import io
import json
import shutil

from integral_view.forms import common_forms
from integral_view.core.system.forms import  system_forms
from integral_view.core.keys_certs.forms import keys_certs_forms

from integralstor import cifs, nfs, iscsi_stgt, local_users, audit, alerts, mail, datetime_utils, remote_replication, rsync, tasks_utils, django_utils, vsftp, ntp, pki, logs, logger, zfs, networking, config, system_info, manifest_status, services_management, command, nginx, mail

def view_email_settings(request):
    return_dict = {}
    try:
        d, err = mail.load_email_settings()
        if err:
            raise Exception(err)
        if not d:
            return_dict["email_not_configured"] = True
        else:
            if d["tls"]:
                d["tls"] = True
            else:
                d["tls"] = False
            return_dict["email_settings"] = d
        ret, err = django_utils.get_request_parameter_values(
            request, ['ack', 'err', 'sent_mail'])
        if err:
            raise Exception(err)
        if 'ack' in ret and ret['ack'] == 'saved':
            return_dict["ack_message"] = 'Email settings have successfully been updated.'
        if 'err' in ret:
            return_dict["err"] = ret['err']
        if 'sent_mail' in ret:
            return_dict["sent_mail"] = ret['sent_mail']
        return django.shortcuts.render_to_response('view_email_settings.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'View email notification settings'
        return_dict['tab'] = 'email_tab'
        return_dict["error"] = 'Error viewing email notification settings'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


def update_email_settings(request):

    try:
        return_dict = {}
        url = "update_email_settings.html"
        if request.method == "GET":
            d, err = mail.load_email_settings()
            if err:
                raise Exception(err)
            if not d:
                form = admin_forms.ConfigureEmailForm()
            else:
                if 'tls' in d and d["tls"]:
                    d["tls"] = True
                else:
                    d["tls"] = False
                form = admin_forms.ConfigureEmailForm(initial={'server': d["server"], 'port': d["port"], 'tls': d["tls"], 'username': d[
                                                      "username"], 'pswd': ""})
        else:
            form = admin_forms.ConfigureEmailForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                # print "Saving : "
                ret, err = mail.save_email_settings(cd)
                if err:
                    raise Exception(err)

                if 'rcpt_list' in cd:
                    ret, err = mail.send_mail(cd["server"], cd["port"], cd["username"], cd["pswd"], cd["tls"], cd["rcpt_list"], "Test email from IntegralStor",
                                              "This is a test email sent by the IntegralStor system in order to confirm that your email settings are working correctly.")
                if err:
                    raise Exception(err)
                if ret:
                    return django.http.HttpResponseRedirect("/system/view_email_settings?ack=saved&sent_mail=1")
                else:
                    return django.http.HttpResponseRedirect("/system/view_email_settings?ack=saved&err=%s" % err)
        return_dict["form"] = form
        return django.shortcuts.render_to_response(url, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Change email notification settings'
        return_dict['tab'] = 'email_tab'
        return_dict["error"] = 'Error changing email notification settings'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


def view_https_mode(request):
    return_dict = {}
    try:
        mode, err = nginx.get_nginx_access_mode()
        if err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "set_to_secure":
                return_dict['ack_message'] = "The IntegralView access mode has been successfully set to secure(HTTPS). The server has been scheduled to restart. Please change your browser to access IntegralView using https://<integralview_ip_address>"
            elif request.GET["ack"] == "set_to_nonsecure":
                return_dict['ack_message'] = "The IntegralView access mode has been successfully set to non-secure(HTTP). The server has been scheduled to restart. Please change your browser to access IntegralView using http://<integralview_ip_address>"

        return_dict['port'] = mode['port']
        return django.shortcuts.render_to_response('view_https_mode.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Integralview access mode'
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error loading IntegralView access mode'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_https_mode(request):
    return_dict = {}
    try:
        ret, err = django_utils.get_request_parameter_values(request, [
                                                             'change_to'])
        if err:
            raise Exception(err)
        if 'change_to' not in ret:
            raise Exception("Invalid request, please use the menus.")
        change_to = ret['change_to']
        return_dict['change_to'] = change_to

        cert_list, err = pki.get_ssl_certificates()
        if err:
            raise Exception(err)
        if not cert_list:
            raise Exception(
                'No certificates have been created. Please create a certificate/key pair before you change the access method')

        if request.method == "GET":
            if change_to == 'secure':
                form = keys_certs_forms.SetHttpsModeForm(cert_list=cert_list)
                return_dict['form'] = form
                return django.shortcuts.render_to_response("update_https_mode.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return_dict['conf_message'] = 'Are you sure you want to disable the secure access mode for IntegralView?'
                return django.shortcuts.render_to_response("update_http_mode_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if change_to == 'secure':
                form = keys_certs_forms.SetHttpsModeForm(
                    request.POST, cert_list=cert_list)
                return_dict['form'] = form
                if not form.is_valid():
                    return django.shortcuts.render_to_response("update_https_mode.html", return_dict, context_instance=django.template.context.RequestContext(request))
                cd = form.cleaned_data
            if change_to == 'secure':
                pki_dir, err = config.get_pki_dir()
                if err:
                    raise Exception(err)
                cert_loc = '%s/%s/%s.cert' % (pki_dir,
                                              cd['cert_name'], cd['cert_name'])
                if not os.path.exists(cert_loc):
                    raise Exception('Error locating certificate')
                ret, err = nginx.generate_nginx_conf(True, cert_loc, cert_loc)
                if err:
                    raise Exception(err)
            else:
                ret, err = nginx.generate_nginx_conf(False)
                if err:
                    raise Exception(err)
            audit_str = "Changed the IntegralView access mode to '%s'" % change_to
            audit.audit("set_https_mode", audit_str, request)

        redirect_url = "https://" if change_to == "secure" else "http://"
        redirect_url = redirect_url + \
            request.META["HTTP_HOST"] + \
            "/system/view_https_mode?ack=set_to_%s" % change_to
        restart, err = tasks_utils.create_task('Chaging IntegralView access mode', [
            {'Restarting Web Server': 'service nginx restart'}], 2)
        if err:
            raise Exception(err)
        return django.http.HttpResponseRedirect(redirect_url)

    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Modify Integralview access mode'
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error modifying IntegralView access mode'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def reboot_or_shutdown(request):
    return_dict = {}
    audit_str = ""
    try:
        minutes_to_wait = 1
        return_dict['minutes_to_wait'] = minutes_to_wait
        ret, err = django_utils.get_request_parameter_values(request, ['do'])
        if err:
            raise Exception(err)
        if 'do' not in ret:
            raise Exception("Invalid request, please use the menus.")
        do = ret['do']
        return_dict['do'] = do
        if request.method == "GET":
            return django.shortcuts.render_to_response("reboot_or_shutdown.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if 'conf' not in request.POST:
                raise Exception('Unknown action. Please use the menus')
            audit.audit('reboot_shutdown', 'System %s initiated' %
                        do, request)
            if do == 'reboot':
                command.execute_with_rc('shutdown -r +%d' % minutes_to_wait)
            elif do == 'shutdown':
                command.execute_with_rc('shutdown -h +%d' % minutes_to_wait)
            return django.shortcuts.render_to_response("reboot_or_shutdown_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Reboot or Shutdown Failure'
        return_dict['tab'] = 'reboot_tab'
        return_dict["error"] = 'Error Rebooting'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))
@login_required
#@django.views.decorators.csrf.csrf_exempt
def flag_node(request):

    try:
        return_dict = {}
        if "node" not in request.GET:
            raise Exception("Error flagging node. No node specified")

        node_name = request.GET["node"]
        blink_time = 255
        use_salt, err = config.use_salt()
        if use_salt:
            import salt.client
            client = salt.client.LocalClient()
            ret = client.cmd(node_name, 'cmd.run', [
                             'ipmitool chassis identify %s' % (blink_time)])
            print ret
            if ret[node_name] == 'Chassis identify interval: %s seconds' % (blink_time):
                return django.http.HttpResponse("Success")
            else:
                raise Exception("")
        else:
            out_list, err = command.get_command_output(
                'service winbind status')
            if err:
                raise Exception(err)
            if 'Chassis identify interval: %s seconds' % (blink_time) in out_list[0]:
                return django.http.HttpResponse("Success")
            else:
                raise Exception("")
    except Exception, e:
        return django.http.HttpResponse("Error")

def access_shell(request):
    return_dict = {}
    try:
        status, err = services_management.get_service_status(['shellinaboxd'])
        if err:
            raise Exception(err)
        if status['status_str'] == "Running":
            return django.shortcuts.render_to_response("shell_access.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            raise Exception(
                "Shell Service is not running. Start the service and visit the page again")

    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Shell Access'
        return_dict['tab'] = 'shell_tab'
        return_dict["error"] = 'Error loading Shell, Check the service'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

@login_required
def update_manifest(request):
    return_dict = {}
    try:
        if request.method == "GET":
            from integralstor import manifest_status as iu
            mi, err = iu.generate_manifest_info(rescan_for_disks=True)
            # print mi, err
            if err:
                raise Exception(err)
            if not mi:
                raise Exception('Could not load new configuration')
            return_dict["mi"] = mi  # Need the hostname here.
            return django.shortcuts.render_to_response("update_manifest.html", return_dict, context_instance=django.template.context.RequestContext(request))
        elif request.method == "POST":
            python_scripts_path, err = config.get_python_scripts_path()
            if err:
                raise Exception(err)
            ss_path, err = config.get_system_status_path()
            if err:
                raise Exception(err)
            #(ret,rc), err = command.execute_with_rc("python %s/generate_manifest.py %s"%(python_scripts_path, ss_path))
            ret, err = command.get_command_output(
                "python %s/generate_manifest.py %s" % (python_scripts_path, ss_path))
            # print 'mani', ret, err
            if err:
                raise Exception(err)
            #(ret,rc), err = command.execute_with_rc("python %s/generate_status.py %s"%(config.get_python_scripts_path(),config.get_system_status_path()))
            ret, err = command.get_command_output(
                "python %s/generate_status.py %s" % (python_scripts_path, ss_path))
            # print 'stat', ret, err
            if err:
                raise Exception(err)
            audit_str = 'Reloaded system configuration after hardware scan'
            audit.audit('update_manifest',
                        audit_str, request)
            return django.http.HttpResponseRedirect("/system/view_system_info/")
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Reload system configuration'
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error reloading system configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def update_org_info(request):
    return_dict = {}
    try:
        if request.method == "GET":
            org_info, err = system_info.get_org_info()
            if err:
                raise Exception(err)
            form = system_forms.OrgInfoForm(initial=org_info)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("update_org_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
        elif request.method == "POST":
            form = system_forms.OrgInfoForm(request.POST)
            return_dict["form"] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_org_info.html", return_dict, context_instance=django.template.context.RequestContext(request))

            cd = form.cleaned_data
            ret, err = system_info.update_org_info(cd)
            if err:
                raise Exception(err)

            audit_str = 'Updated organization information: %s' % str(cd)
            audit.audit('update_org_info',
                        audit_str, request)
            return django.http.HttpResponseRedirect("/system/view_system_info?ack=update_org_info_ok")
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = "Update organization's information"
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error updating organization information'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def view_system_info(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "system_time_set":
                return_dict['ack_message'] = "Time successfully updated"
            elif request.GET["ack"] == "system_date_set":
                return_dict['ack_message'] = "Date successfully updated"
            elif request.GET["ack"] == "system_datetime_set":
                return_dict['ack_message'] = "Date and time successfully updated"
            elif request.GET["ack"] == 'system_timezone_set':
                return_dict['ack_message'] = "Timezone successfully updated"
            elif request.GET['ack'] == 'system_date_timezone_set':
                return_dict['ack_message'] = 'Date and timezone successfully updated'
            elif request.GET['ack'] == 'system_time_timezone_set':
                return_dict['ack_message'] = 'Time and timezone successfully updated'
            elif request.GET['ack'] == 'system_datetimetz_set':
                return_dict['ack_message'] = 'Date, time and timezone successfully updated'
            elif request.GET['ack'] == 'config_uploaded':
                return_dict['ack_message'] = 'Configuration information successfully uploaded'
            elif request.GET['ack'] == 'update_org_info_ok':
                return_dict['ack_message'] = 'Updated orgnazation information successfully'

        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
        org_info, err = system_info.get_org_info()
        if err:
            raise Exception(err)
        return_dict['org_info'] = org_info

        now_epoch, err = datetime_utils.get_epoch(
            when='now', num_previous_days=0)
        if err:
            raise Exception(err)
        now, err = datetime_utils.convert_from_epoch(
            now_epoch, return_format='datetime', to='local')
        if err:
            raise Exception(err)
        milliseconds = int(now_epoch * 1000)
        if err:
            raise Exception(err)
        system_timezone, err = datetime_utils.get_system_timezone()
        if err:
            raise Exception(err)
        return_dict['date_str'] = now.strftime("%A %d %B %Y")
        return_dict['time'] = now
        return_dict['milliseconds'] = milliseconds
        return_dict['system_timezone'] = system_timezone['system_timezone']
        # print return_dict['system_timezone']
        return_dict['system_info'] = si
        if "from" in request.GET:
            frm = request.GET["from"]
            return_dict['frm'] = frm
        return_dict['node'] = si
        return django.shortcuts.render_to_response("view_system_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'System configuration'
        return_dict['tab'] = 'node_info_tab'
        return_dict["error"] = 'Error loading system configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def reset_to_factory_defaults(request):
    return_dict = {}
    try:
        component_descriptions = {'delete_cifs_shares': 'Windows shares',
                                  'delete_nfs_exports': 'NFS exports',
                                  'delete_rsync_shares': 'Rsync shares',
                                  'delete_iscsi_targets': 'ISCSI targets',
                                  'delete_local_users': 'local users',
                                  'delete_local_groups': 'local groups',
                                  'delete_dns_settings': 'DNS settings',
                                  'delete_network_interface_settings': 'network interface settings',
                                  'delete_network_bonds': 'network bonds',
                                  #'delete_network_vlans':'network VLANs',
                                  'reset_hostname': 'hostname and domain name',
                                  'default_ip': 'set default IP',
                                  'delete_ssl_certificates': 'SSL certificates',
                                  'delete_ssh_authorized_keys': 'SSH authorized keys',
                                  'delete_ssh_fingerprints': 'SSH host fingerprints',
                                  'delete_audits': 'audit trail',
                                  'delete_alerts': 'alerts',
                                  'delete_logs': 'logs',
                                  'delete_remote_replications': 'scheduled remote replications',
                                  'delete_tasks_and_logs': 'background tasks and logs',
                                  'reset_cifs_settings': 'Windows access settings',
                                  'reset_ntp_settings': 'NTP settings',
                                  'reset_ftp_settings': 'FTP settings',
                                  'delete_email_settings': 'email server settings',
                                  'delete_zfs_pools': 'ZFS pools (user data)',
                                  'delete_zfs_datasets_and_snapshots': 'ZFS datasets and snapshots (user data)',
                                  'delete_zfs_zvols_and_snapshots': 'ZFS block device volumes and snapshots (user data)',
                                  'delete_org_info': 'Delete organization information'}
        if request.method == 'GET':
            form = system_forms.FactoryDefaultsForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response('reset_to_factory_defaults.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            req_ret, err = django_utils.get_request_parameter_values(request, [
                'conf'])
            if err:
                raise Exception(err)
            form = system_forms.FactoryDefaultsForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'conf' not in req_ret:
                    # No confirmation yet so process the form
                    selected_components = []
                    for key in cd.keys():
                        if cd[key]:
                            selected_components.append(
                                component_descriptions[key])
                    if ('delete_zfs_pools' in cd and cd['delete_zfs_pools']) or ('delete_zfs_datasets_and_snapshots' in cd and cd['delete_zfs_datasets_and_snapshots']) or ('delete_zfs_zvols_and_snapshots' in cd and cd['delete_zfs_zvols_and_snapshots']):
                        return_dict['data_loss'] = 'yes'
                    return_dict['selected_components_str'] = ','.join(
                        selected_components)
                    return_dict['form'] = form
                    return django.shortcuts.render_to_response('reset_to_factory_defaults_conf.html', return_dict, context_instance=django.template.context.RequestContext(request))
                else:
                    # Got the confirmation so now do the work.
                    success_list = []
                    failed_list = []
                    error_dict = {}
                    for key in cd.keys():
                        result = False
                        if not cd[key]:
                            continue
                        if key == 'delete_cifs_shares' and cd[key]:
                            result, err = cifs.delete_all_shares()
                            if result:
                                cifs.reload_configuration()
                        elif key == 'delete_nfs_exports':
                            result, err = nfs.delete_all_exports()
                        elif key == 'delete_rsync_shares':
                            result, err = rsync.delete_all_rsync_shares()
                        elif key == 'delete_iscsi_targets':
                            result, err = iscsi_stgt.delete_all_targets()
                        elif key == 'delete_local_users':
                            result, err = local_users.delete_all_local_users()
                        elif key == 'delete_local_groups':
                            result, err = local_users.delete_all_local_groups()
                        elif key == 'delete_ssl_certificates':
                            result, err = pki.delete_all_ssl_certificates()
                        elif key == 'delete_ssh_authorized_keys':
                            result, err = pki.delete_authorized_keys(
                                'replicator')
                        elif key == 'delete_ssh_fingerprints':
                            result, err = pki.delete_fingerprints('replicator')
                        elif key == 'delete_audits':
                            result, err = audit.delete_all_audits()
                        elif key == 'delete_alerts':
                            result, err = alerts.delete_all_alerts()
                        elif key == 'delete_logs':
                            result, err = logger.zero_logs()
                        elif key == 'delete_remote_replications':
                            result, err = remote_replication.delete_all_remote_replications()
                        elif key == 'delete_tasks_and_logs':
                            res1, err1 = tasks_utils.delete_all_tasks()
                            res2, err2 = logs.delete_all_logs()
                            err = None
                            result = False
                            if err1 and err2:
                                err = '%s\t%s' % (err1, err2)
                            elif err1:
                                err = 'Sucessfully deleted all tasks logs. \t%s' % err1
                            elif err2:
                                err = 'Sucessfully deleted all tasks. \t%s' % err2
                            else:
                                result = True
                        elif key == 'reset_cifs_settings':
                            result, err = cifs.delete_auth_settings()
                            if not err:
                                cifs.reload_configuration()
                        elif key == 'reset_ntp_settings':
                            result, err = ntp.update_integralstor_ntp_servers(
                                ['0.centos.pool.ntp.org', '1.centos.pool.ntp.org', '2.centos.pool.ntp.org', '3.centos.pool.ntp.org'])
                        elif key == 'reset_ftp_settings':
                            result, err = vsftp.delete_ftp_config()
                        elif key == 'delete_email_settings':
                            result, err = mail.delete_email_settings()
                        elif key == 'delete_zfs_pools':
                            result, err = zfs.delete_all_pools(force=True)
                        elif key == 'delete_zfs_datasets_and_snapshots':
                            result, err = zfs.delete_all_datasets(
                                dataset_type='filesystem', recursive=True, force=True)
                        elif key == 'delete_zfs_zvols_and_snapshots':
                            result, err = zfs.delete_all_datasets(
                                dataset_type='volume', recursive=True, force=True)
                        elif key == 'reset_hostname':
                            result, err = networking.update_hostname(
                                'localhost', 'localdomain')
                        elif key == 'delete_dns_settings':
                            result, err = networking.delete_name_servers()
                        # TODO: get vlans sorted out
                        # elif key == 'delete_network_vlans':
                        #    pass
                        elif key == 'delete_network_interface_settings':
                            result, err = networking.delete_interfaces_connection()
                        elif key == 'delete_network_bonds':
                            result, err = networking.delete_all_bonds()
                        elif key == 'default_ip':
                            result, err = networking.default_ip_on_next_boot()
                        elif key == 'delete_org_info':
                            result, err = system_info.delete_org_info()

                        if result:
                            success_list.append(component_descriptions[key])
                        else:
                            failed_list.append(component_descriptions[key])
                            error_dict[component_descriptions[key]] = err
                    audit_str = ''
                    if success_list:
                        audit_str += 'Factory defaults reset of the following components succeeded : '
                        audit_str += ', '.join(success_list)
                        audit_str += '. '
                    if failed_list:
                        audit_str += 'Factory defaults reset of the following components failed : '
                        audit_str += ', '.join(failed_list)
                        audit_str += '. '
                    audit.audit('factory_defaults_reset', audit_str, request)
                    return_dict['success_list'] = success_list
                    return_dict['error_dict'] = error_dict
                    return django.shortcuts.render_to_response('reset_to_factory_defaults_result.html', return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                # Bad form
                return_dict['form'] = form
                return django.shortcuts.render_to_response('reset_to_factory_defaults.html', return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict["base_template"] = 'system_base.html'
        return_dict['tab'] = 'system_info_tab'
        return_dict['page_title'] = 'Reset to factory defaults'
        return_dict["error"] = 'Error resetting to factory defaults'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_system_date_time(request):
    return_dict = {}
    try:
        if request.method == 'GET':
            form = system_forms.DateTimeForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_system_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))

        if request.method == 'POST':
            form = system_forms.DateTimeForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                output, err = datetime_utils.update_system_date_time(
                    cd["system_date"], cd["system_time"], cd["system_timezone"])
                if err:
                    raise Exception(err)
                else:
                    if 'date_set' in output and 'time_set' in output and 'timezone_set' in output:
                        if output['date_set'] == True and output['time_set'] == True and output['timezone_set'] == True:
                            url = '/system/view_system_info?ack=system_datetimetz_set'
                            audit_str = 'System date set to "%s", system time set to "%s", system timezone set to "%s"' % (
                                output['date_set_to'], output['time_set_to'], output['timezone_set_to'])
                            # print audit_str
                    elif "date_set" in output and "time_set" in output:
                        if output["date_set"] == True and output["time_set"] == True:
                            url = "/system/view_system_info?ack=system_datetime_set"
                            audit_str = 'System date set to "%s" and system time set to "%s"' % (
                                output['date_set_to'], output['time_set_to'])
                    elif 'date_set' in output and 'timezone_set' in output:
                        if output['date_set'] == True and output['timezone_set'] == True:
                            url = "/system/view_system_info?ack=system_date_timezone_set"
                            audit_str = 'System date set to "%s" and system timezone set to "%s"' % (
                                output['date_set_to'], output['timezone_set_to'])
                    elif 'time_set' in output and 'timezone_set' in output:
                        if output['time_set'] == True and output['timezone_set'] == True:
                            url = '/system/view_system_info?ack=system_time_timezone_set'
                            audit_str = 'System time set to "%s" and system timezone set to "%s"' % (
                                output['time_set_to'], output['timezone_set_to'])
                    elif "time_set" in output:
                        if output["time_set"] == True:
                            url = "/system/view_system_info?ack=system_time_set"
                            audit_str = 'System time set to "%s"' % output['time_set_to']
                    elif "date_set" in output:
                        if output["date_set"] == True:
                            url = "/system/view_system_info?ack=system_date_set"
                            audit_str = 'System date set to "%s"' % output['date_set_to']
                    elif 'timezone_set' in output:
                        if output['timezone_set'] == True:
                            url = '/system/view_system_info?ack=system_timezone_set'
                            audit_str = 'System timezone set to "%s"' % output['timezone_set_to']

                    audit.audit("update_system_datetimezone",
                                audit_str, request)

                    return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("update_system_date_time.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict["base_template"] = 'system_base.html'
        return_dict['tab'] = 'system_info_tab'
        return_dict['page_title'] = 'Update system and hardware date and time'
        return_dict["error"] = 'Error Performing Date Time Update'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
        return django.http.HttpResponseRedirect("/system/view_system_info")


upload_download_conf_dirs = ['conf_files', 'db', 'pki']
upload_download_logs = {'targets_conf': '/etc/tgt/targets.conf', 'smb_conf': '/etc/samba/smb.conf', 'ntp_conf': '/etc/ntp.conf', 'krb5_conf': '/etc/krb5.conf', 'nfs': '/etc/exports',
                        'ftp': '/etc/vsftpd/vsftpd.conf'}


def download_sys_info(request):
    return_dict = {}
    try:
        config_dir, err = config.get_config_dir()
        if err:
            raise Exception(err)
        zf_name = "system_info.zip"
        try:
            out = io.BytesIO()
            zf = zipfile.ZipFile(out, 'w')
            abs_src = os.path.abspath(config_dir)
            lu, err = local_users.get_local_users()
            if err:
                raise Exception(err)
            lg, err = local_users.get_local_groups()
            if err:
                raise Exception(err)
            with open('/tmp/local_users_tmp', 'w') as fd:
                json.dump(lu, fd, indent=2)
            with open('/tmp/local_groups_tmp', 'w') as fd:
                json.dump(lg, fd, indent=2)
            zf.write('/tmp/local_users_tmp', 'local_users')
            zf.write('/tmp/local_groups_tmp', 'local_groups')
            for conf_subdir in upload_download_conf_dirs:
                for dirname, subdirs, files in os.walk('%s/%s' % (config_dir, conf_subdir)):
                    for filename in files:
                        absname = os.path.abspath(
                            os.path.join(dirname, filename))
                        arcname = absname[len(abs_src) + 1:]
                        zf.write(absname, arcname)
            for key, value in upload_download_logs.iteritems():
                if os.path.isfile(value):
                    zf.write(value, key)
            zf.close()
            audit_str = 'Downloaded system configuration.'
            audit.audit('download_configuration',
                        audit_str, request)
        except Exception as e:
            raise Exception("Error compressing remote log file : %s" % str(e))
        response = django.http.HttpResponse(
            out.getvalue(), content_type='application/x-compressed')
        response['Content-disposition'] = 'attachment; filename=%s' % (
            zf_name)
        return response
    except Exception as e:
        return_dict["base_template"] = 'system_base.html'
        return_dict['tab'] = 'system_info_tab'
        return_dict["page_title"] = 'Download system configuration'
        return_dict["error"] = 'Error downloading system configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def _handle_uploaded_file(f):
    try:
        with open('/tmp/upload.zip', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    except Exception, e:
        return False, 'Error processing upload file : %s' % str(e)
    else:
        return True, None


def _copy_and_overwrite(from_path, to_path):
    try:
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(from_path, to_path)
    except Exception, e:
        return False, 'Error copying/overwriting directory : %s' % str(e)
    else:
        return True, None


def _copy_file_and_overwrite(from_path, to_path):
    try:
        shutil.copyfile(from_path, to_path)
    except Exception, e:
        return False, 'Error copying/overwriting file : %s' % str(e)
    else:
        return True, None


def upload_sys_info(request):
    return_dict = {}
    try:
        config_dir, err = config.get_config_dir()
        if err:
            raise Exception(err)
        if request.method == "POST":
            status, err = _handle_uploaded_file(request.FILES['file_field'])
            if err:
                raise Exception(err)
            display_name, err = config.get_config_dir()
            if err:
                raise Exception(err)
            zip = zipfile.ZipFile('/tmp/upload.zip', 'r')
            data = zip.namelist()
            move = zip.extractall("/tmp/upload_system_config/")
            logs = {'smb_conf': '/etc/samba/smb.conf', 'ntp_conf': '/etc/ntp.conf', 'krb5_conf': '/etc/krb5.conf', 'nfs': '/etc/exports',
                    'ftp': '/etc/vsftpd/vsftpd.conf'}
            if os.path.isfile('/tmp/upload_system_config/local_groups'):
                groups = None
                with open('/tmp/upload_system_config/local_groups', 'r') as f:
                    groups = json.load(f)
                if groups:
                    for group in groups:
                        # print 'creating group ', group
                        ret, err = local_users.create_local_group(
                            group['grpname'])
                        if err:
                            raise Exception(err)
                # print 'groups - ', groups
            if os.path.isfile('/tmp/upload_system_config/local_users'):
                users = None
                with open('/tmp/upload_system_config/local_users', 'r') as f:
                    users = json.load(f)
                if users:
                    default_group_name, err = config.get_users_default_group()
                    if err:
                        raise Exception(err)
                    default_gid, err = config.get_system_uid_gid(
                        default_group_name, 'group')
                    if err:
                        raise Exception(err)
                    for user in users:
                        # print 'creating user ', user
                        # print 'username is ', user['comment'][18:]
                        ret, err = local_users.create_local_user(
                            user['username'], user['comment'][18:], 'password', default_gid)
                        if err:
                            raise Exception(err)
                        if 'other_groups' in user and user['other_groups']:
                            # print 'adding other groups'
                            for g in user['other_groups']:
                                ret, err = local_users.set_group_membership(
                                    g, [user['username']])
                                if err:
                                    raise Exception(err)
                # print 'users - ', users
            for key, value in upload_download_logs.iteritems():
                if key and os.path.isfile("/tmp/upload_system_config/" + key):
                    # print 'overwriting ', "/tmp/upload_system_config/%s"%key,
                    # 'to ', value
                    ret, err = _copy_file_and_overwrite(
                        "/tmp/upload_system_config/%s" % key, value)
                    if err:
                        raise Exception(err)
            for dir in upload_download_conf_dirs:
                if os.path.isdir("/tmp/upload_system_config/%s" % dir):
                    # print 'overwriting ', "/tmp/upload_system_config/%s"%dir,
                    # ' to ', '%s/%s'%(config_dir,dir)
                    ret, err = _copy_and_overwrite(
                        "/tmp/upload_system_config/%s" % dir, '%s/%s' % (config_dir, dir))
                    if err:
                        raise Exception(err)
            services_restart_list = ['ntpd', 'smb',
                                     'winbind', 'tgtd', 'nfs', 'vsftpd']
            for service in services_restart_list:
                ret, err = services_management.update_service_status(
                    service, 'restart')
                if err:
                    raise Exception(err)
            audit_str = 'Upload of an external system configuration completed successfully.'
            audit.audit('upload_configuration',
                        audit_str, request)
            return django.http.HttpResponseRedirect("/system/view_system_info?ack=config_uploaded")
        else:
            form = common_forms.FileUploadForm()
            return_dict["form"] = form
            return django.shortcuts.render_to_response("upload_sys_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        audit_str = 'Upload of an external system configuration failed : %s.' % str(
            e)
        audit.audit('upload_configuration',
                    audit_str, request)
        return_dict["base_template"] = 'system_base.html'
        return_dict['tab'] = 'system_info_tab'
        return_dict["page_title"] = 'Upload system configuration'
        return_dict["error"] = 'Error uploading system configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
