import zipfile
import io
import os
import django
import django.template

from integral_view.applications.storage_insights.forms import storage_insights_forms

from integralstor.applications.storage_insights import scan_utils, query_utils
from integralstor import django_utils, datetime_utils

query_types = [('extension_counts', 'View file count by extension', 'view_general_query_results?query_type=extension_counts'), ('files_by_extension', 'View files by extension', 'view_files_by_extension'), ('duplicates', 'View duplicate files', 'view_general_query_results?query_type=duplicate_sets'), ('newest_files', 'View most recently modified files', 'view_general_query_results?query_type=newest_files'), ('oldest_files','View files with oldest modify times', 'view_general_query_results?query_type=oldest_files'), ('largest_files', 'View largest files', 'view_general_query_results?query_type=largest_files'), ('find_files', 'Find files', 'find_files')]

def view_query_types(request):
    return_dict = {}
    global query_types
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['query_type', 'scan_configuration_id'])
        if err:
            raise Exception(err)

        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)
        if configurations:
            return_dict['configurations'] = configurations


        if request.method == "GET":

            form = storage_insights_forms.ViewQueryTypesForm(configurations = configurations, query_types = query_types)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("view_query_types.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.ViewQueryTypesForm(request.POST, configurations = configurations, query_types = query_types)
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                query_type = cd['query_type']
                scan_configuration_id = int(cd['scan_configuration_id'])
                for q in query_types:
                    if q[0] == query_type:
                        break
                if '?' in q[2]:
                    url = '/applications/storage_insights/%s&scan_configuration_id=%d'%(q[2], scan_configuration_id)
                else:
                    url = '/applications/storage_insights/%s?scan_configuration_id=%d'%(q[2], scan_configuration_id)
                print url
                #raise Exception('a')
                return django.http.HttpResponseRedirect(url)
            else:
                return django.shortcuts.render_to_response("view_query_types.html", return_dict, context_instance=django.template.context.RequestContext(request))
        query_type = None
        if 'query_type' in req_params and req_params['query_type']:
            query_type = req_params['query_type']
        if query_type:
            if query_type not in query_types:
                raise Exception('Unknown query type. Please use the menus')
        return_dict['query_types'] = query_types
        return django.shortcuts.render_to_response('view_query_types.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Select Insight type '
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight types'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_general_query_results(request):
    return_dict = {}
    global query_types
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'query_type', 'param1'])
        if err:
            raise Exception(err)

        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        if 'query_type' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        query_type = req_params['query_type']
        
        if query_type not in ['extension_counts', 'largest_files', 'oldest_files', 'newest_files', 'duplicate_sets', 'duplicate_files']:
            raise Exception('Invalid request. Please use the menus.')

        query_type_str = ''
        for qt in query_types:
            if qt[0] == query_type:
                query_type_str = qt[1]
                break
        return_dict['query_type_str'] = query_type_str

        if query_type == 'duplicate_files':
            if 'param1' not in req_params:
                raise Exception('Invalid request. Please use the menus.')
            results, err = query_utils.get_file_info_query_results(query_type = query_type, scan_configuration_id=scan_configuration_id, param1=req_params['param1'])
        else:
            results, err = query_utils.get_file_info_query_results(query_type = query_type, scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        template = 'view_%s_results.html'%query_type
        return_dict['results'] = results
        return_dict['scan_configuration_id'] = scan_configuration_id
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights query'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight query result '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_files_by_extension(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'extension'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        extensions, err = query_utils.get_unique_extensions(scan_configuration_id=scan_configuration_id)
        if err:
            raise Exception(err)
        configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id, standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        if request.method == "GET":
            form = storage_insights_forms.GetFilesByExtensionForm(initial={'scan_configuration_id': scan_configuration_id}, extensions = extensions)
            return_dict["form"] = form
            return_dict["scan_dir"] = configurations[0]['scan_dir']
            return django.shortcuts.render_to_response("files_by_extension_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.GetFilesByExtensionForm(request.POST, initial={'scan_configuration_id': scan_configuration_id}, extensions = extensions)
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                results, err = query_utils.get_files_by_extension(scan_configuration_id=scan_configuration_id, extension = cd['extension'])
                if err:
                    raise Exception(err)
                return_dict['results'] = results
                return django.shortcuts.render_to_response("view_files_by_extension_results.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("files_by_extension_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights - Extension Counts'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight information - files by extension'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def find_files(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id', 'file_name_pattern'])
        if err:
            raise Exception(err)
        if 'scan_configuration_id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')
        scan_configuration_id = int(req_params['scan_configuration_id'])

        configurations, err = scan_utils.get_scan_configurations(scan_configuration_id=scan_configuration_id, standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        if request.method == "GET":
            form = storage_insights_forms.FindFilesForm(initial={'scan_configuration_id': scan_configuration_id})
            return_dict["form"] = form
            return_dict["scan_dir"] = configurations[0]['scan_dir']
            return django.shortcuts.render_to_response("find_files_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            form = storage_insights_forms.FindFilesForm(request.POST, initial={'scan_configuration_id': scan_configuration_id})
            return_dict['form'] = form
            if form.is_valid():
                cd = form.cleaned_data
                results, err = query_utils.find_files(scan_configuration_id=scan_configuration_id, file_name_pattern = cd['file_name_pattern'])
                if err:
                    raise Exception(err)
                return_dict['results'] = results
                return django.shortcuts.render_to_response("view_find_files_results.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("find_files_form.html", return_dict, context_instance=django.template.context.RequestContext(request))
        
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights - Find files'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error loading Storage Insight information - find files'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def download_file(request):
    return_dict = {}
    try:

        req_params, err = django_utils.get_request_parameter_values(request, ['id'])
        if err:
            raise Exception(err)

        if 'id' not in req_params:
            raise Exception('Invalid request. Please use the menus.')

        id = req_params['id']
        file_info_row, err = query_utils.get_file_info(param = id, param_type='id')
        if err:
            raise Exception(err)
        base_name = os.path.basename(file_info_row['path'])

        zf_name = '%s.zip' % base_name
        try:
            out = io.BytesIO()
            zf = zipfile.ZipFile(out, 'w')
            zf.write(file_info_row['path'], arcname=base_name)
            zf.close()
        except Exception as e:
            raise Exception(
                "Error compressing log file : %s" % str(e))

        response = django.http.HttpResponse(
            out.getvalue(), content_type='application/x-compressed')
        response['Content-disposition'] = 'attachment; filename=%s' % (
            zf_name)

        return response
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Download file'
        return_dict['tab'] = 'query_tab'
        return_dict["error"] = 'Error downloading file'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def view_dashboard(request):
    return_dict = {}
    try:
        req_params, err = django_utils.get_request_parameter_values(request, ['scan_configuration_id'])
        if err:
            raise Exception(err)

        configurations, err = scan_utils.get_scan_configurations(standalone=False, include_deleted=True)
        if err:
            raise Exception(err)

        num_deleted_configurations = 0
        num_active_configurations = 0
        num_configurations = 0

        initial = {}
        scan_configuration_id = None
        if 'scan_configuration_id' in req_params:
            if req_params['scan_configuration_id'] != 'None':
                scan_configuration_id = int(req_params['scan_configuration_id'])
                initial['scan_configuration_id'] = scan_configuration_id

        selected_config = None
        for c in configurations:
            if scan_configuration_id and c['id'] == scan_configuration_id:
                selected_config = c
            if c['status_id'] == -1:
                num_deleted_configurations += 1
            else:
                num_active_configurations += 1

        if selected_config:
            scan_details = {}
            all_scans, err = scan_utils.get_scans(standalone=False)
            if err:
                raise Exception(err)
            selected_scans = []
            for scan in all_scans:
                if scan['scan_configuration_id'] == scan_configuration_id:
                    selected_scans.append(scan)
            scan_details['num_scans'] = len(selected_scans)
            latest = 0
            latest_successful = 0
            for scan in selected_scans:
                if scan['initiate_time'] > latest:
                    latest = scan['initiate_time']
                if scan['status_id'] == 2 and scan['initiate_time'] > latest_successful:
                    latest_successful = scan['initiate_time']
            if latest:
                lt, err = datetime_utils.convert_from_epoch(latest, return_format='str', str_format='%c', to='local')
                if err:
                    raise Exception(err)
                scan_details['latest_scan'] = lt
            if latest_successful:
                lt, err = datetime_utils.convert_from_epoch(latest_successful, return_format='str', str_format='%c', to='local')
                if err:
                    raise Exception(err)
                scan_details['latest_successful_scan'] = lt
            return_dict['scan_details'] = scan_details
            return_dict['selected_configuration'] = selected_config

            duplicate_sets, err = query_utils.get_duplicate_sets(scan_configuration_id)
            if err:
                raise Exception(err)
            return_dict['duplicate_sets'] = duplicate_sets

        num_configurations = num_deleted_configurations + num_active_configurations


        db_details, err = scan_utils.get_db_details()
        if err:
            raise Exception(err)
        return_dict['db_details'] = db_details
        form = storage_insights_forms.ViewConfigurationsForm(initial=initial, configurations=configurations)
        return_dict['form'] = form

        return_dict['configurations'] = configurations
        return_dict['num_deleted_configurations'] = num_deleted_configurations
        return_dict['num_active_configurations'] = num_active_configurations
        return_dict['num_configurations'] = num_configurations
        return django.shortcuts.render_to_response('view_storage_insights_dashboard.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_insights_base.html"
        return_dict["page_title"] = 'Storage Insights dashboard'
        return_dict['tab'] = 'dashboard_tab'
        return_dict["error"] = 'Error loading Storage Insight dashboard'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
