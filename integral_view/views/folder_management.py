import django
import django.template
from django.http import HttpResponse

import os
import pwd
import grp
import stat
import shutil
import time
import json

import integral_view
from integral_view.forms import samba_shares_forms, folder_management_forms

from integralstor import acl, cifs, local_users, nfs, audit, django_utils, file_processing, zfs, config


def _sticky_bit_enabled(path):
    sticky_bit = False
    try:
        s = os.stat(path)
        sticky_bit = ((s.st_mode & stat.S_ISVTX) == stat.S_ISVTX)
    except Exception, e:
        return False, 'Error checking for sticky bit for folder %s : %s' % (path, str(e))
    else:
        return sticky_bit, None


def _has_subdirs(full_path):
    subdirs = False
    try:
        contents = os.listdir(full_path)
        for content in contents:
            if os.path.isdir('%s/%s' % (full_path, content)):
                subdirs = True
    except Exception, e:
        return False, 'Error checking for subdirs : %s' % str(e)
    else:
        return subdirs, None


def _get_subdirs(full_path):
    subdirs = []
    try:
        contents = os.listdir(full_path)
        for content in contents:
            if os.path.isdir('%s/%s' % (full_path, content)):
                subdirs.append(content)
    except Exception, e:
        return None, 'Error getting subdirs : %s' % str(e)
    else:
        return subdirs, None


def _owner_readable(st):
    return bool(st.st_mode & stat.S_IRUSR)


def _owner_writeable(st):
    return bool(st.st_mode & stat.S_IWUSR)


def _owner_executeable(st):
    return bool(st.st_mode & stat.S_IXUSR)


def _group_readable(st):
    return bool(st.st_mode & stat.S_IRGRP)


def _group_writeable(st):
    return bool(st.st_mode & stat.S_IWGRP)


def _group_executeable(st):
    return bool(st.st_mode & stat.S_IXGRP)


def _other_readable(st):
    return bool(st.st_mode & stat.S_IROTH)


def _other_writeable(st):
    return bool(st.st_mode & stat.S_IWOTH)


def _other_executeable(st):
    return bool(st.st_mode & stat.S_IXOTH)


def view_dir_contents(request):
    dir_dict_list = []
    first = request.GET.get("first")
    if first:
        src = request.GET['from']
        if src == 'dataset':
            if 'dataset_name' not in request.GET:
                raise Exception('No dataset supplied')
            ds_name = request.GET['dataset_name']
            mnt_pnt = '/%s' % ds_name
            dirs = []
            if os.path.isdir(mnt_pnt):
                dirs = os.listdir(mnt_pnt)
            if not dirs:
                d_dict = {'id': mnt_pnt, 'text': '/', 'icon': 'fa',
                          'children': False, 'data': {'dir': mnt_pnt}, 'parent': "#"}
                dir_dict_list.append(d_dict)
            for dir in dirs:
                if os.path.isdir('%s/%s' % (mnt_pnt, dir)):
                    subdirs, err = _has_subdirs('%s/%s' % (mnt_pnt, dir))
                    if err:
                        raise Exception(err)
                    #subdirs = os.listdir('%s/%s'%(mnt_pnt, dir))
                    if subdirs:
                        d_dict = {'id': '%s/%s' % (mnt_pnt, dir), 'text': dir, 'icon': 'fa fa-angle-right',
                                  'children': True, 'data': {'dir': '%s/%s' % (mnt_pnt, dir)}, 'parent': "#"}
                    else:
                        d_dict = {'id': '%s/%s' % (mnt_pnt, dir), 'text': dir, 'icon': 'fa', 'children': False, 'data': {
                            'dir': '%s/%s' % (mnt_pnt, dir)}, 'parent': "#"}
                    dir_dict_list.append(d_dict)
        elif src == 'pool':
            if 'pool_name' not in request.GET:
                pools, err = zfs.get_pools()
                if err:
                    raise Exception(err)
                p = pools[0]
            else:
                pool = request.GET['pool_name']
                p, err = zfs.get_pool(pool)
                if err:
                    raise Exception(err)
            dir_dict_list = []
            for ds in p["datasets"]:
                if ds['properties']['type']['value'] == 'filesystem':
                    mnt_pnt = ds['properties']['mountpoint']['value']
                    #subdirs = os.listdir(mnt_pnt)
                    subdirs, err = _has_subdirs(mnt_pnt)
                    if err:
                        raise Exception(err)
                    name = os.path.basename(mnt_pnt)
                    if subdirs:
                        d_dict = {'id': mnt_pnt, 'text': name, 'icon': 'fa fa-angle-right',
                                  'children': True, 'data': {'dir': mnt_pnt}, 'parent': "#"}
                    else:
                        d_dict = {'id': mnt_pnt, 'text': name, 'icon': 'fa', 'children': False, 'data': {
                            'dir': mnt_pnt}, 'parent': "#"}
                    dir_dict_list.append(d_dict)
    else:
        if 'dir' in request.GET and request.GET['dir'] != '/':
            path = request.GET['dir']
        else:
            path = request.GET.get("pool_name")
        dirs = os.listdir(path)
        # print 'path ', path
        for d in dirs:
            # print 'dir', d
            true = True
            if os.path.isdir(path + "/" + d):
                parent = path
                subdirs, err = _has_subdirs('%s/%s' % (path, d))
                if err:
                    raise Exception(err)
                '''
        contents = os.listdir('%s/%s'%(path, d))
        subdirs = False
        for content in contents:
          if os.path.isdir('%s/%s/%s'%(path,d, content)):
            subdirs = True
            break
        '''
                # print 'subdirs ', subdirs
                if subdirs:
                    # print 'yes'
                    d_dict = {'id': path + "/" + d, 'text': d, 'icon': 'fa fa-angle-right',
                              'children': True, 'data': {'dir': path + "/" + d}, 'parent': parent}
                else:
                    # print 'no'
                    d_dict = {'id': path + "/" + d, 'text': d, 'icon': 'fa',
                              'children': False, 'data': {'dir': path + "/" + d}, 'parent': parent}
                dir_dict_list.append(d_dict)
    return HttpResponse(json.dumps(dir_dict_list), content_type='application/json')


def create_aces(request):
    return_dict = {}
    try:
        for_share = False
        share_index = None
        share_name = None
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['for', 'path', 'share_index', 'share_name'])
        if err:
            raise Exception(err)

        if 'for' in req_ret and req_ret['for'] == 'share':
            for_share = True
        if for_share:
            return_dict['base_template'] = "shares_base.html"
            return_dict['tab'] = 'view_cifs_shares_tab'
        else:
            return_dict['base_template'] = "storage_base.html"
            return_dict['tab'] = 'dir_permissions_tab'

        if 'path' not in req_ret:
            raise Exception(
                'Invalid request, please use the menus.')
        path = req_ret['path']
        return_dict["path"] = path

        aces, err = acl.get_all_aces(path)
        if err:
            raise Exception(err)
        user_list, err = cifs.get_user_list()
        if err:
            raise Exception(err)
        group_list, err = cifs.get_group_list()
        if err:
            raise Exception(err)
        new_users, err = acl.get_new_ug_list(aces, user_list, 'user')
        if err:
            raise Exception(err)
        new_groups, err = acl.get_new_ug_list(aces, group_list, 'group')
        if err:
            raise Exception(err)
        return_dict['new_users'] = new_users
        return_dict['new_groups'] = new_groups

        if request.method == "GET":
            initial = {}
            initial['path'] = path
            if for_share:
                if 'share_index' not in req_ret or 'share_name' not in req_ret:
                    raise Exception('Invalid request. Please use the menus.')
                share_index = req_ret['share_index']
                share_name = req_ret['share_name']
                initial['share_index'] = share_index
                initial['share_name'] = share_name
                form = samba_shares_forms.AddShareAcesForm(
                    initial=initial, user_list=new_users, group_list=new_groups)
            else:
                form = folder_management_forms.AddAcesForm(
                    initial=initial, user_list=new_users, group_list=new_groups)
            return_dict["form"] = form
            if for_share:
                return django.shortcuts.render_to_response("create_cifs_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("create_dir_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if for_share:
                form = samba_shares_forms.AddShareAcesForm(
                    request.POST, user_list=new_users, group_list=new_groups)
            else:
                form = folder_management_forms.AddAcesForm(
                    request.POST, user_list=new_users, group_list=new_groups)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                users = cd['users']
                groups = cd['groups']
                recursive = cd['recursive']
                if for_share:
                    share_index = cd['share_index']
                    share_name = cd['share_name']
                ret, err = acl.create_ace_entries(
                    path, users, groups, recursive)
                if err:
                    raise Exception(err)
            else:
                if for_share:
                    return django.shortcuts.render_to_response("create_cifs_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))
                else:
                    return django.shortcuts.render_to_response("create_dir_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))

            audit_str = 'Added ACL entries : '
            for user in users:
                audit_str += '%s(user) ' % user
            for group in groups:
                audit_str += '%s(group) ' % group
            if for_share:
                audit_str += ', for CIFS share %s' % share_name
            else:
                audit_str += ', for path %s' % path
            audit.audit("add_aces", audit_str, request)
            if for_share:
                return django.http.HttpResponseRedirect('/view_cifs_share?access_mode=by_id&index=%s&ack=aces_added' % share_index)
            else:
                return django.http.HttpResponseRedirect('/view_dir_ownership_permissions?path=%s&ack=aces_added' % path)
    except Exception, e:
        return_dict["page_title"] = 'Add new  ACL entries'
        return_dict["error"] = 'Error adding new ACL entries'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_aces(request):
    return_dict = {}
    try:
        for_share = False
        share_index = None
        share_name = None
        path = None
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['for', 'path', 'share_index', 'share_name'])
        if err:
            raise Exception(err)
        if 'for' in req_ret and req_ret['for'] == 'share':
            for_share = True

        if for_share:
            return_dict['base_template'] = "shares_base.html"
            return_dict['tab'] = 'view_cifs_shares_tab'
        else:
            return_dict['base_template'] = "storage_base.html"
            return_dict['tab'] = 'dir_permissions_tab'

        if 'path' not in req_ret:
            raise Exception(
                'Invalid request, please use the menus.')
        if for_share:
            if 'share_index' not in req_ret or 'share_name' not in req_ret:
                raise Exception('Invalid request. Please use the menus.')
            share_index = req_ret['share_index']
            share_name = req_ret['share_name']
            return_dict["share_index"] = share_index
            return_dict["share_name"] = share_name

        path = req_ret['path']
        return_dict["path"] = path

        aces, err = acl.get_all_aces(path)
        if err:
            raise Exception(err)

        minimal_aces, err = acl.get_minimal_aces(aces)
        if err:
            raise Exception(err)

        user_list, err = acl.get_ug_aces(aces, None, 'user')
        if err:
            raise Exception(err)
        group_list, err = acl.get_ug_aces(aces, None, 'group')
        if err:
            raise Exception(err)

        if request.method == "GET":
            initial = {}
            initial["path"] = path
            if for_share:
                initial["share_index"] = share_index
                initial["share_name"] = share_name
                form = samba_shares_forms.EditShareAcesForm(
                    initial=initial, user_list=user_list, group_list=group_list)
            else:
                form = folder_management_forms.EditAcesForm(
                    initial=initial, user_list=user_list, group_list=group_list)
            return_dict["form"] = form

            for ace in minimal_aces:
                if ace[0] == 'user':
                    if ace[2][0] != '-':
                        form.initial['ou_r'] = True
                    if ace[2][1] != '-':
                        form.initial['ou_w'] = True
                    if ace[2][2] != '-':
                        form.initial['ou_x'] = True
                if ace[0] == 'group':
                    if ace[2][0] != '-':
                        form.initial['og_r'] = True
                    if ace[2][1] != '-':
                        form.initial['og_w'] = True
                    if ace[2][2] != '-':
                        form.initial['og_x'] = True
                if ace[0] == 'other':
                    if ace[2][0] != '-':
                        form.initial['ot_r'] = True
                    if ace[2][1] != '-':
                        form.initial['ot_w'] = True
                    if ace[2][2] != '-':
                        form.initial['ot_x'] = True
            user_form_fields = {}
            for user in user_list:
                user_name = user[2]
                user_form_fields[user_name] = (
                    form['user_%s_r' % user_name], form['user_%s_w' % user_name], form['user_%s_x' % user_name])
                if user[3][0] != '-':
                    form.initial['user_%s_r' % user_name] = True
                if user[3][1] != '-':
                    form.initial['user_%s_w' % user_name] = True
                if user[3][2] != '-':
                    form.initial['user_%s_x' % user_name] = True
            group_form_fields = {}
            for group in group_list:
                group_name = group[2]
                group_form_fields[group_name] = (
                    form['group_%s_r' % group_name], form['group_%s_w' % group_name], form['group_%s_x' % group_name])
                if group[3][0] != '-':
                    form.initial['group_%s_r' % group_name] = True
                if group[3][1] != '-':
                    form.initial['group_%s_w' % group_name] = True
                if group[3][2] != '-':
                    form.initial['group_%s_x' % group_name] = True

            return_dict['user_form_fields'] = user_form_fields
            return_dict['group_form_fields'] = group_form_fields

            if for_share:
                return django.shortcuts.render_to_response("update_cifs_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("update_dir_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))

        else:
            if for_share:
                form = samba_shares_forms.EditShareAcesForm(
                    request.POST, user_list=user_list, group_list=group_list)
            else:
                form = folder_management_forms.EditAcesForm(
                    request.POST, user_list=user_list, group_list=group_list)
            return_dict["form"] = form

            user_form_fields = {}
            for user in user_list:
                user_name = user[2]
                user_form_fields[user_name] = (
                    form['user_%s_r' % user_name], form['user_%s_w' % user_name], form['user_%s_x' % user_name])
            group_form_fields = {}
            for group in group_list:
                group_name = group[2]
                group_form_fields[group_name] = (
                    form['group_%s_r' % group_name], form['group_%s_w' % group_name], form['group_%s_x' % group_name])

            return_dict['user_form_fields'] = user_form_fields
            return_dict['group_form_fields'] = group_form_fields

            if form.is_valid():
                cd = form.cleaned_data
                if for_share:
                    share_index = cd['share_index']
                    share_name = cd['share_name']
                ret, err = acl.update_ace_entries(path, cd)
                if err:
                    raise Exception(err)
            else:
                if for_share:
                    return django.shortcuts.render_to_response("update_cifs_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))
                else:
                    return django.shortcuts.render_to_response("update_dir_aces.html", return_dict, context_instance=django.template.context.RequestContext(request))

            if for_share:
                audit_str = 'Modified ACL entries for CIFS share %s: ' % share_name
            else:
                audit_str = 'Modified ACL entries for directory %s: ' % path
            audit.audit("edit_aces", audit_str, request)
            if for_share:
                return django.http.HttpResponseRedirect('/view_cifs_share?access_mode=by_id&index=%s&ack=aces_modified' % share_index)
            else:
                return django.http.HttpResponseRedirect('/view_dir_ownership_permissions?path=%s&ack=aces_modified' % path)
    except Exception, e:
        return_dict["page_title"] = 'Modify ACL entries'
        return_dict["error"] = 'Error modifying ACL entries'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_ace(request):

    return_dict = {}
    try:
        for_share = False
        name = None
        share_index = None
        share_name = None
        ace_type = None

        req_ret, err = django_utils.get_request_parameter_values(
            request, ['for', 'path', 'name', 'type', 'share_index', 'share_name', 'recursive'])
        if err:
            raise Exception(err)
        if 'for' in req_ret and req_ret['for'] == 'share':
            for_share = True
        if for_share:
            return_dict['base_template'] = "shares_base.html"
            return_dict['tab'] = 'view_cifs_shares_tab'
        else:
            return_dict['base_template'] = "storage_base.html"
            return_dict['tab'] = 'dir_permissions_tab'

        if ('path' and 'name' and 'type') not in req_ret:
            raise Exception(
                'Invalid request, please use the menus.')
        if for_share:
            if 'share_name' not in req_ret or 'share_index' not in req_ret:
                raise Exception('Invalid request. Please use the menus.')
            share_name = req_ret['share_name']
            share_index = req_ret['share_index']
            return_dict["share_name"] = share_name
            return_dict["share_index"] = share_index

        path = req_ret['path']
        name = req_ret['name']
        ace_type = req_ret['type']
        return_dict["name"] = name
        return_dict["type"] = ace_type
        return_dict["path"] = path

        if request.method == "GET":
            # Return the conf page
            if for_share:
                return django.shortcuts.render_to_response("delete_cifs_ace_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
            else:
                return django.shortcuts.render_to_response("delete_dir_ace_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if 'recursive' in req_ret and req_ret['recursive']:
                recursive = True
            else:
                recursive = False
            ret, err = acl.delete_ace(path, name, ace_type, recursive)
            if err:
                raise Exception(err)

            if for_share:
                audit_str = "Removed ACL entry %s (%s) for CIFS share %s" % (
                    name, ace_type, share_name)
            else:
                audit_str = "Removed ACL entry %s (%s) for directory %s" % (
                    name, ace_type, path)
            audit.audit("delete_ace", audit_str, request)
            if for_share:
                return django.http.HttpResponseRedirect('/view_cifs_share?access_mode=by_id&index=%s&ack=ace_deleted' % share_index)
            else:
                return django.http.HttpResponseRedirect('/view_dir_ownership_permissions?path=%s&ack=ace_deleted' % path)
    except Exception, e:
        return_dict["page_title"] = 'Delete an ACL entry'
        return_dict["error"] = 'Error deleting an ACL entry'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_dir(request):
    return_dict = {}
    try:
        path = None
        if not "error" in return_dict:
            if "ack" in request.GET:
                if request.GET["ack"] == "ace_deleted":
                    return_dict['ack_message'] = "ACL entry successfully removed"
                elif request.GET["ack"] == "aces_added":
                    return_dict['ack_message'] = "ACL entries successfully added"
                elif request.GET["ack"] == "aces_modified":
                    return_dict['ack_message'] = "ACL entries successfully modified"

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'path'])
        if err:
            raise Exception(err)
        if 'path' not in req_ret:
            raise Exception(
                'Unspecified base directory. Please use the menus.')
        path = req_ret['path']
        try:
            stat_info = os.stat(path)
        except Exception, e:
            raise Exception(
                'Error accessing specified base directory : %s' % str(e))
        return_dict['path'] = path
        if request.method == "GET":
            # Set initial form values
            initial = {}
            initial['path'] = path
            form = folder_management_forms.CreateDirForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response('create_dir.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = folder_management_forms.CreateDirForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                dir_name = cd['dir_name']
                directory = path + "/" + dir_name
                if os.path.exists(directory):
                    raise Exception('The specified directory already exists')

                os.makedirs(directory)

                owner_dict, err = config.get_default_file_dir_owner()
                if err:
                    raise Exception(err)
                owner_uid, err = config.get_system_uid_gid(
                    owner_dict['user'], 'user')
                if err:
                    raise Exception(err)
                owner_gid, err = config.get_system_uid_gid(
                    owner_dict['group'], 'group')
                if err:
                    raise Exception(err)

                os.chown(directory, owner_uid, owner_gid)
                audit_str = "Created new directory '%s' in '%s'" % (
                    dir_name, path)
                audit.audit("create_dir", audit_str, request)
                return django.http.HttpResponseRedirect('/view_dir_manager/?ack=created_dir')
            else:
                return_dict['form'] = form
                return django.shortcuts.render_to_response('create_dir.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Create a directory'
        return_dict['tab'] = 'dir_permissions_tab'
        return_dict["error"] = 'Error creating directory'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_dir(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'path'])
        if err:
            raise Exception(err)
        if 'path' not in req_ret:
            raise Exception('Invalid request, please use the menus')
        path = req_ret['path']
        pools, err = zfs.get_pools()
        ds_list = []
        for pool in pools:
            if pool['properties']['mountpoint']['value'] == path:
                raise Exception(
                    'The selected directory is the mountpoint of a pool and so cannot be deleted.')
            for ds in pool["datasets"]:
                if ds['properties']['type']['value'] == 'filesystem':
                    if ds['properties']['mountpoint']['value'] == path:
                        raise Exception(
                            'The selected directory is the mountpoint of a dataset and so cannot be deleted.')
        if request.method == "GET":
            if 'path' not in request.GET:
                raise Exception('No directory specified')
            initial = {}
            initial['path'] = request.GET['path']
            form = folder_management_forms.DirForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response('delete_dir_conf.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = folder_management_forms.DirForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                path = cd['path']
                if not os.path.exists(path):
                    raise Exception('The specified directory does not exist!')

                if len(path.split("/")) < 2:
                    raise Exception(
                        'Cannot delete specified directory - Invalid path')

                # Need to also check if the path is a share or not. If share, dont delete again.
                # Checking NFS
                exports, err = nfs.load_exports_list()
                if exports:
                    for export in exports:
                        # print id(export["path"]),id(path)
                        if export["path"] == path:
                            raise Exception(
                                'Cannot delete the specified directory as it is path of an NFS share')

                shutil.rmtree(path, ignore_errors=True)
                audit_str = "Deleted directory '%s'" % path
                audit.audit("delete_dir", audit_str, request)

                return django.http.HttpResponseRedirect('/view_dir_manager/?ack=deleted_dir')
            else:
                raise Exception(
                    'Could not delete the specified directory as there was an error in the specified parameters.')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Delete a directory'
        return_dict['tab'] = 'dir_permissions_tab'
        return_dict["error"] = 'Error deleting directory'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_dir_listing(request):
    resp = ''
    try:
        if 'path' not in request.GET:
            raise Exception('No directory specified')

        path = request.GET['path']
        contents = os.listdir(path)
        subdirs, err = _get_subdirs(path)
        if err:
            raise Exception(err)

        files = (file for file in os.listdir(path)
                 if os.path.isfile(os.path.join(path, file)))

        #resp = '<html><body>'
        resp += '<table class="table table-striped">'
        resp += '<tr><th>Type</th><th>Name</th><th>Size</th><th>Modified at<th></tr>'
        for file in files:
            # print 'file', file
            size = os.path.getsize('%s/%s' % (path, file))
            mtime = time.ctime(os.path.getmtime('%s/%s' % (path, file)))
            resp += '<tr><td><i class="fa fa-file-o" aria-hidden="true"></i></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                file, size, mtime)
        for d in subdirs:
            # print 'dir ', d
            mtime = time.ctime(os.path.getmtime('%s/%s' % (path, d)))
            resp += '<tr><td><i class="fa fa-folder" aria-hidden="true"></i></td><td>%s</td><td>&nbsp;</td><td>%s</td></tr>' % (
                d, mtime)
        resp += '</table>'
        #resp += '</body></html>'
        # print 'resp ', resp
        return HttpResponse(resp, content_type='text/html')
    except Exception, e:
        print str(e)
        return HttpResponse('Error processing request : %s' % str(e), content_type='text/html')


def view_dir_manager(request):
    return_dict = {}
    try:
        if not "error" in return_dict:
            if "ack" in request.GET:
                if request.GET["ack"] == "ace_deleted":
                    return_dict['ack_message'] = "ACL entry successfully removed"
                elif request.GET["ack"] == "aces_added":
                    return_dict['ack_message'] = "ACL entries successfully added"
                elif request.GET["ack"] == "aces_modified":
                    return_dict['ack_message'] = "ACL entries successfully modified"
                elif request.GET["ack"] == "created_dir":
                    return_dict['ack_message'] = "Directory successfully created"
                elif request.GET["ack"] == "deleted_dir":
                    return_dict['ack_message'] = "Directory successfully deleted"
                elif request.GET["ack"] == "modified_ownership":
                    return_dict['ack_message'] = "Directory ownership successfully modified"

        initial = {}
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool'])
        if err:
            raise Exception(err)
        if 'pool' in req_ret:
            pool = req_ret['pool']
            initial['pool'] = pool

        pools, err = zfs.get_pools()
        pool_list = []
        for pool in pools:
            # print pool['pool_name']
            pool_list.append(pool['pool_name'])
        if not pool_list:
            raise Exception(
                'No ZFS pools available. Please create a pool and dataset before using the directory manager.')

        form = folder_management_forms.DirManagerForm1(
            initial=initial, pool_list=pool_list)
        return_dict["form"] = form
        return django.shortcuts.render_to_response('view_dir_manager.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Directory manager'
        return_dict['tab'] = 'dir_manager_tab'
        return_dict["error"] = 'Error loading directory manager'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_dir_ownership_permissions(request):
    return_dict = {}
    try:
        if not "error" in return_dict:
            if "ack" in request.GET:
                if request.GET["ack"] == "ace_deleted":
                    return_dict['ack_message'] = "ACL entry successfully removed"
                elif request.GET["ack"] == "aces_added":
                    return_dict['ack_message'] = "ACL entries successfully added"
                elif request.GET["ack"] == "aces_modified":
                    return_dict['ack_message'] = "ACL entries successfully modified"
                elif request.GET["ack"] == "modified_ownership":
                    return_dict['ack_message'] = "Directory ownership successfully modified"
                elif request.GET["ack"] == "modified_sticky_bit":
                    return_dict['ack_message'] = "Directory sticky bit settings successfully modified"

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'path'])
        if err:
            raise Exception(err)
        if 'path' not in req_ret:
            raise Exception('No directory specified. Please use the menus.')
        else:
            path = req_ret['path']

        return_dict['path'] = path
        try:
            stat_info = os.stat(path)
        except Exception, e:
            raise Exception('Error accessing specified path : %s' % str(e))

        uid = stat_info.st_uid
        gid = stat_info.st_gid
        try:
            username = pwd.getpwuid(uid)[0]
        except Exception, e:
            username = 'Unknown'
        try:
            grpname = grp.getgrgid(gid)[0]
        except Exception, e:
            grpname = 'Unknown'
        sticky_bit_enabled, err = _sticky_bit_enabled(path)
        if err:
            raise Exception(err)
        return_dict["user_name"] = username
        return_dict["grp_name"] = grpname
        return_dict["sticky_bit_enabled"] = sticky_bit_enabled

        aces, err = acl.get_all_aces(path)
        if err:
            raise Exception(err)
        minimal_aces, err = acl.get_minimal_aces(aces)
        if err:
            raise Exception(err)
        user_aces, err = acl.get_ug_aces(aces, None, 'user')
        if err:
            raise Exception(err)
        group_aces, err = acl.get_ug_aces(aces, None, 'group')
        if err:
            raise Exception(err)

        return_dict['aces'] = aces
        return_dict['minimal_aces'] = minimal_aces
        if user_aces:
            return_dict['user_aces'] = user_aces
        if group_aces:
            return_dict['group_aces'] = group_aces

        return django.shortcuts.render_to_response('view_dir_ownership_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Directory manager'
        return_dict['tab'] = 'dir_manager_tab'
        return_dict["error"] = 'Error loading directory ownership and permissions'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_dir_owner(request):
    return_dict = {}
    try:
        users, err = local_users.get_local_users()
        if err:
            raise Exception('Error retrieving local user list : %s' % err)
        if not users:
            raise Exception(
                'No local users seem to be created. Please create at least one local user before performing this operation.')

        groups, err = local_users.get_local_groups()
        if err:
            raise Exception('Error retrieving local group list : %s' % err)
        if not groups:
            raise Exception(
                'No local groups seem to be created. Please create at least one local group before performing this operation.')

        if request.method == "GET":
            if 'path' not in request.GET:
                raise Exception('Invalid request. Please use the menus.')
            path = request.GET['path']
            try:
                stat_info = os.stat(path)
            except Exception, e:
                raise Exception('Error accessing specified path : %s' % str(e))
            uid = stat_info.st_uid
            gid = stat_info.st_gid
            user_name = pwd.getpwuid(uid)[0]
            group_name = grp.getgrgid(gid)[0]

            initial = {}
            initial['path'] = path
            initial['uid'] = uid
            initial['gid'] = gid
            initial['user_name'] = user_name
            initial['group_name'] = group_name
            form = folder_management_forms.ModifyOwnershipForm(
                initial=initial, user_list=users, group_list=groups)
            return_dict["form"] = form
            return django.shortcuts.render_to_response('update_dir_ownership.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = folder_management_forms.ModifyOwnershipForm(
                request.POST, user_list=users, group_list=groups)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                os.chown(cd['path'], int(cd['uid']), int(cd['gid']))
                user_name = pwd.getpwuid(int(cd['uid']))[0]
                group_name = grp.getgrgid(int(cd['gid']))[0]
                audit_str = "Set owner user to %s and owner group to %s for directory %s" % (
                    user_name, group_name, cd["path"])
                audit.audit("modify_dir_owner", audit_str, request)
                return django.http.HttpResponseRedirect('/view_dir_ownership_permissions?path=%s&ack=modified_ownership' % cd['path'])
            else:
                return django.shortcuts.render_to_response('update_dir_ownership.html', return_dict, context_instance=django.template.context.RequestContext(request))

    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Modify directory ownership'
        return_dict['tab'] = 'dir_permissions_tab'
        return_dict["error"] = 'Error modifying directory ownership'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_dir_permissions(request):
    return_dict = {}
    try:
        if not "error" in return_dict:
            if "ack" in request.GET:
                if request.GET["ack"] == "ace_deleted":
                    return_dict['ack_message'] = "ACL entry successfully removed"
                elif request.GET["ack"] == "aces_added":
                    return_dict['ack_message'] = "ACL entries successfully added"
                elif request.GET["ack"] == "aces_modified":
                    return_dict['ack_message'] = "ACL entries successfully modified"
                elif request.GET["ack"] == "created_dir":
                    return_dict['ack_message'] = "Directory successfully created"
                elif request.GET["ack"] == "deleted_dir":
                    return_dict['ack_message'] = "Directory successfully deleted"
        users, err = local_users.get_local_users()
        if err:
            raise Exception('Error retrieving local user list : %s' % err)
        if not users:
            raise Exception(
                'No local users seem to be created. Please create at least one local user before performing this operation.')

        groups, err = local_users.get_local_groups()
        if err:
            raise Exception('Error retrieving local group list : %s' % err)
        if not groups:
            raise Exception(
                'No local groups seem to be created. Please create at least one local group before performing this operation.')

        pools, err = zfs.get_pools()
        ds_list = []
        for pool in pools:
            for ds in pool["datasets"]:
                if ds['properties']['type']['value'] == 'filesystem':
                    ds_list.append(ds["name"])
        if not ds_list:
            raise Exception(
                'No ZFS datasets available. Please create a dataset before creating shares.')

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'path'])
        if err:
            raise Exception(err)
        if 'path' not in req_ret:
            path = "/" + pools[0]["datasets"][0]["name"]
        else:
            path = req_ret['path']
        try:
            stat_info = os.stat(path)
        except Exception, e:
            raise Exception('Error accessing specified path : %s' % str(e))
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        username = pwd.getpwuid(uid)[0]
        grpname = grp.getgrgid(gid)[0]
        return_dict["username"] = username
        return_dict["grpname"] = grpname

        aces, err = acl.get_all_aces(path)
        if err:
            raise Exception(err)
        minimal_aces, err = acl.get_minimal_aces(aces)
        if err:
            raise Exception(err)
        user_aces, err = acl.get_ug_aces(aces, None, 'user')
        if err:
            raise Exception(err)
        group_aces, err = acl.get_ug_aces(aces, None, 'group')
        if err:
            raise Exception(err)

        return_dict['aces'] = aces
        return_dict['minimal_aces'] = minimal_aces
        if user_aces:
            return_dict['user_aces'] = user_aces
        if group_aces:
            return_dict['group_aces'] = group_aces

        return_dict['path'] = path
        return_dict["dataset"] = ds_list
        if request.method == "GET":
            # Shd be an edit request

            # Set initial form values
            initial = {}
            initial['path'] = path
            initial['owner_read'] = _owner_readable(stat_info)
            initial['owner_write'] = _owner_writeable(stat_info)
            initial['owner_execute'] = _owner_executeable(stat_info)
            initial['group_read'] = _group_readable(stat_info)
            initial['group_write'] = _group_writeable(stat_info)
            initial['group_execute'] = _group_executeable(stat_info)
            initial['other_read'] = _other_readable(stat_info)
            initial['other_write'] = _other_writeable(stat_info)
            initial['other_execute'] = _other_executeable(stat_info)
            if 'dataset' in request.GET:
                initial['dataset'] = request.GET['dataset']

            form = folder_management_forms.SetFileOwnerAndPermissionsForm(
                initial=initial, user_list=users, group_list=groups)

            return_dict["form"] = form
            return django.shortcuts.render_to_response('update_dir_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))

        elif request.method == "POST":
            path = request.POST.get("path")
            # Shd be an save request
            if request.POST.get("action") == "add_folder":
                folder_name = request.POST.get("new_folder_name")
                directory = path + "/" + folder_name
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    audit_str = "Creating %s" % directory
                    audit.audit("modify_dir_owner_permissions",
                                audit_str, request)
            elif request.POST.get("action") == "delete_folder":
                delete = "false"
                if len(path.split("/")) > 2:
                    delete = "true"
                # Need to also check if the path is a share or not. If share, dont delete again.
                # Checking NFS
                exports, err = nfs.load_exports_list()
                if exports:
                    for export in exports:
                        print id(export["path"]), id(path)
                        if export["path"] == path:
                            delete = "false"
                            break
                        else:
                            delete = "true"

                if delete:
                    print delete
                    # shutil.rmtree(path,ignore_errors=True)
                    audit_str = "Deleting directory %s" % path
                    audit.audit("modify_dir_owner_permissions",
                                audit_str, request)
                else:
                    raise Exception(
                        "Cannot delete folder. It is either a dataset of a share")
            else:
                form = folder_management_forms.SetFileOwnerAndPermissionsForm(
                    request.POST, user_list=users, group_list=groups)
                return_dict["form"] = form
                if form.is_valid():
                    cd = form.cleaned_data
                    ret, err = file_processing.update_dir_ownership_and_permissions(
                        cd)
                    if not ret:
                        if err:
                            raise Exception(err)
                        else:
                            raise Exception(
                                "Error setting directory ownership/permissions.")

                    audit_str = "Modified directory ownsership/permissions for %s" % cd["path"]
                    audit.audit("modify_dir_owner_permissions",
                                audit_str, request)

            return django.http.HttpResponseRedirect('/update_dir_permissions/?ack=set_permissions')

        else:
            return django.shortcuts.render_to_response('update_dir_permissions.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Modify ownership/permissions on a directory'
        return_dict['tab'] = 'dir_permissions_tab'
        return_dict["error"] = 'Error modifying directory ownership/permissions'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_sticky_bit(request):
    return_dict = {}
    try:

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'path'])
        if err:
            raise Exception(err)
        if 'path' not in req_ret:
            raise Exception('Invalid request. Please use the menus.')
        path = req_ret['path']

        sticky_bit_enabled, err = _sticky_bit_enabled(path)
        if err:
            raise Exception(err)

        if request.method == "GET":
            initial = {}
            initial['path'] = path
            initial['sticky_bit_enabled'] = sticky_bit_enabled
            form = folder_management_forms.ModifyStickyBitForm(initial=initial)
            return_dict["form"] = form
            return django.shortcuts.render_to_response('update_sticky_bit.html', return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = folder_management_forms.ModifyStickyBitForm(request.POST)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                s = os.stat(path)
                if cd['sticky_bit_enabled']:
                    audit_str = 'Enabled sticky bit '
                    if cd['recursive']:
                        audit_str += 'recursively '
                        for root, dirs, files in os.walk(path):
                            for target in dirs:
                                os.chmod('%s/%s' % (root, target),
                                         (s.st_mode | stat.S_ISVTX))
                    os.chmod(path, (s.st_mode | stat.S_ISVTX))
                    audit_str += 'for path %s' % path
                    # print audit_str
                else:
                    audit_str = 'Disabled sticky bit '
                    if cd['recursive']:
                        audit_str += 'recursively '
                        for root, dirs, files in os.walk(path):
                            for target in dirs:
                                os.chmod('%s/%s' % (root, target),
                                         (s.st_mode & ~stat.S_ISVTX))
                    os.chmod(path, (s.st_mode & ~stat.S_ISVTX))
                    audit_str += 'for path %s' % path
                    # print audit_str
                audit.audit("modify_dir_sticky_bit", audit_str, request)
                return django.http.HttpResponseRedirect('/view_dir_ownership_permissions?path=%s&ack=modified_sticky_bit' % cd['path'])
            else:
                return django.shortcuts.render_to_response('update_dir_ownership.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Modify directory sticky bit settings'
        return_dict['tab'] = 'dir_permissions_tab'
        return_dict["error"] = 'Error modifying directory sticky bit settings'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
