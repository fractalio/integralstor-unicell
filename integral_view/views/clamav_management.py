import django 
import django.template
from integral_view.forms import clamav_management_forms 
from integralstor_unicell import local_users
from integralstor_common import scheduler_utils, clamav, common
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
            


def change_av_status(request):
  try:
    if 'avscan' not in request.REQUEST and 'name' not in request.REQUEST:
      raise Exception("Malformed request. Please use the menus.")
    name = request.REQUEST['name']
    avscan = request.REQUEST['avscan']
    result,err = clamav.update_scan_list(name, avscan)
    if err:
      raise Exception(err)
    return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&ack=virus_scan_%s'%(name,result))
  except Exception, e:
    return_dict={}
    return_dict['base_template'] = "storage_base.html"
    return_dict["page_title"] = 'Dataset Virus Scan status'
    return_dict['tab'] = 'view_zfs_pools_tab'
    return_dict["error"] = 'Error set ZFS dataset virus scan'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



def configure_clamav(request):
  return_dict = {}
  try:
    config,err = clamav.get_clamav_conf('clamd')
    if err:
      raise Exception(err)
    update_config,err = clamav.get_clamav_conf('freshclam')
    if err:
      raise Exception(err)
    if request.method == 'GET':
      if config:
        form = clamav_management_forms.ClamavConfiguration()
        return_dict['form'] = form
        return_dict['config'] = config
        return_dict['update_check'] = update_config
        cron_task_id,err = clamav.get_clamav_cron_id()
        if err:
          raise Exception(err)
        if cron_task_id:
          crons = scheduler_utils.get_cron_tasks(cron_task_id)
          return_dict['current_schedule'] = crons[0][0]['schedule_description']
        else:
          return_dict['current_schedule'] = 'Not Set'
        return django.shortcuts.render_to_response('configure_clamav.html', return_dict, context_instance = django.template.context.RequestContext(request))
      else:
        raise Exception('ClamAV config file error.')
    else:
      form = clamav_management_forms.ClamavConfiguration(request.POST)
      return_dict['form'] = form
      if form.is_valid():
        max_files = form.cleaned_data['max_files']
        config['MaxFiles'] = max_files
        max_scan_size = form.cleaned_data['max_scan_size']
        config['MaxScanSize'] = max_scan_size
        max_file_size = form.cleaned_data['max_file_size']
        config['MaxFileSize'] = max_file_size
        response,err = clamav.update_clamav_conf(config, 'clamd')
        if err:
          raise Exception(err)
        checks = form.cleaned_data['checks']
        update_config['Checks'] = checks
        response,err = clamav.update_clamav_conf(update_config, 'freshclam')
        if err:
          raise Exception(err)
        scheduler = request.POST.get('scheduler')
        schedule = scheduler.split()
        return_dict['schedule'] = schedule
        old_cron_id,err = clamav.get_clamav_cron_id()
        if err:
          raise Exception(err)
        cron_task_id,err = clamav.update_clamav_cron(schedule,old_cron_id)
        if err:
          raise Exception(err)
        return django.http.HttpResponseRedirect('/view_clamav_configuration?ack=saved')
      else:
        return django.shortcuts.render_to_response("configure_clamav.html", return_dict, context_instance = django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Configure ClamAV'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error configuring ClamAV '
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def upload_clamav_update(request):
  return_dict = {}
  try:
    if request.method == 'POST' and request.FILES['update_file']:
      update_file = request.FILES['update_file']
      root,err = common.clamav_virus_definations_directory()
      if err:
        raise Exception(err)
      fs = FileSystemStorage(location='%s/.new'%root)
      if update_file.name not in ['daily.cvd', 'main.cvd', 'bytecode.cvd']:
        raise Exception('Only clamav update files allowed')
      filename = fs.save(update_file.name, update_file)
      status,err = clamav.update_virus_definations(update_file.name)
      if err:
        raise Exception(err)
      return django.http.HttpResponseRedirect('/view_clamav_configuration?ack=uploaded')
    return render(request, 'upload_clamav_update.html')
  except Exception,e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Configure ClamAV'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error uploading file.'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def restore_default(request):
  try:
    status,err = clamav.restore_default_clamav_conf()
    if err:
      raise Exception(err)
    return django.http.HttpResponse('/view_clamav_configuration?ack=restored')
  except Excepttion,e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Configure ClamAV'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error configuring ClamAV '
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))



def view_clamav_configuration(request):
  return_dict = {}
  try:
    if 'ack' in request.GET:
      if request.GET["ack"] == "saved":
        return_dict['ack_message'] = "ClamAV Configuration Updated"
      if request.GET["ack"] == "restored":
        return_dict['ack_message'] = "Configuration restored to Default"
      if request.GET["ack"] == "uploaded":
    	return_dict['ack_message'] = "Update file uploaded"
    config,err = clamav.get_clamav_conf('clamd')
    if err:
      raise Exception(err)
    update_check,err = clamav.get_clamav_conf('freshclam')
    if err:
      raise Exception(err)
    return_dict['config'] = config
    return_dict['update_check'] = update_check
    cron_task_id,err = clamav.get_clamav_cron_id()
    if err:
      raise Exception(err)
    if cron_task_id:
      crons = scheduler_utils.get_cron_tasks(cron_task_id) 
      return_dict['schedule'] = crons[0][0]['schedule_description']
    else:
      return_dict['schedule'] = 'Not Set'
    return django.shortcuts.render_to_response('view_clamav_configuration.html', return_dict, context_instance = django.template.context.RequestContext(request))

  except Exception, e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'View ClamAV configuration'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error retrieving the ClamAV configuration'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request)) 



def view_quarantine(request):
  return_dict = {}
  try:
    if request.method == 'GET':
      form = clamav_management_forms.QuarantineList()
      return_dict['form'] = form
      virus_list,err = clamav.get_quarantine_list()
      if err:
        raise Exception(err)
      if virus_list == []:
        return_dict['virus_list'] = ['There are no Files in the quarentine',]
      else:
        return_dict['virus_list'] = virus_list
      return django.shortcuts.render_to_response("view_quarantine.html", return_dict, context_instance=django.template.context.RequestContext(request))
    else:
      form = clamav_management_forms.QuarantineList(request.POST)
      return_dict['form'] = form
      if form.is_valid():
        cl = form.cleaned_data
        virus_list,err = clamav.get_quarantine_list()
        if err:
          raise Exception(err)
        if virus_list == []:
          return_dict['virus_list'] = ['There are no Files in the quarantine',]
        else:
          return_dict['virus_list'] = virus_list
        for virus_file in virus_list:
          if cl[virus_file]:
            status,err = clamav.delete_virus(virus_file)
            if err:
              raise Exception(err)
        return django.http.HttpResponseRedirect('/view_quarantine.html')
      else :
          return django.shortcuts.render_to_response("view_quarantine.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception,e :
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'View Quarantine'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error retrieving the quarantine'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def delete_all_virus(request):
  try:
    status,err = clamav.delete_all_virus()
    if err:
      raise Exception(err)
    return django.http.HttpResponseRedirect('/view_quarantine.html')
  except Exception,e :
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'View Quarentine'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error emptying the quarantine'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

