import django
import os

from integralstor import rsync, audit, zfs, config
from integral_view.forms import rsync_forms


def create_rsync_share(request):
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

        if request.method == "GET":
            form = rsync_forms.CreateShareForm(dataset_list=ds_list)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_rsync_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = rsync_forms.CreateShareForm(
                request.POST, dataset_list=ds_list)
            path = request.POST.get("path")
            if not os.path.exists(path):
                os.mkdir(path)
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

            os.chown(path, owner_uid, owner_gid)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_rsync_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            result, err = rsync.create_rsync_share(
                cd["name"], cd["path"], cd["comment"], cd["browsable"], cd["readonly"], "integralstor", "integralstor")
            if err:
                raise Exception(err)
            audit_str = "Created RSYNC share with name '%s'. The share is set to be %s and %s" % (
                cd["name"], "Browsable" if cd["browsable"] else "Not Browsable", "Readonly" if cd["readonly"] else "Read/Write")
            audit.audit("create_rsync_share", audit_str, request)
            return django.http.HttpResponseRedirect('/view_rsync_shares/?ack=created')
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'RSync shares'
        return_dict['tab'] = 'view_rsync_shares_tab'
        return_dict["error"] = 'Error creating RSync shares'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_rsync_share(request):
    return_dict = {}
    try:
        if request.method == "GET":
            name = request.GET.get("name")
            share, err = rsync.get_rsync_share_details(name)
            if err:
                raise Exception("Unable to load Rsync Shares")
            initial = {}
            initial["name"] = share["name"]
            initial["comment"] = share["comment"]
            initial["path"] = share["path"]
            if share["readonly"]:
                initial["readonly"] = True
            else:
                initial["readonly"] = False
            if share["list"]:
                initial["browsable"] = True
            else:
                initial["browsable"] = False
            form = rsync_forms.ShareForm(initial=initial)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("update_rsync_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = rsync_forms.ShareForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                delshare, err = rsync.delete_rsync_share(cd["name"])
                if err:
                    raise Exception(err)
                result, err = rsync.create_rsync_share(
                    cd["name"], cd["path"], cd["comment"], cd["browsable"], cd["readonly"], "integralstor", "integralstor")
                if err:
                    raise Exception(err)
                audit_str = "Edited RSYNC share with name '%s'. The share was modified to be %s and %s" % (
                    cd["name"], "Browsable" if cd["browsable"] else "Not Browsable", "Readonly" if cd["readonly"] else "Read/Write")
                #audit_str = "Edited RSYNC share %s"%cd["name"]
                audit.audit("edit_rsync_share", audit_str, request)
                return django.http.HttpResponseRedirect('/view_rsync_shares/?ack=saved')
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("update_rsync_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'RSync Share'
        return_dict['tab'] = 'view_rsync_shares_tab'
        return_dict["error"] = 'Error editing RSync shares'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_rsync_shares(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "saved":
                return_dict['ack_message'] = "RSync share information successfully updated"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "RSync share successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "RSync share  successfully deleted"
        shares, err = rsync.load_shares_list()
        if err:
            raise Exception("Unable to load Rsync Shares")
        return_dict["shares"] = shares
        return django.shortcuts.render_to_response("view_rsync_shares.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'RSync shares'
        return_dict['tab'] = 'view_rsync_shares_tab'
        return_dict["error"] = 'Error loading RSync shares'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_rsync_share(request):
    return_dict = {}
    try:
        if request.method == "GET":
            name = request.GET.get("name")
            return_dict["name"] = name
            return django.shortcuts.render_to_response("delete_rsync_share.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            name = request.POST.get("name")
            delshare, err = rsync.delete_rsync_share(name)
            if err:
                raise Exception(err)
            audit_str = "Deleted RSYNC share %s" % name
            audit.audit("delete_rsync_share", audit_str, request)
            return django.http.HttpResponseRedirect("/view_rsync_shares/?ack=deleted")
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'RSync shares'
        return_dict['tab'] = 'view_rsync_shares_tab'
        return_dict["error"] = 'Error deleting RSync share'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
