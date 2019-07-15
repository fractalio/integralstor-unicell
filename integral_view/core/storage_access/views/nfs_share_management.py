import django
import django.template

from integralstor import nfs, audit, django_utils, zfs

import integral_view
from integral_view.core.storage_access.forms import nfs_shares_forms

import os


def view_nfs_shares(request):
    return_dict = {}
    try:
        exports_list, err = nfs.load_exports_list()
        if not exports_list and err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "saved":
                return_dict['ack_message'] = "NFS Export information successfully updated"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "NFS Export successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "NFS Export successfully deleted"
        return_dict["exports_list"] = exports_list
        template = "view_nfs_shares.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'NFS shares'
        return_dict['tab'] = 'view_nfs_shares_tab'
        return_dict["error"] = 'Error loading NFS shares'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_nfs_share(request):
    return_dict = {}
    try:
        path = request.GET['path']
        template = 'logged_in_error.html'
        if not path:
            raise Exception("No path specified. Please use the menus.")
        exports_list, err = nfs.load_exports_list()
        if err:
            raise Exception(err)
        if not exports_list:
            raise Exception('Error loading NFS exports information')
        found = False
        for e in exports_list:
            if e['path'] == path:
                found = True
                return_dict['share_info'] = e
                break
        if not found:
            raise Exception("Requested share not found.")

        template = "view_nfs_share.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'View NFS share details'
        return_dict['tab'] = 'view_nfs_shares_tab'
        return_dict["error"] = 'Error viewing NFS share details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_nfs_share(request):

    return_dict = {}
    try:
        if request.method == "GET":
            # Return the conf page
            path = request.GET["path"]
            return_dict["path"] = path
            return django.shortcuts.render_to_response("delete_nfs_share_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            path = request.POST["path"]
            #logger.debug("Delete share request for name %s"%name)
            result, err = nfs.delete_share(path)
            if err:
                raise Exception(err)

            audit_str = "Deleted NFS share %s" % path
            audit.audit("delete_nfs_share", audit_str, request)
            return django.http.HttpResponseRedirect('/storage_access/view_nfs_shares?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Remove NFS share '
        return_dict['tab'] = 'view_nfs_shares_tab'
        return_dict["error"] = 'Error removing NFS share'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_nfs_share(request):
    return_dict = {}
    try:
        if request.method == "GET":
            # Return the conf page
            path = request.GET["path"]
            d, err = nfs.get_share(path)
            if err:
                raise Exception(err)
            if not d:
                raise Exception(
                    'Could not find the specified share. Please use the menus.')
            initial = {}
            initial['path'] = d['path']
            if 'clients' in d:
                client_list = []
                for client in d['clients']:
                    client_list.append(client['name'])
                    if 'options' in client:
                        for option in client['options']:
                            if option == 'ro':
                                initial['readonly'] = True
                            elif option == 'root_squash':
                                initial['root_squash'] = True
                            elif option == 'all_squash':
                                initial['all_squash'] = True
                initial['clients'] = ','.join(client_list)
            form = nfs_shares_forms.ShareForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_nfs_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = nfs_shares_forms.ShareForm(request.POST)
            path = request.POST["path"]
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_nfs_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result, err = nfs.save_share(cd)
            if err:
                raise Exception(err)

            audit_str = "Edited NFS share %s" % path
            audit.audit("edit_nfs_share", audit_str, request)
            return django.http.HttpResponseRedirect('/storage_access/view_nfs_shares?ack=saved')
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Modify a NFS share '
        return_dict['tab'] = 'view_nfs_shares_tab'
        return_dict["error"] = 'Error modifying a NFS share'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_nfs_share(request):
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
            request, ['dataset', 'path'])
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
            form = nfs_shares_forms.CreateShareForm(
                initial=initial, dataset_list=ds_list)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_nfs_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = nfs_shares_forms.CreateShareForm(
                request.POST, dataset_list=ds_list)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_nfs_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
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
            result, err = nfs.save_share(cd, True)
            if err:
                raise Exception(err)

            audit_str = "Created NFS share %s" % cd['path']
            audit.audit("create_nfs_share", audit_str, request)
            return django.http.HttpResponseRedirect('/storage_access/view_nfs_shares?ack=created')
    except Exception, e:
        return_dict['base_template'] = "storage_access_base.html"
        return_dict["page_title"] = 'Create a NFS share '
        return_dict['tab'] = 'view_nfs_shares_tab'
        return_dict["error"] = 'Error creating a NFS share'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
