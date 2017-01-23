import django, django.template

import integralstor_common
import integralstor_unicell
from integralstor_common import networking, audit, command, common
from integralstor_common import route_utils as route
from django.contrib.auth.decorators import login_required

import socket

import integral_view
from integral_view.forms import networking_forms
  
def view_interfaces(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    nics, err = networking.get_interfaces()
    if err:
      raise Exception(err)
    bonds, err = networking.get_bonding_info_all()
    if err:
      raise Exception(err)
  
    if "ack" in request.GET:
      if request.GET["ack"] == "saved":
        return_dict['ack_message'] = "Network interface information successfully updated"
      if request.GET["ack"] == "removed_bond":
        return_dict['ack_message'] = "Network bond successfully removed"
      if request.GET["ack"] == "removed_vlan":
        return_dict['ack_message'] = "VLAN successfully removed"
      if request.GET["ack"] == "created_vlan":
        return_dict['ack_message'] = "VLAN successfully created"
      if request.GET["ack"] == "state_down":
        return_dict['ack_message'] = "Network interface successfully disabled. The state change may take a couple of seconds to reflect on this page so please refresh it to check the updated status."
      if request.GET["ack"] == "state_up":
        return_dict['ack_message'] = "Network interface successfully enabled. The state change may take a couple of seconds to reflect on this page so please refresh it to check the updated status."
      if request.GET["ack"] == "created_bond":
        return_dict['ack_message'] = "Network bond successfully created. Please edit the address information for the bond in order to use it."
    return_dict["nics"] = nics
    return_dict["bonds"] = bonds
    template = "view_interfaces.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'View network interfaces'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error loading interfaces'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_nic(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      raise Exception("Error loading network interface information : No interface name specified.")
    
    name = request.REQUEST['name']
    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception(err)
    elif name not in interfaces:
      raise Exception("Specified interface not found")

    if interfaces[name]['vlan']:
      if '.' not in name:
        raise Exception('Invalid VLAN name : %s'%name)
      comps = name.split('.')
      if len(comps) != 2:
        raise Exception('Invalid VLAN name : %s'%name)
      return_dict['parent_nic'] = comps[0]

    return_dict['nic'] = interfaces[name]
    if interfaces[name]['vlan_ids']:
      return_dict['vlans'] = []
      for vlan_id in interfaces[name]['vlan_ids']:
        if '%s.%d'%(name, vlan_id) in interfaces:
          return_dict['vlans'].append({'name':'%s.%d'%(name, vlan_id), 'vlan_id':vlan_id, 'info':interfaces['%s.%d'%(name, vlan_id)]})
    return_dict['interfaces'] = interfaces
    return_dict['name'] = name
      
    template = "view_nic.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'View network interface details'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error loading interface details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def set_interface_state(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No interface name specified. Please use the menus")

    if 'state' not in request.REQUEST:
      raise Exception("No state specified. Please use the menus")

    name = request.REQUEST["name"]
    return_dict["name"] = name
    state = request.REQUEST["state"]
    return_dict["state"] = state

    if request.method == "GET" and state == 'down':
      #Return the conf page
      return django.shortcuts.render_to_response("set_interface_state_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = networking.set_interface_state(name, state)
      if not result:
        if err:
          raise Exception(err)
        else:
          raise Exception("Error setting interface state")
 
      audit_str = "Set the state of network interface %s to %s"%(name, state)
      audit.audit("set_interface_state", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_interfaces?ack=state_%s'%state)
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Set interface state'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error setting interface state'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_bond(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    if 'name' not in request.REQUEST:
      raise Exception("No bond name specified.")
    
    name = request.REQUEST['name']

    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception(err)
    elif name not in interfaces:
      raise Exception("Specified interface not found")

    bond, err = networking.get_bonding_info(name)
    if err:
      raise Exception(err)
    if not bond:
      raise Exception("Specified bond not found")

    return_dict['nic'] = interfaces[name]
    return_dict['bond'] = bond
    return_dict['name'] = name
      
    template = "view_bond.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'View network bond details'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error loading network bond details'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_interface_address(request):
  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("Interface name not specified. Please use the menus.")

    name = request.REQUEST["name"]
    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception(err)
    elif not interfaces or name not in interfaces:
      raise Exception("Specified interface not found")
    return_dict['nic'] = interfaces[name]

    if request.method == "GET":

      initial = {}
      initial['name'] = name
      initial['mtu'] = name
      if 'mtu' in interfaces[name] and interfaces[name]['mtu']:
      	initial['mtu'] = interfaces[name]['mtu']
      if 'bootproto' in interfaces[name] and interfaces[name]['bootproto'] == 'dhcp':
        initial['addr_type'] = 'dhcp'
      else:
        initial['addr_type'] = 'static'
        if 'addresses' in interfaces[name] and 'AF_INET' in interfaces[name]['addresses'] and interfaces[name]['addresses']['AF_INET']:
          initial['ip'] = interfaces[name]['addresses']['AF_INET'][0]['addr']
          initial['netmask'] = interfaces[name]['addresses']['AF_INET'][0]['netmask']
      #print interfaces[name]
      if 'gateways' in interfaces[name] and interfaces[name]['gateways']:
        if interfaces[name]['gateways'][0][2]:
          initial['default_gateway'] = interfaces[name]['gateways'][0][0]
      #print initial

      form = networking_forms.NICForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_interface_address.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.NICForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_interface_address.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result_str = ""
      success = False
      result, err = networking.set_interface_ip_info(cd['name'], cd)
      if err:
        raise Exception(err)
      result, err = networking.restart_networking()
      if err:
        raise Exception(err)
      ip, err = networking.get_ip_info(common.convert_unicode_to_string(cd['name']))
      if err:
        raise Exception(err)
      audit_str = 'Changed the address of %s. New values are IP : %s, netmask: %s'%(cd['name'], ip['ipaddr'], ip['netmask']) 
      if 'default_gateway' in ip:
        audit_str += ', default gateway : %s'%ip['default_gateway']
      audit.audit("edit_interface_address", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_nic?name=%s&result=addr_changed'%(name))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Modify network interface addressing'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error modifying network interface addressing'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_vlan(request):
  return_dict = {}
  try:

    if 'nic' not in request.REQUEST:
      raise Exception('No base network interface specified. Please use the menus.')

    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception(err)

    if not interfaces:
      raise Exception("Error loading network interface information : No interfaces found")

    return_dict['interfaces'] = interfaces
    if_list = []
    existing_vlans = []
    for if_name, iface in interfaces.items():
      if '.' in if_name:
        comps = if_name.split('.')
        if len(comps) != 2:
          raise Exception('Invalid VLAN specification found : %s'%if_name)
        if int(comps[1]) not in existing_vlans:
          existing_vlans.append(int(comps[1]))
    if request.method == "GET":
      form = networking_forms.CreateVLANForm(existing_vlans = existing_vlans, initial = {'base_interface': request.REQUEST['nic']})
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_vlan.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.CreateVLANForm(request.POST, existing_vlans = existing_vlans)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_vlan.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      #print cd
      result, err = networking.create_vlan(cd['base_interface'], cd['vlan_id'])
      if not result:
        if err:
          raise Exception(err)
        else:
          raise Exception('VLAN creation failed!')

      result, err = networking.restart_networking()
      if err:
        raise Exception(err)
 
      audit_str = "Created a network VLAN with id  %d on the base interface %s"%(cd['vlan_id'], cd['base_interface'])
      audit.audit("create_vlan", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_interfaces?ack=created_vlan')
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Create a network VLAN'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error creating a network VLAN'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_vlan(request):
  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No VLAN name specified. Please use the menus")

    name = request.REQUEST["name"]
    return_dict["name"] = name

    if request.method == "GET" :
      #Return the conf page
      return django.shortcuts.render_to_response("remove_vlan_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = networking.remove_vlan(name)
      if not result:
        if not err:
          raise Exception("Error removing VLAN")
        else:
          raise Exception(err)

      result, err = networking.restart_networking()
      if err:
        raise Exception(err)
 
      audit_str = "Removed VLAN %s"%(name)
      audit.audit("remove_vlan", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_interfaces?ack=removed_vlan')
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Remove a VLAN'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error removing a VLAN'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_bond(request):
  return_dict = {}
  try:

    interfaces, err = networking.get_interfaces()
    if err:
      raise Exception(err)
    if not interfaces:
      raise Exception("Error loading network interface information : No interfaces found")

    bonds, err = networking.get_bonding_info_all()
    if err:
      raise Exception(err)

    return_dict['interfaces'] = interfaces
    if_list = []
    existing_bonds = []
    for if_name, iface in interfaces.items():
      if 'bonding_master' in iface and iface['bonding_master']:
        existing_bonds.append(if_name)
        continue
      if 'slave_to' in iface and iface['slave_to']:
        continue
      #if 'eth' not in if_name:
      #  continue
      if_list.append(if_name)
    if request.method == "GET":
      form = networking_forms.CreateBondForm(interfaces = if_list, existing_bonds = existing_bonds)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("create_bond.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.CreateBondForm(request.POST, interfaces = if_list, existing_bonds = existing_bonds)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("create_bond.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      print cd
      result, err = networking.create_bond(cd['name'], cd['slaves'], int(cd['mode']))
      if not result:
        if err:
          raise Exception(err)
        else:
          raise Exception('Bond creation failed!')
      python_scripts_path, err = common.get_python_scripts_path()
      if err:
        raise Exception(err)
      common_python_scripts_path, err = common.get_common_python_scripts_path()
      if err:
        raise Exception(err)
      status_path, err = common.get_system_status_path()
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_manifest.py %s"%(common_python_scripts_path, status_path))
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_status.py %s"%(common_python_scripts_path, status_path))
      if err:
        raise Exception(err)

      audit_str = "Created a network bond named %s with slaves %s"%(cd['name'], ','.join(cd['slaves']))
      audit.audit("create_bond", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_interfaces?ack=created_bond')
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Create a network interface bond'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error creating a network interface bond'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def remove_bond(request):

  return_dict = {}
  try:
    if 'name' not in request.REQUEST:
      raise Exception("No bond name specified. Please use the menus")

    name = request.REQUEST["name"]
    return_dict["name"] = name

    if request.method == "GET" :
      #Return the conf page
      return django.shortcuts.render_to_response("remove_bond_conf.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      result, err = networking.remove_bond(name)
      if not result:
        if not err:
          raise Exception("Error removing bond")
        else:
          raise Exception(err)

      python_scripts_path, err = common.get_python_scripts_path()
      if err:
        raise Exception(err)
      common_python_scripts_path, err = common.get_common_python_scripts_path()
      if err:
        raise Exception(err)
      status_path, err = common.get_system_status_path()
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_manifest.py %s"%(common_python_scripts_path, status_path))
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_status.py %s"%(common_python_scripts_path, status_path))
      if err:
        raise Exception(err)

      audit_str = "Removed network bond %s"%(name)
      audit.audit("remove_bond", audit_str, request.META)
      return django.http.HttpResponseRedirect('/view_interfaces?ack=removed_bond')
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Remove a network interface bond'
    return_dict['tab'] = 'view_interfaces_tab'
    return_dict["error"] = 'Error removing a network interface bond'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_hostname(request):
  return_dict = {}
  try:
    template = 'logged_in_error.html'
    hostname, err = networking.get_hostname()
    if err:
      raise Exception(err)
    domain_name,err = networking.get_domain_name()
    if err:
      raise Exception(err)
  
    if not "error" in return_dict:
      if "ack" in request.GET:
        if request.GET["ack"] == "saved":
          return_dict['ack_message'] = "Hostname information successfully updated"
      return_dict['domain_name'] = domain_name
      return_dict['hostname'] = hostname
      template = "view_hostname.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'View system hostname'
    return_dict['tab'] = 'view_hostname_tab'
    return_dict["error"] = 'Error loading system hostname'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def edit_hostname(request):
  return_dict = {}
  try:

    hostname = socket.gethostname()
    if request.method == "GET":
      hostname, err = networking.get_hostname()
      if err:
        raise Exception(err)
      domain_name,err = networking.get_domain_name()
      if err:
        raise Exception(err)

      initial = {}
      initial['hostname'] = hostname
      initial['domain_name'] = domain_name

      form = networking_forms.EditHostnameForm(initial=initial)
      return_dict['form'] = form
      return django.shortcuts.render_to_response("edit_hostname.html", return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      form = networking_forms.EditHostnameForm(request.POST)
      return_dict['form'] = form
      if not form.is_valid():
        return django.shortcuts.render_to_response("edit_hostname.html", return_dict, context_instance = django.template.context.RequestContext(request))
      cd = form.cleaned_data
      result_str = ""
      domain_name = None
      if 'domain_name' in cd:
        domain_name = cd['domain_name']
      result, err = networking.set_hostname(cd['hostname'], domain_name)
      if not result:
        if err:
          raise Exception(err)
        else:
          raise Exception('Error setting hostname')
      result, err = networking.set_domain_name(domain_name)
      if not result:
        if err:
          raise Exception(err)
        else:
          raise Exception('Error setting domain name')
      python_scripts_path, err = common.get_python_scripts_path()
      if err:
        raise Exception(err)
      common_python_scripts_path, err = common.get_common_python_scripts_path()
      if err:
        raise Exception(err)
      ss_path, err = common.get_system_status_path()
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_manifest.py %s"%(common_python_scripts_path, ss_path))
      if err:
        raise Exception(err)

      ret, err = command.get_command_output("python %s/generate_status.py %s"%(common_python_scripts_path, ss_path))

      audit_str = "Hostname set to %s."%cd['hostname']
      if 'domain_name' in cd:
        audit_str += 'Domain name set to %s'%cd['domain_name']
      ret, err = audit.audit("edit_hostname", audit_str, request.META)
      if err:
        raise Exception(err)
              
      return django.http.HttpResponseRedirect('/view_hostname?result=saved')
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Modify system hostname'
    return_dict['tab'] = 'view_hostname_tab'
    return_dict["error"] = 'Error modifying system hostname'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_dns_nameservers(request):
  return_dict = {}
  try:
    ns_list, err = networking.get_name_servers()
    if err:
      raise Exception(err)
  
    if "ack" in request.GET:
      if request.GET["ack"] == "saved":
        return_dict['ack_message'] = "Name servers successfully updated"
    return_dict['name_servers'] = ns_list
    template = "view_dns_nameservers.html"
    return django.shortcuts.render_to_response(template, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'View DNS servers'
    return_dict['tab'] = 'view_dns_nameservers_tab'
    return_dict["error"] = 'Error loading DNS servers'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


@login_required
def edit_dns_nameservers(request):

  return_dict = {}
  try:
    ns_list, err = networking.get_name_servers()
    if err:
      raise Exception(err)
    if request.method=="GET":
      if not ns_list:
        form = networking_forms.DNSNameServersForm()
      else:
        form = networking_forms.DNSNameServersForm(initial={'nameservers': ','.join(ns_list)})
      url = "edit_dns_nameservers.html"
    else:
      form = networking_forms.DNSNameServersForm(request.POST)
      if form.is_valid():
        cd = form.cleaned_data
        nameservers = cd["nameservers"]
        if ',' in nameservers:
          slist = nameservers.split(',')
        else:
          slist = nameservers.split(' ')
        res, err = networking.set_name_servers(slist)
        if not res:
          if err:
            raise Exception(err)
          else:
            raise Exception('Error updating nameservers')
        audit_str = "Updated the DNS nameserver list to %s"%nameservers
        audit.audit("set_dns_nameservers", audit_str, request.META)
        return django.http.HttpResponseRedirect('/view_dns_nameservers?ack=saved')
      else:
        #invalid form
        url = "edit_dns_nameservers.html"
    return_dict["form"] = form
    return django.shortcuts.render_to_response(url, return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "networking_base.html"
    return_dict["page_title"] = 'Modify DNS servers'
    return_dict['tab'] = 'view_dns_nameservers_tab'
    return_dict["error"] = 'Error modifying DNS servers'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_route(request):
  return_dict = {}
  if request.method == 'GET':
    form = networking_forms.CreateRouteForm()
  else:
    form = networking_forms.CreateRouteForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      status,err = route.add_route(cd['ip'],cd['gateway'],cd['netmask'],cd['interface'])
      if err:
        return_dict['error'] = err
      else: 
        return django.http.HttpResponseRedirect('/view_routes/')
  return_dict['form'] = form
  return django.shortcuts.render_to_response("create_route.html", return_dict, context_instance=django.template.context.RequestContext(request))
  

def edit_route(request):
  return_dict = {}
  if request.method == 'GET':
    form = networking_forms.CreateRouteForm(request.GET)
  else:
    form = networking_forms.CreateRouteForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      status,err = route.delete_route(cd['ip'],cd['netmask'])
      status,err = route.add_route(cd['ip'],cd['gateway'],cd['netmask'],cd['interface'])
      if err:
        return_dict['error'] = err
      else:
        return django.http.HttpResponseRedirect('/view_routes/')
  return_dict['form'] = form
  return django.shortcuts.render_to_response("create_route.html", return_dict, context_instance=django.template.context.RequestContext(request))
  pass

def delete_route(request):
  if request.method == "POST":
    ip = request.POST.get('ip')
    netmask = request.POST.get('netmask')
    gateway = request.POST.get('gateway')
    status,err = route.delete_route(ip,netmask)
    if err:
        return_dict['error'] = err
        return django.http.HttpResponseRedirect('/view_routes/')
    else:
        return django.http.HttpResponseRedirect('/view_routes/')
  else:
    return django.http.HttpResponseRedirect('/view_routes/')
        
def view_route(request):
  return_dict = {}
  return_dict['routes'] = route.list_routes()
  return django.shortcuts.render_to_response("list_routes.html", return_dict, context_instance=django.template.context.RequestContext(request))
