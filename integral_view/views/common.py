import time
import stat
import datetime
from datetime import timedelta

import django.template
import django
from django.contrib.auth.decorators import login_required
import django.http


from integralstor import system_info, iscsi_stgt, nfs, audit, datetime_utils, cifs, django_utils, stats, services_management, zfs, command, config


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

        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
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
            return django.http.HttpResponseRedirect("/view_system_info/")
    except Exception, e:
        return_dict['base_template'] = "system_base.html"
        return_dict["page_title"] = 'Reload system configuration'
        return_dict['tab'] = 'system_info_tab'
        return_dict["error"] = 'Error reloading system configuration'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


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


@login_required
def view_backup(request):
    return_dict = {}
    try:
        host = request.META['HTTP_HOST']
        if ':' in host:
            col_pos = host.find(':')
            if col_pos:
                host = host[:col_pos]
        url = '%s:55414' % host
        return_dict['url'] = url
        return django.shortcuts.render_to_response("view_backup.html", return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "backup_base.html"
        return_dict["page_title"] = 'Data backup'
        return_dict['tab'] = 'view_backup_tab'
        return_dict["error"] = 'Error loading backup URL'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def view_dashboard(request, page):
    return_dict = {}
    try:
        return_dict["page_title"] = 'Overall system health'
        return_dict['tab'] = 'system_health_tab'
        return_dict["error"] = 'Error loading system health data'

        if request.method != 'GET':
            raise Exception('Invalid access method. Please use the menus')

        si, err = system_info.load_system_config()
        if err:
            raise Exception(err)
        if not si:
            raise Exception('Error loading system configuration')

        #node_name = si.keys()[0]
        #node = si[node_name]
        return_dict['node'] = si
        # print node.keys()

        # By default show error page
        template = "logged_in_error.html"

        # Chart specific declarations
        # will return 02, instead of 2.
        todays_date = (datetime.date.today()).strftime('%02d')
        start_hour = '%02d' % (datetime.datetime.today().hour - 3)
        end_hour = '%02d' % (datetime.datetime.today().hour)
        minute = '%02d' % (datetime.datetime.today().minute)
        start = str(start_hour) + ":" + str(minute) + str(":10")
        end = str(end_hour) + ":" + str(minute) + str(":40")

        value_list = []
        time_list = []

        num_bad_disks = 0
        num_hw_raid_bad_disks = 0
        num_hw_raid_ctrl_disks = 0
        num_smart_ctrl_disks = 0
        num_disks = len(si['disks'])
        disks_ok = True
        for sn, disk in si['disks'].items():
            if 'status' in disk:
                if 'hw_raid' in disk:
                    if not disk['hw_raid']:
                        num_smart_ctrl_disks += 1
                        if (disk['status'] is not None and disk['status'].upper() not in ['PASSED', 'OK']):
                            num_bad_disks += 1
                            disks_ok = False
                    else:
                        num_hw_raid_ctrl_disks += 1
                        if (disk['status'] is not None and disk['status'].upper() != 'OK'):
                            num_hw_raid_bad_disks += 1
                            disks_ok = False
                else:
                    # Assume its a non raid disk
                    num_smart_ctrl_disks += 1
                    if (disk['status'] is not None and disk['status'].upper() not in ['PASSED', 'OK']):
                        num_bad_disks += 1
                        disks_ok = False

        return_dict['num_disks'] = num_disks
        return_dict['num_bad_disks'] = num_bad_disks
        return_dict['disks_ok'] = disks_ok
        return_dict['num_hw_raid_bad_disks'] = num_hw_raid_bad_disks
        return_dict['num_hw_raid_ctrl_disks'] = num_hw_raid_ctrl_disks
        return_dict['num_smart_ctrl_disks'] = num_smart_ctrl_disks

        if 'ipmi_status' in si:
            num_sensors = len(si['ipmi_status'])
            num_bad_sensors = 0
            ipmi_ok = True
            for sensor in si['ipmi_status']:
                if sensor['status'] in ['ok', 'nr', 'na']:
                    continue
                else:
                    num_bad_sensors += 1
                    ipmi_ok = False
            return_dict['num_sensors'] = num_sensors
            return_dict['num_bad_sensors'] = num_bad_sensors
            return_dict['ipmi_ok'] = ipmi_ok

        services_dict, err = services_management.get_sysd_services_status()
        if err:
            raise Exception(err)

        num_services = len(services_dict)
        num_failed_services = 0
        num_active_services = 0
        num_inactive_services = 0
        services_ok = True

        if services_dict:
            for service, service_d in services_dict.items():
                if service_d["info"]["status"]["status_str"] == "Active":
                    num_active_services += 1
                elif service_d["info"]["status"]["status_str"] == "Inactive":
                    num_inactive_services += 1
                elif service_d["info"]["status"]["status_str"] == "Failed":
                    num_failed_services += 1
                    services_ok = False
                elif service_d["info"]["status"]["status_str"] == "Unknown State":
                    num_failed_services += 1
                    services_ok = False
            return_dict['num_services'] = num_services
            return_dict['num_active_services'] = num_active_services
            return_dict['num_inactive_services'] = num_inactive_services
            return_dict['num_failed_services'] = num_failed_services
            return_dict['services_ok'] = services_ok
        else:
            raise Exception('Error retrieving services status')

        pools, err = zfs.get_pools()
        if err:
            raise Exception(err)

        num_pools = len(pools)
        num_bad_pools = 0
        num_degraded_pools = 0
        num_high_usage_pools = 0
        for pool in pools:
            if pool['usage']['used_percent'] > 75:
                num_high_usage_pools += 1
            if pool['config']['pool']['root']['status']['state'] == 'ONLINE':
                pass
            elif pool['config']['pool']['root']['status']['state'] == 'DEGRADED':
                num_degraded_pools += 1
            else:
                num_bad_pools += 1
        return_dict['num_pools'] = num_pools
        return_dict['num_bad_pools'] = num_bad_pools
        return_dict['num_degraded_pools'] = num_degraded_pools
        return_dict['num_high_usage_pools'] = num_high_usage_pools

        load_avg_ok = True
        if (si["load_avg"]["5_min"] > si["load_avg"]["cpu_cores"]) or (si["load_avg"]["15_min"] > si["load_avg"]["cpu_cores"]):
            load_avg_ok = False
        return_dict['load_avg_ok'] = load_avg_ok

        shares_list, err = cifs.get_shares_list()
        if err:
            raise Exception(err)
        return_dict['num_cifs_shares'] = len(shares_list)

        exports_list, err = nfs.load_exports_list()
        if err:
            raise Exception(err)
        return_dict['num_nfs_exports'] = len(exports_list)

        target_list, err = iscsi_stgt.get_targets()
        if err:
            raise Exception(err)
        return_dict['num_iscsi_targets'] = len(target_list)

        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_str = '%s hours' % (
                ':'.join(str(timedelta(seconds=uptime_seconds)).split(':')[:2]))
            return_dict['uptime_str'] = uptime_str

        # CPU status
        if page == "cpu":
            return_dict["page_title"] = 'CPU statistics'
            return_dict['tab'] = 'cpu_tab'
            return_dict["error"] = 'Error loading CPU statistics'
            cpu, err = stats.get_system_stats(todays_date, start, end, "cpu")
            if err:
                raise Exception(err)
            value_dict = {}
            if cpu:
                for key in cpu.keys():
                    value_list = []
                    time_list = []
                    if key == "date":
                        pass
                    else:
                        if cpu[key]:
                            for a in cpu[key]:
                                time_list.append(a[0])
                                value_list.append(a[1])
                        value_dict[key] = value_list
            return_dict["data_dict"] = value_dict
            queue, err = stats.get_system_stats(
                todays_date, start, end, "queue")
            if err:
                raise Exception(err)
            value_dict = {}
            if queue:
                for key in queue.keys():
                    value_list = []
                    time_list = []
                    if key == "date":
                        pass
                    else:
                        for a in queue[key]:
                            time_list.append(a[0])
                            value_list.append(a[1])
                        value_dict[key] = value_list
            return_dict["data_dict_queue"] = value_dict
            return_dict['node'] = si
            d = {}
            template = "view_cpu_stats.html"
        elif page == "sys_health":
            return_dict["page_title"] = 'Overall system health'
            return_dict['tab'] = 'system_health_tab'
            return_dict["error"] = 'Error loading system health data'
            template = "view_dashboard.html"
            hw_platform, err = config.get_hardware_platform()
            if hw_platform:
                return_dict['hw_platform'] = hw_platform
                if hw_platform == 'dell':
                    from integralstor.platforms import dell
                    idrac_url, err = dell.get_idrac_addr()
                    if idrac_url:
                        return_dict['idrac_url'] = idrac_url
        # Memory
        elif page == "memory":
            return_dict["page_title"] = 'Memory statistics'
            return_dict['tab'] = 'memory_tab'
            return_dict["error"] = 'Error loading memory statistics'
            mem, err = stats.get_system_stats(
                todays_date, start, end, "memory")
            if err:
                raise Exception(err)
            if mem:
                for a in mem["memused"]:
                    time_list.append(a[0])
                    value_list.append((a[1] / (1024 * 1024)))
            return_dict['memory_status'] = si['memory']
            template = "view_memory_stats.html"
        # Network
        elif page == "network":
            return_dict["page_title"] = 'Network statistics'
            return_dict['tab'] = 'network_tab'
            return_dict["error"] = 'Error loading Network statistics'
            network, err = stats.get_system_stats(
                todays_date, start, end, "network")
            if err:
                raise Exception(err)
            value_dict = {}
            if network:
                for key in network.keys():
                    value_list = []
                    time_list = []
                    if key == "date" or key == "lo":
                        pass
                    else:
                        for a in network[key]["ifutil-percent"]:
                            time_list.append(a[0])
                            value_list.append(a[1])
                        value_dict[key] = value_list

            return_dict["data_dict"] = value_dict
            return_dict["network_status"] = si['interfaces']
            template = "view_network_stats.html"
        return_dict["labels"] = time_list
        return_dict["data"] = value_list
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "dashboard_base.html"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


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


'''
@login_required    
def show(request, page, info = None):

  return_dict = {}
  try:

    si,err = system_info.load_system_config()
    if err:
      raise Exception(err)

    #assert False
    return_dict['system_info'] = si

    #By default show error page
    template = "logged_in_error.html"

    if page == "dir_contents":
      #CHANGE THIS TO SHOW LOCAL DIR LISTINGS!!
      return django.http.HttpResponse(dir_list,content_type=='application/json')

    elif page == "integral_view_log_level":

      template = "view_integral_view_log_level.html"
      try:
        log_level = iv_logging.get_log_level_str()
      except Exception, e:
        return_dict["error"] = str(e)
      else:
        return_dict["log_level_str"] = log_level

      ret, err = django_utils.get_request_parameter_values(request,['saved'])
      if err:
        raise Exception(err)
      if 'saved' not in ret:
        raise Exception("Request not found, please use the menus.")
      return_dict["saved"] = ret['saved']

    return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
'''


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
