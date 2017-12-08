import ast
import django
import django.template

from integralstor import audit, rsync, remote_replication, scheduler_utils, django_utils, zfs, config

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
            elif request.GET["ack"] == "pause_schedule_updated":
                return_dict['ack_message'] = 'Replication pause schedule successfully updated.'

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
            # check for parameters that are required initially for both
            # modes: zfs and rsync
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
                # check for parameters that are relevant to ZFS mode
                req_ret, err = django_utils.get_request_parameter_values(
                    request, ['target_pool'])
                if err:
                    raise Exception(err)
                if ('target_pool') not in req_ret or ('target_ip') not in req_ret_init:
                    raise Exception("Malformed request. Please use the menus")
                initial['target_pool'] = str(req_ret['target_pool'])
                initial['target_ip'] = str(req_ret_init['target_ip'])

            elif initial['select_mode'] == 'rsync':
                # check for parameters that are relevant to rsync mode
                req_ret, err = django_utils.get_request_parameter_values(
                    request, ['rsync_type', 'local_path', 'remote_path'])
                if err:
                    raise Exception(err)
                if ('rsync_type' and 'local_path' and 'remote_path') not in req_ret:
                    raise Exception("Malformed request. Please use the menus")
                initial['switches'] = {}
                if 'switches' in request.POST:
                    # if switches were selected, retain their values.
                    switches_l = request.POST.getlist('switches')
                    for switch in switches_l:
                        # switch dict is retained as string in the
                        # request. Convert it.
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
                # well formed
                cd = form.cleaned_data

                # pass request and cleaned_data to the respective
                # mode functions
                if cd['select_mode'] == 'zfs':
                    ret, err = _create_zfs_remote_replication(request, cd)
                    if err:
                        raise Exception(err)

                elif cd['select_mode'] == 'rsync':
                    ret, err = _create_rsync_remote_replication(request, cd)
                    if err:
                        raise Exception(err)

                return django.http.HttpResponseRedirect('/view_remote_replications?ack=created')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure remote replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring remote replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def _create_zfs_remote_replication(request, cleaned_data):
    """Schedule ZFS remote replication

    - call add_remote_replication() which adds the remote replication
      entry to the remote_replications table, the appropriate zfs 
      mode specific replication table:zfs_replications and adds the
      python script as a crontab entry that runs ZFS replication.
    """
    try:
        if (not request) or (not cleaned_data):
            raise Exception('Insufficient parameters')

        cd = cleaned_data
        source_dataset = cd['source_dataset']
        scheduler = request.POST.get('scheduler')
        schedule = scheduler.split()
        target_ip = cd['target_ip']
        target_pool = cd['target_pool']
        target_user_name = "replicator"
        is_one_shot = False
        description = ''

        if (not target_ip) or (not target_pool) or (not source_dataset):
            raise Exception("Incomplete request.")
        if 'is_one_shot' in cd and cd['is_one_shot'] == True:
            is_one_shot = True
            description = '[One shot]'

        existing_repl, err = remote_replication.get_remote_replications_with(
            'zfs', {'source_dataset': source_dataset, 'target_ip': target_ip, 'target_pool': target_pool})
        if err:
            raise Exception(err)
        if existing_repl:
            raise Exception(
                "A replication schedule already exists with matching entries/options.")

        description = '%s ZFS replication of %s to pool %s on machine %s' % (
            description, source_dataset, target_pool, target_ip)

        # add_remote_replication() will add the remote replication
        # entry to the remote_replications table, the appropriate ZFS
        # mode specific replication table:zfs_replications and add the
        # python script as a crontab entry that runs ZFS replication.
        ids, err = remote_replication.add_remote_replication(
            'zfs', {'source_dataset': source_dataset, 'target_ip': target_ip, 'target_user_name': target_user_name, 'target_pool': target_pool, 'schedule': schedule, 'description': description, 'is_one_shot':is_one_shot})
        if err:
            raise Exception(err)

        # updated cron_task_id becomes available now
        crons, err = scheduler_utils.get_cron_tasks(ids['cron_task_id'])
        if err:
            raise Exception(err)
        description += '\nSchedule: %s' % crons[0]['schedule_description']

        audit.audit("create_remote_replication",
                    description, request)

    except Exception as e:
        return False, 'Failed creating/scheduling ZFS replication: %s' % e
    else:
        return True, None


def _create_rsync_remote_replication(request, cleaned_data):
    """Schedule rsync remote replication

    - call add_remote_replication() which adds the remote replication
      entry to the remote_replications table, the appropriate rsync 
      mode specific replication table:rsync_replications and adds the
      python script as a crontab entry that runs rsync replication.
    """
    try:
        if (not request) or (not cleaned_data):
            raise Exception('Insufficient parameters')

        cd = cleaned_data
        source_path = None
        target_path = None
        target_ip = cd['target_ip']
        target_user_name = "replicator"
        switches_formed = {}
        switches_formed['short'] = ''
        switches_formed['long'] = ''
        switches = {}
        description = ''
        is_between_integralstor = False
        is_one_shot = False

        if 'is_between_integralstor' in cd and cd['is_between_integralstor'] == True:
            is_between_integralstor = True
        if 'is_one_shot' in cd and cd['is_one_shot'] == True:
            is_one_shot = True
            description = '[One shot]'


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
            #target_user_name = None
            # since this replication is local to the box, go in as root
            # instead of going in as 'replicator'. This variable
            # becomes a dummy later anyway for 'local' related checks,
            # so, does not matter.
            target_user_name = "root"

        scheduler = request.POST.get('scheduler')
        schedule = scheduler.split()

        # argument value of switches that can take an argument is a
        # separate input element; not part of switches. So, update
        # switches dictionary to contain the argument value as well.
        if 'switches' in cd and cd['switches']:
            for switch in cd['switches']:
                s = ast.literal_eval(switch)
                for k, v in s.items():
                    if v['is_arg']:
                        v['arg_value'] = cd['%s_arg' % v['id']]
                switches.update(s)
        if switches:
            # pass the switches dictionary to form the switch part of
            # the rsync command as a string. Two strings will be
            # returned as a dictionary: long,short
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

        if rsync_type == 'pull':
            description = '%s rsync replication of %s from %s to %s on local host' % (
                description, source_path, target_ip, target_path)
        elif rsync_type == 'push':
            description = '%s rsync replication of %s from local host to %s on %s' % (
                description, source_path, target_path, target_ip)
        elif rsync_type == 'local':
            description = '%s rsync replication of %s from local host to %s on local host' % (
                description, source_path, target_path)

        # add_remote_replication() will add the remote replication
        # entry to the remote_replications table, the appropriate rsync
        # mode specific replication table:rsync_replications and add the
        # python script as a crontab entry that runs rsync replication.

        ids, err = remote_replication.add_remote_replication('rsync', {'rsync_type': rsync_type, 'short_switches': switches_formed['short'], 'long_switches': switches_formed[
                                                             'long'], 'source_path': source_path, 'target_path': target_path, 'target_ip': target_ip, 'is_one_shot': is_one_shot, 'is_between_integralstor': is_between_integralstor, 'target_user_name': target_user_name, 'description': description, 'schedule': schedule})
        if err:
            raise Exception(err)

        # updated cron_task_id becomes available now
        crons, err = scheduler_utils.get_cron_tasks(ids['cron_task_id'])
        if err:
            raise Exception(err)
        description += '\nSchedule: %s' % crons[0]['schedule_description']

        audit.audit("create_remote_replication",
                    description, request)

    except Exception as e:
        return False, 'Failed creating/scheduling rsync replication: %s' % e
    else:
        return True, None


def update_remote_replication(request):
    """Modifies only the schedule, not any other field

    """
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

            # update the schedule of the cron entry in-place
            is_update, err = remote_replication.update_remote_replication_schedule(
                remote_replication_id, schedule)
            if err:
                raise Exception(err)

            crons, err = scheduler_utils.get_cron_tasks(cron_task_id)
            if err:
                raise Exception(err)
            description += '\nSchedule: %s' % crons[0]['schedule_description']

            audit.audit("modify_remote_replication", description, request)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=updated')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Configure remote replication'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error configuring replication'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_rsync_remote_replication_pause_schedule(request):
    """Modifies only the pause schedule, not any other field

    TODO: shorten this ridiculously large name when cleaning up
    """
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
        if replications[0]['mode'] != 'rsync':
            raise Exception('Unsupported replication mode')

        if request.method == "GET":
            return_dict['replication'] = replications[0]
            return django.shortcuts.render_to_response('update_remote_replication_pause_schedule.html', return_dict, context_instance=django.template.context.RequestContext(request))
        elif request.method == "POST":
            scheduler = None
            schedule = None
            is_disabled = True
            if ('pause_cron_task_id' and 'is_disabled') not in request.POST:
                raise Exception("Incomplete request.")
            is_disabled = request.POST.get('is_disabled')
            if str(is_disabled) == 'False':
                if ('scheduler') not in request.POST:
                    raise Exception("Incomplete request.")
                scheduler = request.POST.get('scheduler')
                schedule = scheduler.split()
            pause_cron_task_id = request.POST.get('pause_cron_task_id')
            description = ''
            description += replications[0]['description']

            # update the schedule of the cron entry in-place
            pause_cron_task_id, err = remote_replication.update_rsync_remote_replication_pause_schedule(
                remote_replication_id, schedule)
            if err:
                raise Exception(err)

            audit_tag = ''
            if schedule:
                crons, err = scheduler_utils.get_cron_tasks(pause_cron_task_id)
                if err:
                    raise Exception(err)
                if 'schedule_description' in crons[0] and crons[0]['schedule_description']:
                    description += '\nSchedule: %s' % crons[0]['schedule_description']
                audit_tag = 'update_rsync_remote_replication_pause_schedule'
            else:
                audit_tag = 'remove_rsync_remote_replication_pause_schedule'

            audit.audit(audit_tag, description, request)
            return django.http.HttpResponseRedirect('/view_remote_replications?ack=pause_schedule_updated')
    except Exception as e:
        return_dict['base_template'] = "snapshot_replication_base.html"
        return_dict["page_title"] = 'Update rsync remote replication pause schedule'
        return_dict['tab'] = 'view_remote_replications_tab'
        return_dict["error"] = 'Error updating rsync remote replication pause schedule'
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
            ret, err = remote_replication.delete_remote_replication(
                remote_replication_id)
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
