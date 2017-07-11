import ast
import django
import django.template

from integralstor_utils import zfs, audit, config, remote_replication, scheduler_utils, django_utils, rsync

from integral_view.forms import remote_replication_forms


def view_remote_replications(request):
    return_dict = {}
    try:
        modes, err = remote_replication.get_replication_modes()
        if err:
            raise Exception(
                'Could not read available replication modes: %s' % err)

        if 'mode' in request.GET:
            mode = str(request.GET['mode'])
            if mode not in modes:
                raise Exception("Malformed request. Please use the menus")
        else:
            mode = modes[0]
        select_mode = mode

        if "ack" in request.GET:
            if request.GET["ack"] == "cancelled":
                return_dict['ack_message'] = 'Selected replication successfully cancelled.'
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = 'Replication successfully scheduled.'
            elif request.GET["ack"] == "updated":
                return_dict['ack_message'] = 'Selected replication parameters successfully updated.'

        replications, err = remote_replication.get_remote_replications()
        if err:
            raise Exception(err)
        is_zfs = False
        is_rsync = False
        for replication in replications:
            if replication.get('mode') == 'zfs':
                is_zfs = True
            elif replication.get('mode') == 'rsync':
                is_rsync = True

        return_dict["replications"] = replications
        return_dict["modes"] = modes
        return_dict["select_mode"] = select_mode
        return_dict["is_zfs"] = is_zfs
        return_dict["is_rsync"] = is_rsync
        return django.shortcuts.render_to_response('view_remote_replications.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'View Remote Replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error retrieving replication informat'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_remote_replication(request):
    return_dict = {}
    try:
        datasets = []
        initial = {}
        mode = None
        select_mode = None

        modes, err = remote_replication.get_replication_modes()
        if err:
            raise Exception(
                'Could not read available replication modes: %s' % err)

        switches, err = rsync.get_available_switches()
        if err:
            raise Exception(
                'Could not read available rsync switches: %s' % err)

        pools, err = zfs.get_all_datasets_and_pools()
        if err:
            raise Exception(err)
        for pool in pools:
            if "/" in pool:
                datasets.append(pool)

        if request.method == "GET":
            if 'mode' in request.GET:
                mode = str(request.GET['mode'])
                if mode not in modes:
                    raise Exception("Malformed request. Please use the menus")
            else:
                mode = modes[0]
            select_mode = mode
            form = remote_replication_forms.CreateRemoteReplication(
                modes=modes, select_mode=select_mode, datasets=datasets, switches=switches)
            return_dict['form'] = form
            return_dict['switches'] = switches
            return django.shortcuts.render_to_response('create_remote_replication.html', return_dict, context_instance=django.template.context.RequestContext(request))

        elif request.method == "POST":
            req_ret_init, err = django_utils.get_request_parameter_values(
                request, ['modes', 'select_mode', 'source_dataset', 'target_ip'])
            if err:
                raise Exception(err)
            if ('modes' and 'select_mode' and 'source_dataset') not in req_ret_init:
                raise Exception("Malformed request. Please use the menus")

            select_mode = str(req_ret_init['select_mode'])
            initial['modes'] = modes
            initial['select_mode'] = req_ret_init['select_mode']
            initial['source_dataset'] = req_ret_init['source_dataset']

            if initial['select_mode'] == 'zfs':
                req_ret, err = django_utils.get_request_parameter_values(
                    request, ['target_pool'])
                if err:
                    raise Exception(err)
                if ('target_pool') not in req_ret or ('target_ip') not in req_ret_init:
                    raise Exception("Malformed request. Please use the menus")
                initial['target_pool'] = str(req_ret['target_pool'])
                initial['target_ip'] = str(req_ret_init['target_ip'])

            elif initial['select_mode'] == 'rsync':
                req_ret, err = django_utils.get_request_parameter_values(
                    request, ['rsync_type', 'local_path', 'remote_path'])
                if err:
                    raise Exception(err)
                if ('rsync_type' and 'local_path' and 'remote_path') not in req_ret:
                    raise Exception("Malformed request. Please use the menus")
                initial['switches'] = {}
                if 'switches' in request.POST:
                    switches_l = request.POST.getlist('switches')
                    for switch in switches_l:
                        s = ast.literal_eval(switch)
                        for k, v in s.items():
                            initial['switches'][k] = s[k]
                initial['rsync_type'] = str(req_ret['rsync_type'])
                initial['local_path'] = str(req_ret['local_path'])
                initial['remote_path'] = str(req_ret['remote_path'])
                if initial['rsync_type'] != 'local' and 'target_ip' not in req_ret_init:
                    raise Exception("Malformed request. Please use the menus")
                else:
                    initial['target_ip'] = str(req_ret_init['target_ip'])

            form = remote_replication_forms.CreateRemoteReplication(
                request.POST, initial=initial, modes=modes, select_mode=select_mode, datasets=datasets, switches=switches)
            return_dict['form'] = form
            return_dict['initial'] = initial
            return_dict['switches'] = switches

            if not form.is_valid():
                return django.shortcuts.render_to_response('create_remote_replication.html', return_dict, context_instance=django.template.context.RequestContext(request))

            if form.is_valid():
                cd = form.cleaned_data

                if cd['select_mode'] == 'zfs':
                    source_dataset = cd['source_dataset']
                    scheduler = request.POST.get('scheduler')
                    schedule = scheduler.split()
                    target_ip = cd['target_ip']
                    target_pool = cd['target_pool']
                    target_user_name = "replicator"

                    if (not target_ip) or (not target_pool) or (not source_dataset):
                        raise Exception("Incomplete request.")

                    existing_repl, err = remote_replication.get_remote_replications_with(
                        'zfs', {'source_dataset': source_dataset, 'target_ip': target_ip, 'target_pool': target_pool})
                    if err:
                        raise Exception(err)
                    if existing_repl:
                        raise Exception(
                            "A replication schedule already exists with matching entries/options.")

                    # Since cron_task_id is a required parameter pass -1 to
                    # represent its unavailability. Update when available.
                    remote_replication_id, err = remote_replication.add_remote_replication(
                        -1, 'zfs', {'source_dataset': source_dataset, 'target_ip': target_ip, 'target_user_name': target_user_name, 'target_pool': target_pool})
                    if err:
                        raise Exception(err)

                    py_scripts_path, err = config.get_python_scripts_path()
                    if err:
                        raise Exception(err)

                    cmd = '%s/add_remote_replication_task.py %s' % (
                        py_scripts_path, remote_replication_id)
                    description = 'ZFS replication of %s to pool %s on machine %s' % (
                        source_dataset, target_pool, target_ip)
                    cron_task_id, err = scheduler_utils.create_cron_task(
                        cmd, description, schedule[0], schedule[1], schedule[2], schedule[3], schedule[4])
                    if err:
                        raise Exception(err)

                    # Update cron_task_id which was previously set as -1
                    is_update, err = remote_replication.update_remote_replication(
                        remote_replication_id, cron_task_id)
                    if err:
                        raise Exception(
                            'Scheduling remote replication unsuccessfull: %s' % err)

                    crons, err = scheduler_utils.get_cron_tasks(cron_task_id)
                    if err:
                        raise Exception(err)
                    description += ' Scheduled for %s' % crons[0]['schedule_description']

                    audit.audit("create_remote_replication",
                                description, request)

                elif cd['select_mode'] == 'rsync':
                    source_path = None
                    target_path = None
                    target_ip = cd['target_ip']
                    target_user_name = "replicator"
                    switches_formed = None
                    switches = {}

                    rsync_type = cd['rsync_type']
                    if rsync_type == 'push':
                        source_path = cd['local_path']
                        target_path = cd['remote_path']
                    elif rsync_type == 'pull':
                        source_path = cd['remote_path']
                        target_path = cd['local_path']
                    elif rsync_type == 'local':
                        source_path = cd['local_path']
                        target_path = cd['remote_path']
                        target_user_name = "root"

                    scheduler = request.POST.get('scheduler')
                    schedule = scheduler.split()

                    if 'switches' in cd and cd['switches']:
                        for switch in cd['switches']:
                            s = ast.literal_eval(switch)
                            for k, v in s.items():
                                if v['is_arg']:
                                    v['arg_value'] = cd['%s_arg' % v['id']]
                            switches.update(s)

                    if switches:
                        switches_formed, err = rsync.form_switches_command(
                            switches)
                        if err:
                            raise Exception(
                                'Could not form rsync switch: %s' % err)

                    existing_repl, err = remote_replication.get_remote_replications_with(
                        'rsync', {'source_path': source_path, 'target_ip': target_ip, 'target_path': target_path})
                    if err:
                        raise Exception(err)
                    if existing_repl:
                        raise Exception(
                            "A replication schedule already exists with matching entries/options.")

                    # Since cron_task_id is a required parameter pass -1 to
                    # represent its unavailability. Update when available.
                    remote_replication_id, err = remote_replication.add_remote_replication(-1, 'rsync', {'rsync_type': rsync_type, 'short_switches': switches_formed['short'], 'long_switches': switches_formed['long'], 'source_path': source_path, 'target_path': target_path, 'target_ip': target_ip, 'target_user_name': target_user_name})
                    if err:
                        raise Exception(err)

                    py_scripts_path, err = config.get_python_scripts_path()
                    if err:
                        raise Exception(err)

                    cmd = '%s/add_remote_replication_task.py %s' % (
                        py_scripts_path, remote_replication_id)
                    if rsync_type == 'pull':
                        description = 'rsync replication of %s from %s to %s on local host' % (
                            source_path, target_ip, target_path)
                    elif rsync_type == 'push':
                        description = 'rsync replication of %s from local host to %s on %s' % (
                            source_path, target_path, target_ip)
                    elif rsync_type == 'local':
                        description = 'rsync replication of %s from local host to %s on local host' % (
                            source_path, target_path)

                    cron_task_id, err = scheduler_utils.create_cron_task(
                        cmd, description, schedule[0], schedule[1], schedule[2], schedule[3], schedule[4])
                    if err:
                        raise Exception(err)

                    # Update cron_task_id which was previously set as -1
                    is_update, err = remote_replication.update_remote_replication(
                        remote_replication_id, cron_task_id)
                    if err:
                        raise Exception(
                            'Scheduling remote replication unsuccessfull: %s' % err)

                    crons, err = scheduler_utils.get_cron_tasks(cron_task_id)
                    if err:
                        raise Exception(err)
                    description += ' Scheduled for %s' % crons[0]['schedule_description']

                    audit.audit("create_remote_replication",
                                description, request)

                return django.http.HttpResponseRedirect('/view_remote_replications?ack=created')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure remote replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring remote replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_remote_replication(request):
    return_dict = {}
    try:

        ret, err = django_utils.get_request_parameter_values(
            request, ['remote_replication_id'])
        if err:
            raise Exception(err)
        if 'remote_replication_id' not in ret:
            raise Exception(
                "Requested remote replication not found, please use the menus.")
        remote_replication_id = ret['remote_replication_id']
        replications, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception(err)
        if not replications:
            raise Exception('Specified replication definition not found')

        if request.method == "GET":
            return_dict['replication'] = replications[0]
            return django.shortcuts.render_to_response('update_remote_replication.html', return_dict, context_instance=django.template.context.RequestContext(request))
        elif request.method == "POST":
            if ('scheduler' and 'cron_task_id') not in request.POST:
                raise Exception("Incomplete request.")
            cron_task_id = request.POST.get('cron_task_id')
            scheduler = request.POST.get('scheduler')
            schedule = scheduler.split()
            description = ''
            description += replications[0]['description']

            is_update, err = scheduler_utils.update_cron_schedule(
                cron_task_id, 'root', schedule[0], schedule[1], schedule[2], schedule[3], schedule[4])
            if err:
                raise Exception(err)

            crons, err = scheduler_utils.get_cron_tasks(cron_task_id)
            if err:
                raise Exception(err)
            description += '\nScheduled for %s' % crons[0]['schedule_description']

            audit.audit("modify_remote_replication", description, request)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=updated')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure remote replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_remote_replication(request):
    return_dict = {}
    try:
        ret, err = django_utils.get_request_parameter_values(
            request, ['remote_replication_id'])
        if err:
            raise Exception(err)
        if 'remote_replication_id' not in ret:
            raise Exception(
                "Requested remote replication not found, please use the menus.")
        remote_replication_id = ret['remote_replication_id']
        return_dict['remote_replication_id'] = remote_replication_id
        replications, err = remote_replication.get_remote_replications(
            remote_replication_id)
        if err:
            raise Exception(err)
        if not replications:
            raise Exception(
                'Specified remote replication definition not found')

        if request.method == "GET":
            return_dict['replication'] = replications[0]
            return django.shortcuts.render_to_response("delete_remote_replication_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = django_utils.get_request_parameter_values(
                request, ['cron_task_id'])
            if err:
                raise Exception(err)
            if 'cron_task_id' not in ret:
                raise Exception("Request not found, please use the menus.")
            cron_task_id = ret['cron_task_id']

            ret, err = remote_replication.delete_remote_replication(
                remote_replication_id)
            if err:
                raise Exception(err)

            cron_remove, err = scheduler_utils.delete_cron(
                int(cron_task_id))
            if err:
                raise Exception(err)
            audit.audit("remove_remote_replication",
                        replications[0]['description'], request)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=cancelled')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Remove remote replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error removing remote replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
