import django 
import django.template
from commands import getstatusoutput
from integral_view.forms import clamav_management_forms 
from integralstor_unicell import local_users
from integralstor_common import scheduler_utils, clamav
from os import listdir
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
            


def change_av_status(request):
  try:
    if 'name' not in request.REQUEST and 'avscan' not in request.REQUEST:
      raise Exception("Malformed request. Please use the menus.")
    name = request.REQUEST['name']
    avscan = request.REQUEST['avscan']
    result,err = clamav.change_scan_file(name, str(avscan))
    if err:
      raise Exception(err)
    if result not in ['on','off']:
      raise Exception(result)
    return django.http.HttpResponseRedirect('/view_zfs_dataset?name={0}&ack=virus_scan_{1}'.format(name,result))
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
    config,err = clamav.get_file()
    if err:
      raise Exception(err)
    update_config,err = clamav.get_file_updater()
    if err:
      raise Exception(err)
    if request.method == 'GET':
      if config:
        form = clamav_management_forms.Config()
        return_dict['form'] = form
        return_dict['config'] = config
        return_dict['update_check'] = update_config
        cron_task_id,err = clamav.get_cron_id()
        if err:
          raise Exception(err)
        crons = scheduler_utils.get_cron_tasks(cron_task_id)
        return_dict['current_schedule'] = crons[0][0]['schedule_description']
        return django.shortcuts.render_to_response('configure_clamav.html', return_dict, context_instance = django.template.context.RequestContext(request))
      else:
        raise Exception('ClamAV config file error.')
    else:
      form = clamav_management_forms.Config(request.POST)
      return_dict['form'] = form
      if form.is_valid():
        MaxFiles = form.cleaned_data['MaxFiles']
        config['MaxFiles'] = MaxFiles
        MaxScanSize = form.cleaned_data['MaxScanSize']
        config['MaxScanSize'] = MaxScanSize
        MaxFileSize = form.cleaned_data['MaxFileSize']
        config['MaxFileSize'] = MaxFileSize
        response,err = clamav.write_conf(config)
        if err:
          raise Exception(err)
                ###############################
        Checks = form.cleaned_data['Checks']
        update_config['Checks'] = Checks
        response,err = clamav.write_conf_updater(update_config)
        if err:
          raise Exception(err)
################################################################
        scheduler = request.POST.get('scheduler')
        schedule = scheduler.split()
        return_dict['schedule'] = schedule
        cron_task_id,err = clamav.add_cron(schedule)
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

def upload_update(request):
  return_dict = {}
  try:
    if request.method == 'POST' and request.FILES['update_file']:
      update_file = request.FILES['update_file']
      fs = FileSystemStorage(location='/opt/integralstor/integralstor_unicell/config/clamav/virus_definations/')
      if update_file.name not in ['daily.cvd', 'main.cvd', 'bytecode.cvd']:
        raise Exception('Only clamav update files allowed')
      getstatusoutput('rm -f /opt/integralstor/integralstor_unicell/config/clamav/virus_definations/'+update_file.name)
      getstatusoutput('rm -f /var/lib/clamav/'+update_file.name)
      filename = fs.save(update_file.name, update_file)
      confirm,err = clamav.match_date(update_file.name)
      if err:
        raise Exception(err)
      if confirm == 'invalid':
        raise Exception('Update file is not downloaded today. Use the update file downloaded today')
      st,cm = getstatusoutput('ln -s /opt/integralstor/integralstor_unicell/config/clamav/virus_definations/'+update_file.name+' /var/lib/clamav/'+update_file.name)
      if st != 0:
		    raise Exception(cm)
      getstatusoutput('sytemctl restart clamd@scan')
      return django.http.HttpResponseRedirect('/view_clamav_configuration?ack=uploaded')
    return render(request, 'upload_update.html')
  except Exception,e:
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'Configure ClamAV'
    return_dict['tab'] = 'clamav_configuration'
    return_dict["error"] = 'Error uploading file.'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def restore_default(request):
  try:
    status,op = getstatusoutput('cp /usr/local/etc/clamd.conf.default /usr/local/etc/clamd.conf')
    if status !=0:
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
    config,err = clamav.get_file()
    if err:
      raise Exception(err)
    update_check,err = clamav.get_file_updater()
    if err:
      raise Exception(err)
    return_dict['config'] = config
    return_dict['update_check'] = update_check
        #################
    cron_task_id,err = clamav.get_cron_id()
    if err:
      raise Exception(err)
    crons = scheduler_utils.get_cron_tasks(cron_task_id)
    return_dict['schedule'] = crons[0][0]['schedule_description']
        #################
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
      virus_list = listdir('/opt/integralstor/integralstor_unicell/config/clamav/quarantine/')
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
        virus_list = listdir('/opt/integralstor/integralstor_unicell/config/clamav/quarantine/')
        if virus_list == []:
          return_dict['virus_list'] = ['There are no Files in the quarentine',]
        else:
          return_dict['virus_list'] = virus_list
        for virus_file in virus_list:
          if cl[virus_file]:
            status,cm = getstatusoutput('rm -rf /opt/integralstor/integralstor_unicell/config/clamav/quarantine/%s' %virus_file)
            if status != 0:
              raise Exception('Error Deleting File')
        return django.http.HttpResponseRedirect('/view_quarantine.html')
      else :
          return django.shortcuts.render_to_response("view_quarantine.html", return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception,e :
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'View Quarentine'
    return_dict['tab'] = 'quarantine'
    return_dict["error"] = 'Error retrieving the quarantine'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def del_all_virus(request):
  try:
    status,cm = getstatusoutput('rm -rf /opt/integralstor/integralstor_unicell/config/clamav/quarantine/*')
    if status != 0:
      raise Exception('Error Deleting File')
    return django.http.HttpResponseRedirect('/view_quarantine.html')
  except Exception,e :
    return_dict['base_template'] = "services_base.html"
    return_dict["page_title"] = 'View Quarentine'
    return_dict['tab'] = 'quarantine'
    return_dict["error"] = 'Error emptying the quarantine'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

