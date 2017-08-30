import django
import django.template

from integralstor_utils import config, disks, command, zfs, django_utils
from integralstor import system_info, manifest_status, audit, tasks_utils


def view_disks(request):
    return_dict = {}
    type = 'data'
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "blink":
                return_dict['ack_message'] = "Disk identification LED successfully activated"
            elif request.GET["ack"] == "unblink":
                return_dict['ack_message'] = "Disk identification LED successfully de-activated"
        ret, err = django_utils.get_request_parameter_values(
            request, ['type'])
        if err:
            raise Exception(err)
        if ('type' not in ret) or ret['type'] not in ['data', 'os']:
            type = 'data'
        else:
            type = ret['type']
        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
        if not si:
            raise Exception('Error loading system configuration')
        hw_platform, err = config.get_hardware_platform()
        if hw_platform:
            return_dict['hw_platform'] = hw_platform
            if hw_platform == 'dell':
                from integralstor_utils.platforms import dell
                idrac_url, err = dell.get_idrac_addr()
                if idrac_url:
                    return_dict['idrac_url'] = idrac_url
        if type == 'os':
            os_disk_stats, err = disks.get_os_partition_stats()
            if err:
                raise Exception(err)
            return_dict['os_disk_stats'] = os_disk_stats
        return_dict['node'] = si
        return_dict['system_info'] = si
        return_dict["disk_status"] = si['disks']
        return_dict['node_name'] = si['fqdn']
        if type == 'os':
            return django.shortcuts.render_to_response('view_os_disks.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            return django.shortcuts.render_to_response('view_data_disks.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Disks'
        return_dict['tab'] = 'view_%s_disks_tab'%type
        return_dict["error"] = 'Error loading disk information'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def identify_disk(request):
    return_dict = {}
    try:
        action = None
        channel = None
        enclosure_id = None
        controller_number = None
        target_id = None
        ret, err = django_utils.get_request_parameter_values(
            request, ['hw_platform', 'action', 'controller_number', 'channel', 'enclosure_id', 'target_id', 'disk_type'])
        if err:
            raise Exception(err)

        if 'hw_platform' not in ret or ret['hw_platform'].lower() != 'dell':
            raise Exception(
                'Unknown hardware platform so cannot toggle identification LED')
        if 'action' not in ret or ret['action'] not in ['blink', 'unblink']:
            raise Exception(
                'Unknown action specified so cannot toggle identification LED')
        if ('channel' and 'enclosure_id' and 'target_id' and 'controller_number') not in ret:
            raise Exception(
                'Invalid request, please use the menus.')
        action = ret['action']
        if 'disk_type' in ret:
            disk_type = ret['disk_type']
        else:
            disk_type = 'data'
        channel = ret['channel']
        enclosure_id = ret['enclosure_id']
        target_id = ret['target_id']
        controller_number = ret['controller_number']
        from integralstor_utils.platforms import dell
        result, err = dell.blink_unblink_disk(
            action, controller_number, channel, enclosure_id, target_id)
        if not result:
            raise Exception(err)
        return django.http.HttpResponseRedirect('/view_disks?ack=%s&type=%s' %(action, disk_type))

    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Disks'
        return_dict['tab'] = 'view_data_disks_tab'
        return_dict["error"] = 'Error toggling disk identification'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def replace_disk(request):

    return_dict = {}
    try:
        form = None

        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
        if not si:
            raise Exception('Error loading system config')

        return_dict['system_config_list'] = si

        template = 'logged_in_error.html'
        use_salt, err = config.use_salt()
        if err:
            raise Exception(err)

        if request.method == "GET":
            raise Exception("Incorrect access method. Please use the menus")
        else:
            if 'node' in request.POST:
                node = request.POST["node"]
            else:
                node = si['fqdn']
            serial_number = request.POST["serial_number"]

            if "conf" in request.POST:
                if "node" not in request.POST or "serial_number" not in request.POST:
                    raise Exception(
                        "Incorrect access method. Please use the menus")
                elif request.POST["node"] != si['fqdn']:
                    raise Exception("Unknown node. Please use the menus")
                elif "step" not in request.POST:
                    raise Exception("Incomplete request. Please use the menus")
                elif request.POST["step"] not in ["replace_method", "select_replacement_disk", "offline_disk", "scan_for_new_disk", "online_new_disk"]:
                    raise Exception("Incomplete request. Please use the menus")
                else:
                    step = request.POST["step"]

                    # Which step of the replace disk are we in?

                    if step == "offline_disk":

                        # get the pool corresponding to the disk
                        # zpool offline pool disk
                        # send a screen asking them to replace the disk

                        if 'replacement_method' not in request.POST or request.POST['replacement_method'] not in ['use_existing_disk', 'swap_out_disk']:
                            raise Exception('Invalid request')
                        return_dict['replacement_method'] = request.POST['replacement_method']
                        if request.POST['replacement_method'] == 'use_existing_disk':
                            # Then we should have landed here after already
                            # selecting the new disk so get and record the new
                            # disk details
                            if 'new_serial_number' not in request.POST:
                                raise Exception(
                                    'Incomplete request. Please try again')
                            new_serial_number = request.POST['new_serial_number']
                            all_disks, err = disks.get_disk_info_status_all(rescan=True)
                            if new_serial_number not in all_disks:
                                raise Exception('Invalid disk selection')
                            # print new_serial_number
                            # print all_disks[new_serial_number]['id']
                            return_dict['new_serial_number'] = new_serial_number
                            return_dict['new_id'] = all_disks[new_serial_number]['id']

                        pool = None
                        if serial_number in si["disks"]:
                            disk = si["disks"][serial_number]
                            if "pool" in disk:
                                pool = disk["pool"]
                            disk_id = disk["id"]
                        if not pool:
                            raise Exception(
                                "Could not find the storage pool on that disk. Please use the menus")
                        else:
                            cmd_to_run = 'zpool offline %s %s' % (
                                pool, disk_id)
                            # print 'Running %s'%cmd_to_run
                            #assert False
                            ret, err = command.get_command_output(cmd_to_run)
                            if err:
                                raise Exception(err)
                            audit_str = "Replace disk - Disk with serial number %s brought offline" % serial_number
                            audit.audit("replace_disk_offline_disk",
                                        audit_str, request)
                            return_dict["serial_number"] = serial_number
                            return_dict["node"] = node
                            return_dict["pool"] = pool
                            return_dict["old_id"] = disk_id
                            template = "replace_disk_offlined_conf.html"

                    elif step == "replace_method":
                        return_dict["node"] = node
                        return_dict["serial_number"] = serial_number
                        template = "replace_disk_method.html"

                    elif step == "select_replacement_disk":
                        if 'replacement_method' not in request.POST or request.POST['replacement_method'] not in ['use_existing_disk', 'swap_out_disk']:
                            raise Exception('Invalid request')
                        return_dict['replacement_method'] = request.POST['replacement_method']
                        return_dict["node"] = node
                        return_dict["serial_number"] = serial_number
                        free_disks, err = zfs.get_free_disks()
                        if err:
                            raise Exception(err)
                        if not free_disks:
                            raise Exception(
                                'There are no unused disks presently')
                        return_dict['free_disks'] = free_disks
                        template = "replace_disk_choose_disk.html"

                    elif step == "scan_for_new_disk":

                        # they have replaced the disk so scan for the new disk
                        # and prompt for a confirmation of the new disk serial
                        # number

                        pool = request.POST["pool"]
                        old_id = request.POST["old_id"]
                        return_dict["node"] = node
                        return_dict["serial_number"] = serial_number
                        return_dict["pool"] = pool
                        return_dict["old_id"] = old_id
                        old_disks = si["disks"].keys()
                        result = False
                        rc, err = manifest_status.get_disk_info_and_status()
                        if err:
                            raise Exception(err)
                        if rc:
                            result = True
                            new_disks = rc
                        if result:
                            # print '1'
                            if new_disks:
                                # print new_disks.keys()
                                # print old_disks
                                for disk in new_disks.keys():
                                    # print disk
                                    if disk not in old_disks:
                                        # print 'new disk : ', disk
                                        return_dict["inserted_disk_serial_number"] = disk
                                        return_dict["new_id"] = new_disks[disk]["id"]
                                        break
                                if "inserted_disk_serial_number" not in return_dict:
                                    raise Exception(
                                        "Could not detect any new disk. Please check the new disk is inserted and give the system a few seconds to detect the drive and refresh the page to try again.")
                                else:
                                    template = "replace_disk_confirm_new_disk.html"
                    elif step == "online_new_disk":

                        pool = request.POST["pool"]
                        old_id = request.POST["old_id"]
                        new_id = request.POST["new_id"]
                        new_serial_number = request.POST["new_serial_number"]
                        common_python_scripts_path, err = config.get_common_python_scripts_path()
                        if err:
                            raise Exception(err)
                        cmd_list = []
                        cmd_list.append(
                            {'Replace old disk': 'zpool replace -f %s %s %s' % (pool, old_id, new_id)})
                        cmd_list.append(
                            {'Online the new disk': 'zpool online -e %s %s' % (pool, new_id)})
                        cmd_list.append(
                            {'Regenerate the system configuration': '%s/generate_manifest.py' % common_python_scripts_path})
                        ret, err = tasks_utils.create_task(
                            'Disk replacement', cmd_list, task_type_id=1, attempts=1)
                        if err:
                            raise Exception(err)
                        if not ret:
                            raise Exception(
                                'Error scheduling disk replacement tasks')
                        audit_str = "Replace disk - Scheduled a task for replacing the old disk with serial number %s with the new disk with serial number %s" % (
                            serial_number, new_serial_number)
                        audit.audit("replace_disk_replaced_disk",
                                    audit_str, request)
                        return_dict["node"] = node
                        return_dict["old_serial_number"] = serial_number
                        return_dict["new_serial_number"] = new_serial_number
                        template = "replace_disk_success.html"
                    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

            else:
                if "serial_number" not in request.POST:
                    raise Exception(
                        "Incorrect access method. Please use the menus")
                else:
                    if 'node' in request.POST:
                        return_dict["node"] = request.POST["node"]
                    else:
                        node = si['fqdn']
                    return_dict["serial_number"] = request.POST["serial_number"]
                    template = "replace_disk_conf.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Replace a disk in a ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error replacing a disk in a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
