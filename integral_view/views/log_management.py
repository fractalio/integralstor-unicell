import zipfile, datetime,os,shutil

import django, django.template
from  django.contrib import auth
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required

from integralstor_common import common, audit, alerts,command, db
from integralstor_common.clamav import vs_log

from integralstor_unicell import system_info

import integral_view
from integral_view.forms import log_management_forms,common_forms
from integral_view.utils import iv_logging

def view_log(request):
  return_dict = {}
  try:
    form = log_management_forms.ViewLogsForm(request.POST or None)
    if request.method == 'POST':
      if form.is_valid():
        cd = form.cleaned_data
        log_type = cd['log_type']
        if log_type not in ['alerts', 'audit', 'hardware', 'av']:
          raise Exception('Invalid log type specified')
        if log_type == 'alerts':
          alerts_list, err = alerts.load_alerts()
          if err:
            raise Exception(err)
          return_dict['alerts_list'] = alerts_list
          return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance=django.template.context.RequestContext(request))
        elif log_type == 'audit':
          al, err = audit.get_lines()
          if err:
            raise Exception(err)
          return_dict["audit_list"] = al
          return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance=django.template.context.RequestContext(request))
        ################
        elif log_type == 'av':
            vs_log_list,err = vs_log()
            if err:
                raise Exception(err)
            return_dict['vs_log_list'] = vs_log_list
            return django.shortcuts.render_to_response('view_virus_scan_logs.html', return_dict, context_instance=django.template.context.RequestContext(request))

        ################
        
        elif log_type == 'hardware':
          hw_platform, err = common.get_hardware_platform()
          if err:
            raise Exception(err)
          if not hw_platform or hw_platform != 'dell':
            raise Exception('Unknown hardware platform')
          return_dict['hw_platform'] = hw_platform
          if hw_platform == 'dell':
            from integralstor_common.platforms import dell
            logs_dict, err = dell.get_alert_logs()
            if logs_dict:
              return_dict['logs_dict'] = logs_dict
          return django.shortcuts.render_to_response('view_hardware_logs.html', return_dict, context_instance=django.template.context.RequestContext(request))
    # either a get or an invalid form so send back form
    return_dict['form'] = form
    return django.shortcuts.render_to_response('view_log_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'System alerts'
    return_dict['tab'] = 'view_current_alerts_tab'
    return_dict["error"] = 'Error loading system alerts'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_virus_scan_logs(request):
    return_dict = {}
    try:
        vs_log_list,err = vs_log()
        if err:
            raise Exception(err)
        return_dict['vs_log_list'] = vs_log_list
        return django.shortcuts.render_to_response('view_virus_scan_logs.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "logging_base.html"
        return_dict["page_title"] = 'System alerts'
        return_dict['tab'] = 'view_current_alerts_tab'
        return_dict["error"] = 'Error loading system alerts'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_alerts(request):
  return_dict = {}
  try:
    alerts_list, err = alerts.load_alerts()
    if err:
      raise Exception(err)
    return_dict['alerts_list'] = alerts_list
    return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'System alerts'
    return_dict['tab'] = 'view_current_alerts_tab'
    return_dict["error"] = 'Error loading system alerts'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_hardware_logs(request):
  return_dict = {}
  try:
    hw_platform, err = common.get_hardware_platform()
    if hw_platform:
      return_dict['hw_platform'] = hw_platform
      if hw_platform == 'dell':
        from integralstor_common.platforms import dell
        logs_dict, err = dell.get_alert_logs()
        if logs_dict:
          return_dict['logs_dict'] = logs_dict
    return django.shortcuts.render_to_response('view_hardware_logs.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Hardware logs'
    return_dict['tab'] = 'view_hardware_logs_tab'
    return_dict["error"] = 'Error loading hardware logs'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_audit_trail(request):
  return_dict = {}
  try:
    al = None
    al, err = audit.get_lines()
    if err:
      raise Exception(err)
    return_dict["audit_list"] = al
    return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'System audit trail'
    return_dict['tab'] = 'view_current_audit_tab'
    return_dict["error"] = 'Error loading system audit trail'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def handle_uploaded_file(f):
  with open('/tmp/upload.zip', 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
  return True,"/tmp/upload.zip"

def copy_and_overwrite(from_path, to_path):
  if os.path.exists(to_path):
    shutil.rmtree(to_path)
  #command.execute("cp -rf %s/* %s"%(from_path,to_path))
  shutil.copytree(from_path, to_path)
  return True

def copy_file_and_overwrite(from_path,to_path):
  shutil.copyfile(from_path,to_path)
  return True

def edit_integral_view_log_level(request):

  return_dict = {}
  try:
    if request.method == 'POST':
      iv_logging.debug("Trying to change Integral View Log settings")
      form = log_management_forms.IntegralViewLoggingForm(request.POST)
      if form.is_valid():
        iv_logging.debug("Trying to change Integral View Log settings - form valid")
        cd = form.cleaned_data
        log_level = int(cd['log_level'])
        iv_logging.debug("Trying to change Integral View Log settings - log level is %d"%log_level)
        ret, err = iv_logging.set_log_level(log_level)
        if err:
          raise Exception(err)
        iv_logging.debug("Trying to change Integral View Log settings - changed log level")
        return django.http.HttpResponseRedirect("/show/integral_view_log_level?saved=1")
    else:
      init = {}
      init['log_level'] = iv_logging.get_log_level()
      form = log_management_forms.IntegralViewLoggingForm(initial=init)
      return_dict['form'] = form
      return django.shortcuts.render_to_response('edit_integral_view_log_level.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Modify IntegralView log level'
    return_dict['tab'] = 'view_current_audit_tab'
    return_dict["error"] = 'Error modifying IntegralView log level'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def download_log(request):
  """ Download the system log of the type specified in log_type POST param 
  This calls the /sys_log via an http request on that node to get the info"""

  return_dict = {}
  try:
    form = log_management_forms.DownloadLogsForm(request.POST or None)
  
    if request.method == 'POST':
      if form.is_valid():
        cd = form.cleaned_data
        log_type = cd['log_type']
  
        response = django.http.HttpResponse()
        if log_type in ['alerts', 'audit', 'hardware']:
          if log_type == 'alerts':
            response['Content-disposition'] = 'attachment; filename=alerts_log.txt'
            all_alerts, err = alerts.load_alerts()
            if err:
              raise Exception(err)
            for alert in all_alerts:
              response.write('%s : %s\n'%(alert['time'], alert['message']))
              response.flush()
          elif log_type == 'audit':
            response['Content-disposition'] = 'attachment; filename=audit_log.txt'
            all_audits, err = audit.get_lines()
            if err:
              raise Exception(err)
            for audit_info in all_audits:
              response.write('Time : %s \n'%audit_info['time'])
              response.write('Source IP : %s \n'%audit_info['ip'])
              response.write('Action : %s \n'%audit_info['action'])
              response.write('\n')
              response.flush()
          elif log_type == 'hardware':
            response['Content-disposition'] = 'attachment; filename=hardware_logs.txt'
            hw_platform, err = common.get_hardware_platform()
            if not hw_platform or hw_platform != 'dell':
              raise Exception('Unknown hardware platform')
            if hw_platform == 'dell':
              from integralstor_common.platforms import dell
              logs_dict, err = dell.get_alert_logs()
              if err:
                raise Exception(err)
              if not logs_dict:
                raise Exception('No logs detected!')
              for timestamp, log_list in logs_dict.items():
                for log in log_list:
                  response.write('Time : %s\n'%log['date_time'])
                  response.write('Severity : %s\n'%log['Severity'])
                  response.write('Description : %s\n'%log['description'])
                  response.write('\n')
                  response.flush()
            else:
              raise Exception('Unknown platform')
        else:
  
            fn = {'boot':'/var/log/boot.log', 'dmesg':'/var/log/dmesg', 'message':'/var/log/messages', 'smb':'/var/log/smblog.vfs', 'winbind':'/var/log/samba/log.winbindd','ctdb':'/var/log/log.ctdb'}
            dn = {'boot':'boot.log', 'dmesg':'dmesg', 'message':'messages','smb':'samba_logs','winbind':'winbind_logs','ctdb':'ctdb_logs'}
  
            file_name = fn[log_type]
            display_name = dn[log_type]
  
            zf_name = '%s.zip'%display_name
      
            try:
              zf = zipfile.ZipFile(zf_name, 'w')
              zf.write(file_name, arcname = display_name)
              zf.close()
            except Exception as e:
              raise Exception("Error compressing remote log file : %s"%str(e))
  
            response['Content-disposition'] = 'attachment; filename=%s.zip'%(display_name)
            response['Content-type'] = 'application/x-compressed'
            with open(zf_name, 'rb') as f:
              byte = f.read(1)
              while byte:
                response.write(byte)
                byte = f.read(1)
            response.flush()
  
        return response
  
    # either a get or an invalid form so send back form
    return_dict['form'] = form
    return django.shortcuts.render_to_response('download_log_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Download system logs'
    return_dict['tab'] = 'download_logs_tab'
    return_dict["error"] = 'Error downloading system logs'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

'''
  
def download_hardware_logs(request):
  return_dict = {}
  try:
  
    hw_platform, err = common.get_hardware_platform()
    if not hw_platform or hw_platform != 'dell':
      raise Exception('Unknown hardware platform')
    if hw_platform == 'dell':
      from integralstor_common.platforms import dell
      logs_dict, err = dell.get_alert_logs()
      if err:
        raise Exception(err)
      if not logs_dict:
        raise Exception('No logs detected!')

      try:
        response = django.http.HttpResponse()
        response['Content-disposition'] = 'attachment; filename=hardware_logs.txt'
        response['Content-type'] = 'text/plain'
        for timestamp, log_list in logs_dict.items():
          for log in log_list:
            response.write('Time : %s\n'%log['date_time'])
            response.write('Severity : %s\n'%log['Severity'])
            response.write('Description : %s\n'%log['description'])
            response.write('\n')
            response.flush()
      except Exception as e:
        raise Exception(e)
  
      return response
  
    # either a get or an invalid form so send back form
    return_dict['form'] = form
    return django.shortcuts.render_to_response('download_sys_log_form.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Download system logs'
    return_dict['tab'] = 'view_hardware_logs_tab'
    return_dict["error"] = 'Error downloading hardware logs'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
'''
  
def rotate_log(request, log_type=None):
  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
      return django.shortcuts.render_to_response('logged_in_error.html', return_dict, context_instance = django.template.context.RequestContext(request))
    if log_type == "alerts":
      return_dict['tab'] = 'view_current_alerts_tab'
      return_dict["page_title"] = 'Rotate system alerts log'
      ret, err = alerts.rotate_alerts()
      if err:
        raise Exception(err)
      return_dict["message"] = "Alerts log successfully rotated."
      return django.http.HttpResponseRedirect("/view_rotated_log_list/alerts?success=true")
    elif log_type == "audit_trail":
      return_dict['tab'] = 'view_current_audit_tab'
      return_dict["page_title"] = 'Rotate system audit trail'
      ret, err = audit.rotate_audit_trail()
      if err:
        raise Exception(err)
      return_dict["message"] = "Audit trail successfully rotated."
      return django.http.HttpResponseRedirect("/view_rotated_log_list/audit_trail/?success=true")
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error rotating log'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

  
def download_sys_info(request):
  return_dict = {}
  try:
    display_name, err = common.get_config_dir()
    if err:
      raise Exception(err)
    zf_name = "system_info.zip"
    try:
      zf = zipfile.ZipFile(zf_name, 'w')
      abs_src = os.path.abspath(display_name)
      for dirname, subdirs, files in os.walk(display_name):
        if not( ("logs" in dirname) or ("ntp" in dirname) or ("rc_local" in dirname) or ("samba" in dirname) or ("status" in dirname)):
          for filename in files: 
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
      logs = {'smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf','nfs':'/etc/exports','ftp':'/etc/vsftpd/vsftpd.conf','master.status':display_name+"/status/master.status",'master.manifest':display_name+"/status/master.manifest"}
      for key,value in logs.iteritems():
          if os.path.isfile(value):
            zf.write(value, key)
      zf.close()
    except Exception as e:
      raise Exception("Error compressing remote log file : %s"%str(e))
    response = django.http.HttpResponse()
    response['Content-disposition'] = 'attachment; filename=system_info.zip'
    response['Content-type'] = 'application/x-compressed'
    with open(zf_name, 'rb') as f:
      byte = f.read(1)
      while byte:
        response.write(byte)
        byte = f.read(1)
    response.flush()
    return response
  except Exception as e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'Download system information'
    return_dict['tab'] = 'node_info_tab'
    return_dict["error"] = 'Error downloading system information'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_sys_info(request):
  return_dict = {}
  try:
    if request.method == "POST" :
      status,path = handle_uploaded_file(request.FILES['file_field'])
      display_name, err = common.get_config_dir()
      if err:
        raise Exception(err)
      if path:
        zip = zipfile.ZipFile(path,'r')
        data = zip.namelist()
        move = zip.extractall("/tmp/upload/")
       # logs = {'smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf','nfs':'/etc/exports','ftp':'/etc/vsftpd/vsftpd.conf'}
        logs = {'smb_conf':'/etc/samba/smb.conf','ntp_conf':'/etc/ntp.conf','krb5_conf':'/etc/krb5.conf','nfs':'/etc/exports','ftp':'/etc/vsftpd/vsftpd.conf','master.status':display_name+"/status/master.status",'master.manifest':display_name+"/status/master.manifest"}
        for key,value in logs.iteritems():
          if key and os.path.isfile("/tmp/upload/"+key):
            copy_file_and_overwrite("/tmp/upload/"+key,value)
        for dir in os.listdir("/tmp/upload"):
          if dir and os.path.isdir("/tmp/upload/"+dir):
            copy_and_overwrite("/tmp/upload/"+dir,common.get_config_dir()[0]+"/"+dir)
        return django.http.HttpResponseRedirect("/view_system_info/")
    else:
      form = common_forms.FileUploadForm()
      return_dict["form"] = form  
      return django.shortcuts.render_to_response("upload_sys_info.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception,e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error displaying rotated log list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
   

def view_rotated_log_list(request, log_type):

  return_dict = {}
  try:
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
    l = None
    if log_type == "alerts":
      return_dict["page_title"] = 'View rotated alerts logs'
      return_dict['tab'] = 'view_rotated_alert_log_list_tab'
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical alerts log"
      l, err = alerts.get_log_file_list()
      if err:
        raise Exception(err)
    elif log_type == "audit_trail":
      return_dict["page_title"] = 'View rotated audit trail logs'
      return_dict['tab'] = 'view_rotated_audit_log_list_tab'
      return_dict["page_header"] = "Logging"
      return_dict["page_sub_header"] = "View historical audit log"
      l, err = audit.get_log_file_list()
      if err:
        raise Exception(err)
  
    return_dict["type"] = log_type
    return_dict["log_file_list"] = l
    return django.shortcuts.render_to_response('view_rolled_log_list.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["error"] = 'Error displaying rotated log list'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_rotated_log_file(request, log_type):

  return_dict = {}
  try:
    return_dict['tab'] = 'view_rotated_alert_log_list_tab'
    if log_type not in ["alerts", "audit_trail"]:
      raise Exception("Unknown log type")
  
    if request.method != "POST":
      raise Exception("Unsupported request")
      
    if "file_name" not in request.POST:
      raise Exception("Filename not specified")
  
    file_name = request.POST["file_name"]
  
    return_dict["historical"] = True
    if log_type == "alerts":
      return_dict['tab'] = 'view_rotated_alert_log_list_tab'
      l, err = alerts.load_alerts(file_name)
      if err:
        raise Exception(err)
      return_dict["alerts_list"] = l
      return django.shortcuts.render_to_response('view_alerts.html', return_dict, context_instance = django.template.context.RequestContext(request))
    else:
      return_dict['tab'] = 'view_rotated_audit_log_list_tab'
      d, err = audit.get_lines(file_name)
      if err:
        raise Exception(err)
      return_dict["audit_list"] = d
      return django.shortcuts.render_to_response('view_audit_trail.html', return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "logging_base.html"
    return_dict["page_title"] = 'View rotated log file'
    return_dict["error"] = 'Error viewing rotated log file'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def refresh_alerts(request, random=None):
  try:
    from datetime import datetime
    cmd_list = []
    #this command will insert or update the row value if the row with the user exists.
    cmd = ["INSERT OR REPLACE INTO admin_alerts (user, last_refresh_time) values (?,?);", (request.user.username, datetime.now())]
    cmd_list.append(cmd)
    db_path, err = common.get_db_path()
    if err:
      raise Exception(err)
    test, err = db.execute_iud(db_path, cmd_list)
    if err:
      raise Exception(err)
    new_alerts_present, err = alerts.new_alerts()
    if err:
      raise Exception(err)
    if new_alerts_present:
      import json
      alerts_list, err = alerts.load_alerts(last_n = 5)
      if err:
        raise Exception(err)
      if not alerts_list:
        raise Exception('Error loading alerts')
      new_alerts = json.dumps([dict(alert=pn) for pn in alerts_list])
      return django.http.HttpResponse(new_alerts, content_type='application/json')
    else:
      clss = "btn btn-default btn-sm"
      message = "View alerts"
      return django.http.HttpResponse("No New Alerts")
  except Exception, e:
    return django.http.HttpResponse("Error loading alerts : %s"%str(e))

@login_required
def raise_alert(request):

  return_dict = {}
  template = "logged_in_error.html"
  if "msg" not in request.REQUEST:
    return_dict["error"] = "No alert message specified."
  else:
    try:
      msg = request.REQUEST["msg"]
      ret, err = alerts.raise_alert(msg)
      if err:
        raise Exception(err)
    except Exception, e:
      return_dict["error"] = "Error logging alert : %s"%e
      iv_logging.info("Error logging alert %s"%str(e))
    else:
      return django.http.HttpResponse("Raised alert")

  return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

@login_required
def internal_audit(request):

  response = django.http.HttpResponse()
  if request.method == "GET":
    response.write("Error!")
  else:
    if not "who" in request.POST or request.POST["who"] != "batch":
      response.write("Unknown requester")
      return response
    if (not "audit_action" in request.POST) or (not "audit_str" in request.POST):
      response.write("Insufficient information!")
    else:
      audit.audit(request.POST["audit_action"], request.POST["audit_str"], "0.0.0.0")
    response.write("Success")
  return response
import zipfile, datetime,os,shutil

import django, django.template
from  django.contrib import auth
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required

from integralstor_common import common, audit, alerts,command, db
from integralstor_common.clamav import vs_log
