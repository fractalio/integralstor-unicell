import django
import django.template

from integralstor_utils import zfs, audit, ramdisk, config, command, db
from integralstor_utils import cifs as common_cifs, django_utils
from integralstor import nfs, local_users, iscsi_stgt, system_info

from integral_view.forms import zfs_forms


def view_zfs_pools(request):
    return_dict = {}
    try:
        template = "view_zfs_pools.html"
        pool_list, err = zfs.get_pools()
        if err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "saved":
                return_dict['ack_message'] = "ZFS pool information successfully updated"
            elif request.GET["ack"] == "expanded_pool":
                return_dict['ack_message'] = "ZFS pool successfully expanded"
            elif request.GET["ack"] == "pool_exported":
                return_dict['ack_message'] = "ZFS pool successfully exported"
            elif request.GET["ack"] == "imported_pool":
                return_dict['ack_message'] = "ZFS pool successfully imported"
            elif request.GET["ack"] == "set_quota":
                return_dict['ack_message'] = "ZFS quota successfully set"
            elif request.GET["ack"] == "removed_quota":
                return_dict['ack_message'] = "ZFS quota successfully removed"
            elif request.GET["ack"] == "created_pool":
                return_dict['ack_message'] = "ZFS pool successfully created"
            elif request.GET["ack"] == "set_permissions":
                return_dict['ack_message'] = "Directory ownership/permissions successfully set"
            elif request.GET["ack"] == "created_dataset":
                return_dict['ack_message'] = "ZFS dataset successfully created"
            elif request.GET["ack"] == "created_zvol":
                return_dict['ack_message'] = "ZFS block device volume successfully created"
            elif request.GET["ack"] == "pool_deleted":
                return_dict['ack_message'] = "ZFS pool successfully destroyed"
            elif request.GET["ack"] == "pool_scrub_initiated":
                return_dict['ack_message'] = "ZFS pool scrub successfully initiated"
            elif request.GET["ack"] == "dataset_deleted":
                return_dict['ack_message'] = "ZFS dataset successfully destroyed"
            elif request.GET["ack"] == "zvol_deleted":
                return_dict['ack_message'] = "ZFS block device volume successfully destroyed"
            elif request.GET["ack"] == "slog_deleted":
                return_dict['ack_message'] = "ZFS write cache successfully removed"
            elif request.GET["ack"] == "changed_slog":
                return_dict['ack_message'] = "ZFS pool write cache successfully set"
            elif request.GET["ack"] == "added_spares":
                return_dict['ack_message'] = "Successfully added spare disks to the pool"
            elif request.GET["ack"] == "removed_spare":
                return_dict['ack_message'] = "Successfully removed a spare disk from the pool"
            elif request.GET["ack"] == "replication_success":
                return_dict['ack_message'] = "Replication Successful"
            elif request.GET["ack"] == "replication_error":
                return_dict['ack_message'] = "Replication Failed"
        return_dict["pool_list"] = pool_list
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pools'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error loading ZFS pools'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_pool(request):
    return_dict = {}
    try:
        template = 'logged_in_error.html'
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'view', 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")

        if "ack" in request.GET:
            if request.GET["ack"] == "saved":
                return_dict['ack_message'] = "ZFS pool information successfully updated"
            elif request.GET["ack"] == "expanded_pool":
                return_dict['ack_message'] = "ZFS pool successfully expanded"
            elif request.GET["ack"] == "set_quota":
                return_dict['ack_message'] = "ZFS quota successfully set"
            elif request.GET["ack"] == "removed_quota":
                return_dict['ack_message'] = "ZFS quota successfully removed"
            elif request.GET["ack"] == "set_permissions":
                return_dict['ack_message'] = "Directory ownership/permissions successfully set"
            elif request.GET["ack"] == "created_dataset":
                return_dict['ack_message'] = "ZFS dataset successfully created"
            elif request.GET["ack"] == "created_zvol":
                return_dict['ack_message'] = "ZFS block device volume successfully created"
            elif request.GET["ack"] == "pool_scrub_initiated":
                return_dict['ack_message'] = "ZFS pool scrub successfully initiated"
            elif request.GET["ack"] == "dataset_deleted":
                return_dict['ack_message'] = "ZFS dataset successfully destroyed"
            elif request.GET["ack"] == "zvol_deleted":
                return_dict['ack_message'] = "ZFS block device volume successfully destroyed"
            elif request.GET["ack"] == "slog_deleted":
                return_dict['ack_message'] = "ZFS write cache successfully removed"
            elif request.GET["ack"] == "l2arc_deleted":
                return_dict['ack_message'] = "ZFS read cache successfully removed"
            elif request.GET["ack"] == "changed_slog":
                return_dict['ack_message'] = "ZFS pool write cache successfully set"
            elif request.GET["ack"] == "changed_l2arc":
                return_dict['ack_message'] = "ZFS pool read cache successfully set"
            elif request.GET["ack"] == "added_spares":
                return_dict['ack_message'] = "Successfully added spare disks to the pool"
            elif request.GET["ack"] == "removed_spare":
                return_dict['ack_message'] = "Successfully removed a spare disk from the pool"
            elif request.GET["ack"] == "clear_zfs_pool":
                return_dict['ack_message'] = "ZFS pool errors successfully cleared"
        if 'view' in req_ret:
            view = req_ret['view']
        else:
            view = 'basic'

        pool_name = req_ret['name']
        pool, err = zfs.get_pool(pool_name)

        if err:
            raise Exception(err)
        elif not pool:
            raise Exception("Specified pool not found")

        if view == 'components':
            num_free_disks_for_spares, err = zfs.get_free_disks_for_spares(
                pool_name)
            if err:
                raise Exception(err)

            num_free_disks_for_cache, err = zfs.get_free_disks(
                disk_type='flash')
            if err:
                raise Exception(err)

            (can_expand, new_pool_type), err = zfs.can_expand_pool(pool_name)

            return_dict['can_expand_pool'] = can_expand
            return_dict['num_free_disks_for_spares'] = num_free_disks_for_spares
            return_dict['num_free_disks_for_cache'] = num_free_disks_for_cache

        if view == 'quotas':
            quotas, err = zfs.get_all_quotas(pool_name)
            if err:
                raise Exception(err)
            return_dict['quotas'] = quotas

        return_dict['pool'] = pool
        return_dict['pool_name'] = pool_name

        if view == 'basic':
            template = "view_zfs_pool.html"
        elif view == 'components':
            template = "view_zfs_pool_components.html"
        elif view == 'datasets_and_zvols':
            template = "view_zfs_pool_datasets_zvols.html"
        elif view == 'quotas':
            template = "view_zfs_pool_quotas.html"

        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pool details'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error loading ZFS pool details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_zfs_quota(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['path', 'path_type', 'ug_type', 'pool_name'])
        if err:
            raise Exception(err)
        if ('path' and 'path_type' and 'pool_name' and 'ug_type') not in req_ret:
            raise Exception("Malformed request. Please use the menus")
        path_type = req_ret['path_type']
        path = req_ret['path']
        ug_type = req_ret['ug_type']
        pool_name = req_ret['pool_name']
        if ug_type not in ['user', 'group']:
            raise Exception("Malformed request. Please use the menus")
        if ug_type == 'user':
            ugl, err = local_users.get_local_users()
        else:
            ugl, err = local_users.get_local_groups()
        if err:
            raise Exception(err)
        ug_list = []
        for ug in ugl:
            if ug_type == 'user':
                ug_list.append(ug['username'])
            else:
                ug_list.append(ug['grpname'])
        return_dict["path"] = path
        return_dict["pool_name"] = pool_name
        return_dict["path_type"] = path_type
        return_dict["ug_type"] = ug_type
        if request.method == "GET":
            form = zfs_forms.QuotaForm(user_group_list=ug_list, initial={
                                       'ug_type': ug_type, 'path': path})
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_zfs_quota.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.QuotaForm(request.POST, user_group_list=ug_list)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_zfs_quota.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            if cd['ug_type'] == 'user':
                user = True
            else:
                user = False
            ret, err = zfs.update_quota(
                cd['path'], cd['ug_name'], '%d%s' % (cd['size'], cd['unit']), user)
            if err:
                raise Exception(err)
            audit_str = "Set ZFS quota for %s %s for %s to %s%s" % (
                cd['ug_type'], cd['ug_name'], cd['path'], cd['size'], cd['unit'])
            audit.audit("set_zfs_quota", audit_str, request)
            if path_type == 'pool':
                return django.http.HttpResponseRedirect('/view_zfs_pool?ack=set_quota&name=%s&view=quotas' % pool_name)
            else:
                return django.http.HttpResponseRedirect('/view_zfs_dataset?ack=set_quota&name=%s' % path)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Setting ZFS quota'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error setting ZFS quota'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_quota(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['path', 'path_type', 'ug_type', 'ug_name', 'pool_name'])
        if err:
            raise Exception(err)
        if ('path' and 'path_type' and 'ug_name' and 'ug_type' and 'pool_name') not in req_ret:
            raise Exception("Malformed request. Please use the menus")
        path_type = req_ret['path_type']
        path = req_ret['path']
        ug_type = req_ret['ug_type']
        ug_name = req_ret['ug_type']
        pool_name = req_ret['pool_name']

        return_dict["path"] = path
        return_dict["pool_name"] = pool_name
        return_dict["path_type"] = path_type
        return_dict["ug_name"] = ug_name
        return_dict["ug_type"] = ug_type
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_quota_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if ug_type == 'user':
                user = True
            else:
                user = False
            result, err = zfs.update_quota(path, ug_name, 'none', user)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Removed ZFS quota for %s %s for %s" % (
                ug_type, ug_name, path)
            audit.audit("remove_zfs_quota", audit_str, request)
            if path_type == 'pool':
                return django.http.HttpResponseRedirect('/view_zfs_pool?ack=removed_quota&name=%s&view=quotas' % pool_name)
            else:
                return django.http.HttpResponseRedirect('/view_zfs_dataset?ack=removed_quota&name=%s' % path)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Removing ZFS quota'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing ZFS quota'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def export_zfs_pool(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool_name'])
        if err:
            raise Exception(err)
        if 'pool_name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool_name']

        return_dict["pool_name"] = pool_name
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("export_zfs_pool_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.export_pool(pool_name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = 'Exported ZFS pool "%s"' % pool_name
            audit.audit("export_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pools?ack=pool_exported')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Export ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error exporting ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def import_all_zfs_pools(request):
    return_dict = {}
    try:
        template = 'logged_in_error.html'

        output, err = command.get_command_output('zpool import -maf')
        if err:
            raise Exception(err)

        return_dict['output'] = output

        template = "import_pool_from_disks_result.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Import all ZFS pools'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error importing all ZFS pool(s) from disks'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def import_zfs_pool(request):
    return_dict = {}
    try:
        if request.method == 'GET':
            form = zfs_forms.ImportPoolForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response("import_zfs_pool.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.ImportPoolForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("import_zfs_pool.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            ret, err = zfs.import_pool(cd['name'])
            if err:
                raise Exception(err)
            audit_str = 'Imported a ZFS pool named "%s" ' % (cd['name'])
            audit.audit("import_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pools?ack=imported_pool')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Import a ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error importing a specific ZFS pool from disks'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_zfs_pool(request):
    return_dict = {}
    try:

        free_disks, err = zfs.get_free_disks()
        if err:
            raise Exception(err)

        if not free_disks or len(free_disks) < 2:
            raise Exception(
                'There are insufficient unused disks available to create a pool')

        pool_types = []
        if len(free_disks) >= 2:
            pool_types.append(('mirror', 'MIRROR'))
        if len(free_disks) >= 3:
            pool_types.append(('raid5', 'RAID-5'))
        if len(free_disks) >= 4:
            pool_types.append(('raid6', 'RAID-6'))
            pool_types.append(('raid10', 'RAID-10'))
        if len(free_disks) >= 6:
            pool_types.append(('raid50', 'RAID-50'))
        if len(free_disks) >= 8:
            pool_types.append(('raid60', 'RAID-60'))

        if request.method == "GET":
            # Return the conf page
            form = zfs_forms.CreatePoolForm(pool_types=pool_types, num_free_disks=len(
                free_disks), initial={'num_disks': len(free_disks)})
            return_dict['form'] = form
            return_dict['num_disks'] = len(free_disks)
            return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.CreatePoolForm(
                request.POST, pool_types=pool_types, num_free_disks=len(free_disks))
            return_dict['form'] = form
            return_dict['num_disks'] = len(free_disks)
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_zfs_pool.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            # print cd
            vdev_list = None
            if cd['pool_type'] in ['raid5', 'raid6']:
                vdev_list, err = zfs.create_pool_data_vdev_list(
                    cd['pool_type'], disk_type=cd['disk_type'], num_raid_disks=cd['num_raid_disks'])
            elif cd['pool_type'] == 'raid10':
                vdev_list, err = zfs.create_pool_data_vdev_list(
                    cd['pool_type'], disk_type=cd['disk_type'], stripe_width=cd['stripe_width'])
            elif cd['pool_type'] in ['raid50', 'raid60']:
                vdev_list, err = zfs.create_pool_data_vdev_list(
                    cd['pool_type'], disk_type=cd['disk_type'], num_raid_disks=cd['num_raid_disks'], stripe_width=cd['stripe_width'])
            else:
                vdev_list, err = zfs.create_pool_data_vdev_list(
                    cd['pool_type'], disk_type=cd['disk_type'])
            if err:
                raise Exception(err)
            # print 'vdevlist', vdev_list
            result, err = zfs.create_pool(
                cd['name'], cd['pool_type'], vdev_list, dedup=cd['dedup'])
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Created a ZFS pool named %s of type %s" % (
                cd['name'], cd['pool_type'])
            audit.audit("create_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pools?ack=created_pool')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pool creation'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error creating a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def expand_zfs_pool(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool_name'])
        if err:
            raise Exception(err)
        if 'pool_name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool_name']
        if request.method == 'GET':
            (can_expand, new_pool_type), err = zfs.can_expand_pool(pool_name)
            if err:
                raise Exception(err)
            if not can_expand:
                raise Exception('Cannot expand the specified pool.')
            return_dict['new_pool_type'] = new_pool_type
            return_dict['pool_name'] = pool_name
            return django.shortcuts.render_to_response("expand_zfs_pool_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = zfs.expand_pool(pool_name)
            if err:
                raise Exception(err)
            audit_str = "Expanded the ZFS pool named %s" % pool_name
            audit.audit("expand_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=expanded_pool&name=%s&view=components' % pool_name)

    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pool expansion'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error expanding a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def scrub_zfs_pool(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['name']
        return_dict["name"] = name
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("scrub_zfs_pool_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.scrub_pool(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "ZFS pool scrub initiated on pool %s" % name
            audit.audit("scrub_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=pool_scrub_initiated&name=%s' % name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pool scrub'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error scrubbing ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def clear_zfs_pool(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool_name'])
        if err:
            raise Exception(err)
        if 'pool_name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['pool_name']
        return_dict["name"] = name
        if request.method == "GET":
            return django.http.HttpResponseRedirect('/view_zfs_pools/')
        else:
            result, err = zfs.clear_pool(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Cleared ZFS pool errors on pool %s" % name
            audit.audit("clear_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=clear_zfs_pool&name=%s' % name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS pool clear'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error clearing ZFS pool errors'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_pool(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['name']
        nfs_shares, err = nfs.get_shares_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        cifs_shares, err = common_cifs.get_shares_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        luns, err = iscsi_stgt.get_luns_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        if nfs_shares or cifs_shares or luns:
            elements = []
            if nfs_shares:
                shl = []
                for sh in nfs_shares:
                    shl.append(sh['path'])
                elements .append('NFS share(s) : %s' % ' , '.join(shl))
            if cifs_shares:
                # print '1'
                shl = []
                for sh in cifs_shares:
                    shl.append(sh['name'])
                elements .append('CIFS share(s) : %s' % ' , '.join(shl))
                # print '2'
            if luns:
                shl = []
                for sh in luns:
                    # print sh
                    shl.append(sh['path'][9:])
                elements .append('ISCSI LUN(s) : %s' % ' , '.join(shl))
                # print '3'
            raise Exception(
                'The pool cannot be deleted as the following components exist on this pool : %s. Please delete them first before deleting the pool.' % ' , '.join(elements))
        return_dict["name"] = name
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_pool_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.delete_pool(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Deleted ZFS pool %s" % name
            audit.audit("delete_zfs_pool", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pools?ack=pool_deleted')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Remove a ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_zfs_slog(request):
    return_dict = {}
    try:

        template = 'logged_in_error.html'

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool'])
        if err:
            raise Exception(err)
        if 'pool' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool']

        pool, err = zfs.get_pool(pool_name)

        if err:
            raise Exception(err)
        elif not pool:
            raise Exception(
                "Error loading ZFS storage information : Specified pool not found")

        slog = None
        if not pool['config']['logs']:
            slog = None
        else:
            kids = pool['config']['logs']['root']['children']
            if len(kids) == 1 and 'ramdisk' in kids[0]:
                slog = 'ramdisk'
                rdisk, err = ramdisk.get_ramdisk_info(
                    '/mnt/ramdisk_%s' % pool_name)
                if err:
                    raise Exception(err)
                elif not rdisk:
                    raise Exception(
                        "Could not determine the configuration for the RAM disk for the specified ZFS pool")
                ramdisk_size = rdisk['size'] / 1024
            else:
                # For now pass but we need to code this to read the component
                # disk ID!!!!!!!!!!!!1
                slog = 'flash'
        free_disks, err = zfs.get_free_disks(disk_type='flash')
        # print free_disks
        if err:
            raise Exception(err)

        if request.method == "GET":
            # Return the conf page

            initial = {}
            initial['pool'] = pool_name
            initial['slog'] = slog
            if slog == 'ramdisk':
                initial['ramdisk_size'] = ramdisk_size

            form = zfs_forms.SlogForm(initial=initial, free_disks=free_disks)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_zfs_slog.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.SlogForm(request.POST, free_disks=free_disks)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_zfs_slog.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            # print cd
            if cd['slog'] == 'ramdisk':
                if ((cd['slog'] == slog) and (cd['ramdisk_size'] != ramdisk_size)) or (cd['slog'] != slog):
                    # Changed to ramdisk or ramdisk parameters changed so
                    # destroy and recreate
                    oldramdisk, err = ramdisk.get_ramdisk_info(
                        '/mnt/ramdisk_%s' % cd['pool'])
                    if err:
                        raise Exception(err)
                    if oldramdisk:
                        result, err = ramdisk.delete_ramdisk(
                            '/mnt/ramdisk_%s' % cd['pool'], cd['pool'])
                        if err:
                            raise Exception(err)
                        result, err = zfs.delete_pool_vdev(
                            cd['pool'], '/mnt/ramdisk_%s/ramfile' % cd['pool'])
                        if err:
                            raise Exception(err)
                    result, err = ramdisk.create_ramdisk(
                        1024 * cd['ramdisk_size'], '/mnt/ramdisk_%s' % cd['pool'], cd['pool'])
                    if err:
                        raise Exception(err)
                    else:
                        result, err = zfs.update_pool_log_vdev(
                            cd['pool'], '/mnt/ramdisk_%s/ramfile' % cd['pool'])
                        if err:
                            ramdisk.delete_ramdisk(
                                '/mnt/ramdisk_%s' % cd['pool'], cd['pool'])
                            raise Exception(err)
                        audit.audit("edit_zfs_slog", 'Changed the write log for pool %s to a RAM disk of size %dGB' % (
                            cd['pool'], cd['ramdisk_size']), request)
            else:
                # Flash drive
                result, err = zfs.update_pool_log_vdev(cd['pool'], cd['disk'])
                if err:
                    raise Exception(err)
                audit.audit("edit_zfs_slog", 'Changed the write log for pool %s to a flash drive' % (
                    cd['pool']), request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=changed_slog&name=%s&view=components' % pool_name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Set ZFS pool write cache'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error setting ZFS pool write cache'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_slog(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['pool', 'device', 'type'])
        if err:
            raise Exception(err)
        if ('pool' and 'device' and 'type') not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool = req_ret['pool']
        device = req_ret['device']
        return_dict["pool"] = pool
        type = req_ret["type"]
        return_dict["device"] = device
        return_dict["type"] = type
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_slog_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.delete_pool_vdev(pool, device)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)
            if type == 'ramdisk':
                result, err = ramdisk.delete_ramdisk(
                    '/mnt/ramdisk_%s' % pool, pool)
                if err:
                    raise Exception(err)

            audit_str = "Removed ZFS write cache for pool %s" % pool
            audit.audit("remove_zfs_slog", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&ack=slog_deleted&view=components' % pool)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Removing ZFS pool write cache'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing ZFS pool write cache'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_zfs_l2arc(request):
    return_dict = {}
    try:

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool'])
        if err:
            raise Exception(err)
        if 'pool' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool']

        pool, err = zfs.get_pool(pool_name)

        if err:
            raise Exception(err)
        elif not pool:
            raise Exception(
                "Error loading ZFS storage information : Specified pool not found")

        free_disks, err = zfs.get_free_disks(disk_type='flash')
        if err:
            raise Exception(err)
        # print free_disks
        if not free_disks:
            raise Exception(
                'There are no unused flash drives to use as a read cache')

        if request.method == "GET":
            # Return the conf page

            initial = {}
            initial['pool'] = pool_name

            form = zfs_forms.L2arcForm(initial=initial, free_disks=free_disks)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_zfs_l2arc.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.L2arcForm(request.POST, free_disks=free_disks)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_zfs_l2arc.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            # print cd
            result, err = zfs.update_pool_cache_vdev(cd['pool'], cd['disk'])
            if err:
                raise Exception(err)
            ret, err = audit.audit("edit_zfs_l2arc", 'Changed the read cache for pool %s to a flash drive' % (
                cd['pool']), request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=changed_l2arc&name=%s&view=components' % pool_name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Set ZFS pool read cache'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error setting ZFS pool read cache'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_l2arc(request):

    return_dict = {}
    try:

        req_ret, err = django_utils.get_request_parameter_values(
            request, ['pool', 'device'])
        if err:
            raise Exception(err)
        if ('pool' and 'device') not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool = req_ret['pool']
        device = req_ret['device']

        return_dict["pool"] = pool
        return_dict["device"] = device

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_l2arc_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.delete_pool_vdev(pool, device)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Removed ZFS read cache for pool %s" % pool
            ret, err = audit.audit("remove_zfs_l2arc", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&ack=l2arc_deleted&view=components' % pool)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Removing ZFS pool read cache'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing ZFS pool read cache'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_dataset(request):
    return_dict = {}
    try:
        template = 'logged_in_error.html'

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")

        if "ack" in request.GET:
            if request.GET["ack"] == "set_quota":
                return_dict['ack_message'] = "ZFS quota successfully set"
            elif request.GET["ack"] == "removed_quota":
                return_dict['ack_message'] = "ZFS quota successfully removed"
            elif request.GET["ack"] == "set_permissions":
                return_dict['ack_message'] = "Directory ownership/permissions successfully set"
            elif request.GET["ack"] == "modified_dataset_properties":
                return_dict['ack_message'] = "ZFS dataset/volume configuration successfully modified"
            elif request.GET["ack"] == "created_dataset":
                return_dict['ack_message'] = "ZFS dataset successfully created"

        dataset_name = req_ret['name']
        if '/' in dataset_name:
            pos = dataset_name.find('/')
            pool = dataset_name[:pos]
        else:
            pool = dataset_name
        return_dict['pool'] = pool

        properties, err = zfs.get_properties(dataset_name)
        if err:
            raise Exception(err)
        elif not properties:
            raise Exception("Specified dataset not found")

        children, err = zfs.get_children_datasets(dataset_name)
        if err:
            raise Exception(err)

        is_zvol = True
        if properties['type']['value'] == 'filesystem':
            is_zvol = False
            quotas, err = zfs.get_all_quotas(dataset_name)
            if err:
                raise Exception(err)
            return_dict['quotas'] = quotas

        schedule, err = zfs.get_snapshot_schedule(dataset_name)
        if err:
            raise Exception(err)

        return_dict['snapshot_schedule'] = schedule

        if children:
            return_dict['children'] = children
        return_dict['name'] = dataset_name
        return_dict['properties'] = properties
        prop_dict, err = zfs.get_exposed_ds_zvol_properties(properties)
        if err:
            raise Exception(err)
        return_dict['exposed_properties'] = prop_dict['exposed_properties']
        return_dict['ordered_exposed_properties'] = prop_dict['ordered_exposed_properties']
        if 'result' in request.GET:
            return_dict['result'] = request.GET['result']

        template = "view_zfs_dataset.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS dataset details'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error loading ZFS dataset details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_zfs_dataset(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")

        name = req_ret['name']
        is_zvol = False

        properties, err = zfs.get_properties(name)
        if not properties and err:
            raise Exception(err)
        elif not properties:
            raise Exception("Error loading ZFS dataset properties")

        if properties['type']['value'] == 'volume':
            is_zvol = True

        return_dict['type'] = properties['type']
        if is_zvol is False:
            return_dict['quota'] = properties['quota']['value']
        else:
            return_dict['quota'] = 'none'

        if request.method == "GET":
            # Return the conf page
            initial = {}
            initial['name'] = name
            for p in ['compression', 'dedup', 'readonly']:
                if properties[p]['value'] == 'off':
                    initial[p] = False
                else:
                    initial[p] = True
            if is_zvol is True:
                form = zfs_forms.BaseZvolForm(initial=initial)
            else:
                form = zfs_forms.BaseDatasetForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_zfs_dataset.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            if is_zvol is True:
                form = zfs_forms.BaseZvolForm(request.POST)
            else:
                form = zfs_forms.BaseDatasetForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_zfs_dataset.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result_str = ""
            audit_str = "Changed the following dataset properties for dataset %s : " % name
            success = False
            # Do this for all boolean values
            to_change = []
            for p in ['compression', 'dedup', 'readonly']:
                orig = properties[p]['value']
                if cd[p]:
                    changed = 'on'
                else:
                    changed = 'off'
                # print 'property %s orig %s changed %s'%(p, orig, changed)
                if orig != changed:
                    result, err = zfs.update_dataset_zvol_property(
                        name, p, changed)
                    # print err
                    if not result:
                        result_str += ' Error setting property %s' % p
                        if not err:
                            results += ' : %s' % str(e)
                    else:
                        result_str += ' Successfully set property %s to %s' % (
                            p, changed)
                        audit_str += " property '%s' set to '%s'" % (
                            p, changed)
                        success = True

            if is_zvol is False:
                orig_quota = properties['quota']['value']
                print 'original quota was ', orig_quota
                if 'quota_size' not in cd or not cd['quota_size']:
                    new_quota = 'none'
                elif cd['quota_size'] == 0:
                    new_quota = 'none'
                else:
                    new_quota = '%d%s' % (cd['quota_size'], cd['quota_unit'])
                print 'new quota is ', new_quota
                if orig_quota != new_quota:
                    result, err = zfs.update_dataset_zvol_property(
                        name, 'quota', new_quota)
                    if not result:
                        result_str += ' Error setting property quota'
                        if not err:
                            results += ' : %s' % str(e)
                    audit_str += " property 'quota' set to '%s'" % new_quota
                    success = True
            if success:
                audit.audit("edit_zfs_dataset", audit_str, request)

            return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&ack=modified_dataset_properties' % name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Modify ZFS dataset properties'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error modifying ZFS dataset properties'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_zfs_dataset_advanced_properties(request):
    return_dict = {}
    try:
        param_dict, err = django_utils.get_request_parameter_values(request, [
                                                                    'name'])
        if err:
            raise Exception(err)
        if 'name' not in param_dict.keys() or not param_dict['name']:
            raise Exception(
                'Dataset name not specified. Please use the menus.')
        name = param_dict['name']

        properties, err = zfs.get_properties(name)
        if not properties and err:
            raise Exception(err)
        elif not properties:
            raise Exception("Error loading ZFS dataset properties")

        return_dict['type'] = properties['type']

        prop_dict, err = zfs.get_exposed_ds_zvol_properties(properties)
        if err:
            raise Exception(err)

        if request.method == "GET":
            # Return the conf page
            initial = {}
            initial['name'] = name
            form = zfs_forms.AdvancedDatasetZvolPropertiesForm(
                modifiable_properties=prop_dict['modifiable_properties'], initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_zfs_dataset_zvol_advanced_properties.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.AdvancedDatasetZvolPropertiesForm(
                request.POST, modifiable_properties=prop_dict['modifiable_properties'])
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("update_zfs_dataset_zvol_advanced_properties.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result_str = ""
            result, err = zfs.update_dataset_zvol_property(
                name, cd['property_name'], cd['property_value'])
            if err:
                raise Exception(err)
            audit_str = "Updated the dataset/volume property %s for dataset %s to %s : " % (
                cd['property_name'], name, cd['property_value'])
            audit.audit("edit_zfs_dataset", audit_str, request)

            return django.http.HttpResponseRedirect('/view_zfs_dataset?name=%s&ack=modified_dataset_properties' % name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Modify ZFS advance dataset/volume properties'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error modifying ZFS advanced dataset/volume properties'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_dataset(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['name', 'type', 'pool_name'])
        if err:
            raise Exception(err)
        if ('name' and 'pool_name') not in req_ret:
            raise Exception("Invalid request, please use the menus.")

        name = req_ret['name']
        pool_name = req_ret['pool_name']
        if 'type' not in req_ret:
            type = 'filesystem'
        else:
            type = req_ret['type']
        nfs_shares, err = nfs.get_shares_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        cifs_shares, err = common_cifs.get_shares_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        luns, err = iscsi_stgt.get_luns_on_subpath('%s/' % name)
        if err:
            raise Exception(err)
        if nfs_shares or cifs_shares or luns:
            elements = []
            if nfs_shares:
                shl = []
                for sh in nfs_shares:
                    shl.append(sh['path'])
                elements .append('NFS share(s) : %s' % ' , '.join(shl))
            if cifs_shares:
                shl = []
                for sh in cifs_shares:
                    shl.append(sh['name'])
                elements .append('CIFS share(s) : %s' % ' , '.join(shl))
            if luns:
                shl = []
                for sh in luns:
                    shl.append(sh['path'][9:])
                elements .append('ISCSI LUN(s) : %s' % ' , '.join(shl))
            raise Exception(
                'The dataset cannot be deleted as the following components exist on this pool : %s. Please delete them first before deleting the pool.' % ' , '.join(elements))
        return_dict["name"] = name
        return_dict["pool_name"] = pool_name
        return_dict["type"] = type
        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_dataset_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.delete_dataset(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            if type == 'filesystem':
                audit_str = "Deleted ZFS dataset %s" % name
                audit.audit("delete_zfs_dataset", audit_str, request)
                return django.http.HttpResponseRedirect('/view_zfs_pool?ack=dataset_deleted&name=%s' % pool_name)
            else:
                audit_str = "Deleted ZFS block device volume %s" % name
                audit.audit("delete_zfs_zvol", audit_str, request)
                return django.http.HttpResponseRedirect('/view_zfs_pool?ack=zvol_deleted&name=%s&view=datasets_and_zvols' % pool_name)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Remove a ZFS dataset/volume'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing a dataset/volume '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_zfs_dataset(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool'])
        if err:
            raise Exception(err)
        if 'pool' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool = req_ret['pool']

        datasets, err = zfs.get_children_datasets(pool)
        if err:
            raise Exception("Could not retrieve the list of existing datasets")
        if pool not in datasets:
            datasets.append(pool)
        return_dict['pool'] = pool

        if request.method == "GET":
            # Return the conf page
            initial = {}
            initial['pool'] = pool
            form = zfs_forms.CreateDatasetForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.CreateDatasetForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_zfs_dataset.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            properties = {}
            if 'compression' in cd and cd['compression']:
                properties['compression'] = 'on'
            if 'dedup' in cd and cd['dedup']:
                properties['dedup'] = 'on'
            if 'quota_size' in cd and cd['quota_size'] and int(cd['quota_size']) > 0:
                properties['quota'] = '%d%s' % (
                    int(cd['quota_size']), cd['quota_unit'])
            result, err = zfs.create_dataset(
                cd['pool'], cd['name'], properties)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Created a ZFS dataset named %s/%s" % (
                cd['pool'], cd['name'])
            audit.audit("create_zfs_dataset", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?name=%s&ack=created_dataset&view=datasets_and_zvols' % pool)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Create a ZFS dataset'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error creating a ZFS dataset'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_zfs_zvol(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool'])
        if err:
            raise Exception(err)
        if 'pool' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool = req_ret['pool']

        return_dict['pool'] = pool

        if request.method == "GET":
            parent = None
            if 'parent' in request.GET:
                parent = request.GET['parent']
            initial = {}
            initial['pool'] = pool
            initial['block_size'] = '64K'
            form = zfs_forms.CreateZvolForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_zfs_zvol.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.CreateZvolForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_zfs_zvol.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            properties = {}
            if 'compression' in cd and cd['compression']:
                properties['compression'] = 'on'
            if 'dedup' in cd and cd['dedup']:
                properties['dedup'] = 'on'
            if 'thin_provisioned' in cd and cd['thin_provisioned']:
                thin = True
            else:
                thin = False
            result, err = zfs.create_zvol(
                cd['pool'], cd['name'], properties, cd['size'], cd['unit'], cd['block_size'], thin)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            if thin:
                audit_str = "Created a thinly provisioned ZFS block device volume named %s/%s with size %s%s" % (
                    cd['pool'], cd['name'], cd['size'], cd['unit'])
            else:
                audit_str = "Created a ZFS block device volume named %s/%s with size %s%s" % (
                    cd['pool'], cd['name'], cd['size'], cd['unit'])
            audit.audit("create_zfs_zvol", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=created_zvol&name=%s&view=datasets_and_zvols' % pool)
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Create a ZFS block device volume'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error creating a ZFS block device volume '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_zvol(request):
    return_dict = {}
    try:
        template = 'logged_in_error.html'
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['name']

        if '/' in name:
            pos = name.find('/')
            pool = name[:pos]
        else:
            pool = name
        return_dict['pool'] = pool

        properties, err = zfs.get_properties(name)
        if not properties and err:
            raise Exception(err)
        elif not properties:
            raise Exception("Specified block device volume not found")

        return_dict['name'] = name
        return_dict['properties'] = properties
        return_dict['exposed_properties'] = ['compression',
                                             'compressratio', 'dedup',  'type',  'creation']
        if 'result' in request.GET:
            return_dict['result'] = request.GET['result']

        template = "view_zfs_zvol.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS block device volume details'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error loading ZFS block device volume details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_snapshots(request):
    return_dict = {}
    try:

        datasets, err = zfs.get_all_datasets_and_pools()
        if err:
            raise Exception(err)

        # If the list of snapshots is for a particular dataset or pool, get the
        # name of that ds or pool
        name = None
        snap_list = None
        initial = {}
        if 'name' in request.GET:
            name = request.GET['name']
        else:
            name = None

        if name == 'None':
            name = None
        if name:
            initial['name'] = name
        snap_list, err = zfs.get_snapshots(name)
        if err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "created":
                return_dict['ack_message'] = "ZFS snapshot successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "ZFS snapshot successfully destroyed"
            elif request.GET["ack"] == "scheduled":
                return_dict['ack_message'] = "ZFS snapshot schedule successfully modified"
            elif request.GET["ack"] == "renamed":
                return_dict['ack_message'] = "ZFS snapshot successfully renamed"
            elif request.GET["ack"] == "rolled_back":
                return_dict['ack_message'] = "ZFS filesystem successfully rolled back to the snapshot"

        form = zfs_forms.ViewSnapshotsForm(initial=initial, datasets=datasets)
        return_dict['form'] = form
        return_dict["snap_list"] = snap_list
        template = "view_zfs_snapshots.html"
        return django.shortcuts.render_to_response(template, return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS snapshots'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error loading ZFS snapshots'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_zfs_snapshot(request):
    return_dict = {}
    try:
        datasets, err = zfs.get_all_datasets_and_pools()
        if not datasets:
            raise Exception("Could not get the list of existing datasets")

        if request.method == "GET":
            target = None
            if 'target' in request.GET:
                target = request.GET['target']
            # Return the conf page
            initial = {}
            if target:
                initial['target'] = target
            form = zfs_forms.CreateSnapshotForm(
                initial=initial, datasets=datasets)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.CreateSnapshotForm(
                request.POST, datasets=datasets)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result, err = zfs.create_snapshot(cd['target'], cd['name'])
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Created a ZFS snapshot named %s for target %s" % (
                cd['name'], cd['target'])
            audit.audit("create_zfs_snapshot", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_snapshots?ack=created')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Create a ZFS snapshot'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error creating a ZFS snapshot'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_snapshot(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['name', 'display_name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['name']
        return_dict["name"] = name
        if 'display_name' in req_ret:
            return_dict["display_name"] = req_ret['display_name']

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_zfs_snapshot_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.delete_snapshot(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Deleted ZFS snapshot %s" % name
            audit.audit("delete_zfs_snapshot", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_snapshots?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Delete a ZFS snapshot'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error deleting a ZFS snapshot'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_all_zfs_snapshots(request):
    return_dict = {}
    try:
        pool_names, err = zfs.get_all_pool_names()
        if err:
            raise exception(err)
        fs_names, err = zfs.get_all_datasets_and_pools(dataset_type='filesystem')
        if err:
            raise exception(err)
        all_child_fs = []
        child_fs = []
        if pool_names and fs_names:
            # Remove root zfs filesystems from the list
            all_child_fs = [fs for fs in fs_names if fs not in pool_names]
            for fs in all_child_fs:
                # Include only the filesystem that contain snapshots
                has_snaps, err = zfs.get_snapshots(fs)
                if has_snaps:
                    child_fs.append(fs)
        return_dict['child_fs'] = child_fs

        if request.method == "GET":
            form = zfs_forms.DeleteSnapshotsForm(
                child_fs=child_fs)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("delete_all_zfs_snapshots.html", return_dict, context_instance=django.template.context.RequestContext(request))

        else:
            form = zfs_forms.DeleteSnapshotsForm(
                request.POST, child_fs=child_fs)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("delete_all_zfs_snapshots.html", return_dict, context_instance=django.template.context.RequestContext(request))

            cd = form.cleaned_data

            filesystems = []
            if 'filesystems' in cd and cd['filesystems']:
                filesystems = [fs for fs in cd['filesystems']]

            audit_fail_str = 'Failed deleting snapshots of - '
            audit_str = 'Deleted snapshots of - '
            is_fail_str = False
            for fs in filesystems:
                result, err = zfs.delete_all_snapshots(fs)
                if not result:
                    if not err:
                        audit_fail_str = '%s %s,' % (audit_fail_str, fs)
                    else:
                        audit_fail_str = '%s %s,' % (audit_fail_str, fs)
                elif result:
                    audit_str = '%s %s,' % (audit_str, fs)
            if is_fail_str:
                audit_str = '%s %s' % (audit_str, audit_fail_str)
                audit.audit("delete_zfs_snapshot", audit_str, request)
                raise Exception(audit_str)
            else:
                audit.audit("delete_zfs_snapshot", audit_str, request)

            return django.http.HttpResponseRedirect('/view_zfs_snapshots?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Delete ZFS snapshots'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error deleting ZFS snapshots'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def rollback_zfs_snapshot(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['name', 'display_name'])
        if err:
            raise Exception(err)
        if 'name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        name = req_ret['name']
        return_dict["name"] = name
        if 'display_name' in req_ret:
            return_dict["display_name"] = req_ret['display_name']

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("rollback_zfs_snapshot_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            result, err = zfs.rollback_snapshot(name)
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Rolled back to ZFS snapshot %s" % name
            audit.audit("rollback_zfs_snapshot", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_snapshots?ack=rolled_back')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Rollback a ZFS snapshot'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error rolling back a  ZFS snapshot'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def rename_zfs_snapshot(request):
    return_dict = {}
    try:
        if request.method == "GET":
            if ('ds_name' not in request.GET) or ('snapshot_name' not in request.GET):
                raise Exception(
                    "Required info not passed. Please use the menus.")

            ds_name = request.GET['ds_name']
            snapshot_name = request.GET['snapshot_name']
            # Return the conf page
            initial = {}
            initial['snapshot_name'] = snapshot_name
            initial['ds_name'] = ds_name
            form = zfs_forms.RenameSnapshotForm(initial=initial)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("rename_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.RenameSnapshotForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("rename_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result, err = zfs.rename_snapshot(
                cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
            if not result:
                if not err:
                    raise Exception('Unknown error!')
                else:
                    raise Exception(err)

            audit_str = "Renamed  ZFS snapshot for %s from %s to %s" % (
                cd['ds_name'], cd['snapshot_name'], cd['new_snapshot_name'])
            audit.audit("rename_zfs_snapshot", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_snapshots?ack=renamed')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Rename a ZFS snapshot'
        return_dict['tab'] = 'view_zfs_snapshots_tab'
        return_dict["error"] = 'Error renaming a loading ZFS snapshot'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_zfs_snapshot_schedules(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "scheduled":
                return_dict['ack_message'] = "ZFS snapshot schedule successfully modified"
        snapshot_schedules, err = zfs.get_all_snapshot_schedules()
        if err:
            raise Exception(err)
        return_dict["snapshot_schedules"] = snapshot_schedules
        return django.shortcuts.render_to_response("view_zfs_snapshot_schedules.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'ZFS snapshot schedules'
        return_dict['tab'] = 'zfs_snapshots_schedule_tab'
        return_dict["error"] = 'Error retrieving ZFS snapshot schedules'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def schedule_zfs_snapshot(request):
    return_dict = {}
    try:
        datasets, err = zfs.get_all_datasets_and_pools()
        if err:
            raise Exception(err)
        if not datasets:
            raise Exception("Could not get the list of existing datasets")

        if request.method == "GET":
            target = None
            if 'target' in request.GET:
                target = request.GET['target']
            # Return the conf page
            schedule = None
            if not target:
                target = datasets[0]
            schedule, err = zfs.get_snapshot_schedule(target)
            if err:
                raise Exception(err)
            initial = {}
            if schedule:
                initial['frequent'] = schedule['frequent']
                initial['hourly'] = schedule['hourly']
                initial['daily'] = schedule['daily']
                initial['weekly'] = schedule['weekly']
                initial['monthly'] = schedule['monthly']
            if target:
                initial['target'] = target
            form = zfs_forms.ScheduleSnapshotForm(
                initial=initial, datasets=datasets)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("schedule_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.ScheduleSnapshotForm(
                request.POST, datasets=datasets)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("schedule_zfs_snapshot.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            target = cd['target']
            frequent = cd['frequent']
            hourly = cd['hourly']
            daily = cd['daily']
            weekly = cd['weekly']
            monthly = cd['monthly']
            result, err = zfs.schedule_snapshot(
                target, frequent, hourly, daily, weekly, monthly)
            audit_str = "Enabled/Modified ZFS snapshot scheduling for target %s " % cd['target']
            if err:
                raise Exception(err)

            audit.audit("schedule_zfs_snapshot", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_snapshot_schedules?ack=scheduled')
    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Schedule a ZFS snapshot'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error scheduling ZFS snapshot'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_zfs_spares(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool_name'])
        if err:
            raise Exception(err)
        if 'pool_name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool_name']
        free_drives, err = zfs.get_free_disks_for_spares(pool_name)
        if err:
            raise Exception(err)
        num_free_drives = len(free_drives)
        if request.method == 'GET':
            if num_free_drives == 0:
                raise Exception(
                    'There are no free drives to be added as spares')
            form = zfs_forms.AddSparesForm(num_free_drives=num_free_drives)
            return_dict['form'] = form
            return_dict['pool_name'] = pool_name
            return django.shortcuts.render_to_response("create_zfs_spares.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = zfs_forms.AddSparesForm(
                request.POST, num_free_drives=num_free_drives)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_zfs_spares.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            num_spares = cd['num_spares']
            # print num_spares
            ret, err = zfs.add_spares_to_pool(pool_name, int(num_spares))
            if err:
                raise Exception(err)
            audit_str = "Added %s spare drive(s) to pool %s" % (
                num_spares, pool_name)
            audit.audit("add_zfs_spares", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=added_spares&name=%s&view=components' % pool_name)

    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Add spare drives to a ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error adding spares drives to a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_zfs_spare(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'pool_name'])
        if err:
            raise Exception(err)
        if 'pool_name' not in req_ret:
            raise Exception("Invalid request, please use the menus.")
        pool_name = req_ret['pool_name']
        spares, err = zfs.get_pool_spares(pool_name)
        if err:
            raise Exception(err)
        if not spares:
            raise Exception(
                'The pool does not have any spare drives assigned to it')
        if request.method == 'GET':
            return_dict['pool_name'] = pool_name
            return django.shortcuts.render_to_response("delete_zfs_spare_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = zfs.delete_spare_from_pool(pool_name)
            if err:
                raise Exception(err)
            audit_str = "Removed a  spare drive from pool %s" % pool_name
            audit.audit("remove_zfs_spare", audit_str, request)
            return django.http.HttpResponseRedirect('/view_zfs_pool?ack=removed_spare&name=%s&view=components' % pool_name)

    except Exception, e:
        return_dict['base_template'] = "storage_base.html"
        return_dict["page_title"] = 'Remove a spare disk from a ZFS pool'
        return_dict['tab'] = 'view_zfs_pools_tab'
        return_dict["error"] = 'Error removing a  spares disk from a ZFS pool'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
