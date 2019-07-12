import django
import django.template

from integralstor import afp, audit, django_utils, zfs

import integral_view
from integral_view.core.storage_access.forms import afp_volumes_forms

import os


def view_afp_volumes(request):
    return_dict = {}
    try:
        volumes_dict, err = afp.load_config_file()
        if not volumes_dict and err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "renamed":
                return_dict['ack_message'] = "AFP volume information successfully renamed"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "AFP volume successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "AFP volume successfully deleted"
        return_dict["volumes_dict"] = volumes_dict
        template = "view_afp_volumes.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'View AFP volumes'
        return_dict['tab'] = 'view_afp_volumes_tab'
        return_dict["error"] = 'Error loading AFP volumes'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def rename_afp_volume(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['path', 'current_name', 'new_name'])
        if err:
            raise Exception(err)

        if 'current_name' not in req_ret:
            raise Exception('Invalid request. Please use the menus.')

        volumes_dict, err = afp.load_config_file()
        if not volumes_dict and err:
            raise Exception(err)

        if req_ret['current_name'] not in volumes_dict.keys():
            raise Exception('Invalid volume specified. Please use the menus.')

        if request.method == "GET":
            initial = {}
            initial['current_name'] = req_ret['current_name']
            initial['path'] = volumes_dict[req_ret['current_name']]['path']
            form = afp_volumes_forms.RenameVolumeForm(initial=initial)
            return_dict['form'] = form
            return_dict['current_name'] = req_ret['current_name']
            return_dict['path'] = volumes_dict[req_ret['current_name']]['path']
            return django.shortcuts.render_to_response('rename_afp_volume.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = afp_volumes_forms.RenameVolumeForm(request.POST)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                result, err = afp.rename_volume(cd['current_name'], cd['new_name'])
                if err:
                    raise Exception(err)
                audit_str = 'Renamed AFP volume with path %s from "%s" to "%s"' % (cd['path'], cd['current_name'], cd['new_name'])
                audit.audit("rename_afp_volume", audit_str, request)
                return django.http.HttpResponseRedirect('/storage_access/view_afp_volumes?ack=renamed')
            else:
                return django.shortcuts.render_to_response('rename_afp_volume.html', return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Rename AFP volume'
        return_dict['tab'] = 'view_afp_volumes_tab'
        return_dict["error"] = 'Error renaming AFP volume'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_afp_volume(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['name'])
        if 'name' not in req_ret:
            raise Exception('Invalid request. Please use the menus.')
        volumes_dict, err = afp.load_config_file()
        if not volumes_dict and err:
            raise Exception(err)

        if req_ret['name'] not in volumes_dict.keys():
            raise Exception('Invalid volume specified. Please use the menus.')

        if request.method == "GET":
            # Return the conf page
            name = request.GET["name"]
            return_dict["name"] = name
            return_dict["path"] = volumes_dict[name]['path']
            return django.shortcuts.render_to_response("delete_afp_volume_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = afp.delete_volume(req_ret['name'])
            if err:
                raise Exception(err)

            audit_str = 'Deleted AFP volume name "%s" with path %s' % (req_ret['name'], volumes_dict[req_ret['name']]['path'])
            audit.audit("delete_afp_volume", audit_str, request)
            return django.http.HttpResponseRedirect('/storage_access/view_afp_volumes?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Remove AFP volume '
        return_dict['tab'] = 'view_afp_volumes_tab'
        return_dict["error"] = 'Error removing AFP volume'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

def create_afp_volume(request):
    return_dict = {}
    try:
        pools, err = zfs.get_pools()
        if err:
            raise Exception(err)

        ds_list = []
        for pool in pools:
            for ds in pool["datasets"]:
                if ds['properties']['type']['value'] == 'filesystem':
                    ds_list.append(
                        {'name': ds["name"], 'mountpoint': ds["mountpoint"]})
        if not ds_list:
            raise Exception(
                'No ZFS datasets available. Please create a dataset before creating shares.')

        req_ret, err = django_utils.get_request_parameter_values(
            request, ['name', 'dataset', 'path'])
        if err:
            raise Exception(err)

        if 'dataset' in req_ret:
            dataset = req_ret['dataset']
        else:
            dataset = ds_list[0]['mountpoint']
        if 'path' in req_ret:
            path = req_ret['path']
        else:
            path = dataset

        return_dict['path'] = path
        return_dict["dataset"] = ds_list

        if request.method == "GET":
            # Return the conf page
            initial = {}
            initial['path'] = path
            initial['dataset'] = dataset
            form = afp_volumes_forms.CreateVolumeForm(
                initial=initial, dataset_list=ds_list)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_afp_volume.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = afp_volumes_forms.CreateVolumeForm(
                request.POST, dataset_list=ds_list)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_afp_volume.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            if 'new_folder' in cd and cd['new_folder']:
                try:
                    os.mkdir('%s/%s' % (cd['path'], cd['new_folder']))
                    audit_str = 'Created new directory "%s" in "%s"' % (
                        cd['new_folder'], cd['path'])
                    audit.audit("create_dir", audit_str, request)
                    cd['path'] = '%s/%s' % (cd['path'], cd['new_folder'])
                except Exception, e:
                    raise Exception('Error creating subfolder %s : %s' % (
                        cd['new_folder'], str(e)))
            result, err = afp.create_volume(cd['name'], cd['path'])
            if err:
                raise Exception(err)

            audit_str = 'Created AFP volume named "%s" with path  %s' % (cd['name'], cd['path'])
            audit.audit("create_afp_volume", audit_str, request)
            return django.http.HttpResponseRedirect('/storage_access/view_afp_volumes?ack=created')
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Create an AFP volume '
        return_dict['tab'] = 'view_afp_volumes_tab'
        return_dict["error"] = 'Error creating an AFP volume '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
