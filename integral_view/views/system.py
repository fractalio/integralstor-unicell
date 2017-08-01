import django
import django.template

from integral_view.forms import system_forms
from integralstor_utils import django_utils, cifs as cifs_utils, rsync, logger, ntp, vsftp, remote_replication, scheduler_utils, zfs, networking, pki
from integralstor import cifs as cifs_integralstor, nfs, iscsi_stgt, local_users, audit, alerts, mail, datetime_utils


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
                                  'delete_zfs_zvols_and_snapshots': 'ZFS block device volumes and snapshots (user data)'}
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
                            result, err = cifs_utils.delete_all_shares()
                            if result:
                                cifs_integralstor.reload_configuration()
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
                            res1, err1 = scheduler_utils.delete_all_tasks()
                            res2, err2 = scheduler_utils.delete_all_logs()
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
                            result, err = cifs_utils.delete_auth_settings()
                            if not err:
                                cifs_integralstor.reload_configuration()
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
                            url = '/view_system_info?ack=system_datetimetz_set'
                            audit_str = 'System date set to "%s", system time set to "%s", system timezone set to "%s"' % (
                                output['date_set_to'], output['time_set_to'], output['timezone_set_to'])
                            # print audit_str
                    elif "date_set" in output and "time_set" in output:
                        if output["date_set"] == True and output["time_set"] == True:
                            url = "/view_system_info?ack=system_datetime_set"
                            audit_str = 'System date set to "%s" and system time set to "%s"' % (
                                output['date_set_to'], output['time_set_to'])
                    elif 'date_set' in output and 'timezone_set' in output:
                        if output['date_set'] == True and output['timezone_set'] == True:
                            url = "/view_system_info?ack=system_date_timezone_set"
                            audit_str = 'System date set to "%s" and system timezone set to "%s"' % (
                                output['date_set_to'], output['timezone_set_to'])
                    elif 'time_set' in output and 'timezone_set' in output:
                        if output['time_set'] == True and output['timezone_set'] == True:
                            url = '/view_system_info?ack=system_time_timezone_set'
                            audit_str = 'System time set to "%s" and system timezone set to "%s"' % (
                                output['time_set_to'], output['timezone_set_to'])
                    elif "time_set" in output:
                        if output["time_set"] == True:
                            url = "/view_system_info?ack=system_time_set"
                            audit_str = 'System time set to "%s"' % output['time_set_to']
                    elif "date_set" in output:
                        if output["date_set"] == True:
                            url = "/view_system_info?ack=system_date_set"
                            audit_str = 'System date set to "%s"' % output['date_set_to']
                    elif 'timezone_set' in output:
                        if output['timezone_set'] == True:
                            url = '/view_system_info?ack=system_timezone_set'
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
        return django.http.HttpResponseRedirect("/view_system_info")

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
