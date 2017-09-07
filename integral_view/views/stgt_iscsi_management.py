
from integralstor import iscsi_stgt, audit, django_utils, zfs

from integral_view.forms import iscsi_stgt_forms

import django
import django.template


def view_targets(request):
    return_dict = {}
    try:
        target_list, err = iscsi_stgt.get_targets()
        if err:
            raise Exception(err)

        return_dict["target_list"] = target_list

        if "ack" in request.GET:
            if request.GET["ack"] == "created":
                return_dict['ack_message'] = "ISCSI target successfully created"
            elif request.GET["ack"] == "target_deleted":
                return_dict['ack_message'] = "ISCSI target successfully deleted"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "ISCSI target successfully deleted"

        return django.shortcuts.render_to_response('view_iscsi_targets.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'ISCSI targets'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error loading ISCSI targets'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_target(request):
    return_dict = {}
    try:
        if 'name' not in request.GET:
            raise Exception("Malformed request. Please use the menus.")

        target, err = iscsi_stgt.get_target(request.GET['name'])
        if err:
            raise Exception(err)

        if not target:
            raise Exception(
                "Specified target not found. Please use the menus.")

        if "ack" in request.GET:
            if request.GET["ack"] == "lun_created":
                return_dict['ack_message'] = "ISCSI LUN successfully created"
            elif request.GET["ack"] == "lun_deleted":
                return_dict['ack_message'] = "ISCSI LUN successfully deleted"
            elif request.GET["ack"] == "added_acl":
                return_dict['ack_message'] = "ISCSI target ACL successfully added"
            elif request.GET["ack"] == "removed_acl":
                return_dict['ack_message'] = "ISCSI target ACL successfully removed"
            elif request.GET["ack"] == "added_initiator_authentication":
                return_dict['ack_message'] = "ISCSI initiator authentication successfully added"
            elif request.GET["ack"] == "added_target_authentication":
                return_dict['ack_message'] = "ISCSI target authentication successfully added"
            elif request.GET["ack"] == "removed_initiator_authentication":
                return_dict['ack_message'] = "ISCSI initiator authentication successfully removed"
            elif request.GET["ack"] == "removed_target_authentication":
                return_dict['ack_message'] = "ISCSI target authentication successfully removed"

        return_dict["target"] = target

        return django.shortcuts.render_to_response('view_iscsi_target.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'ISCSI target details'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error loading ISCSI target details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_iscsi_target(request):
    return_dict = {}
    try:
        if request.method == "GET":
            # Return the form
            form = iscsi_stgt_forms.IscsiTargetForm()
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            form = iscsi_stgt_forms.IscsiTargetForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ret, err = iscsi_stgt.create_target(cd["name"])
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Unknown error.")
                audit_str = "Created an ISCSI target %s" % cd["name"]
                audit.audit("create_iscsi_target", audit_str, request)
                url = '/view_iscsi_targets?ack=created'
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_iscsi_target.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Create an ISCSI target'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error creating an ISCSI target'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_iscsi_target(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'target_name'])
        if err:
            raise Exception(err)
        if 'target_name' not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        target_name = req_ret['target_name']

        if request.method == "GET":
            return_dict["target_name"] = target_name
            return django.shortcuts.render_to_response("delete_iscsi_target_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = iscsi_stgt.delete_target(target_name)
            if not ret:
                if err:
                    raise Exception(err)
                else:
                    raise Exception("Unknown error")
            audit_str = "Deleted ISCSI target %s" % target_name
            url = '/view_iscsi_targets?ack=target_deleted'
            audit.audit("delete_iscsi_target", audit_str, request)
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Remove an ISCSI targets'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error removing an ISCSI target'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_iscsi_lun(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'target_name'])
        if err:
            raise Exception(err)
        if 'target_name' not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        target_name = req_ret['target_name']
        zvols, err = zfs.get_all_zvols()
        if err:
            raise Exception(err)
        if not zvols:
            raise Exception(
                "There are no block device volumes created. Please create one first before adding a LUN.")
        if request.method == "GET":
            # Return the form
            initial = {}
            initial['target_name'] = target_name
            form = iscsi_stgt_forms.IscsiLunForm(initial=initial, zvols=zvols)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            form = iscsi_stgt_forms.IscsiLunForm(request.POST, zvols=zvols)
            if form.is_valid():
                cd = form.cleaned_data
                ret, err = iscsi_stgt.create_lun(cd["target_name"], cd['path'])
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Unknown error.")
                audit_str = "Created an ISCSI LUN in target %s with path %s" % (
                    cd["target_name"], cd['path'])
                audit.audit("create_iscsi_lun", audit_str, request)
                url = '/view_iscsi_target?name=%s&ack=lun_created' % target_name
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_iscsi_lun.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Create an ISCSI LUN'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error creating an ISCSI LUN'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_iscsi_lun(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['target_name', 'store'])
        if err:
            raise Exception(err)
        if ('target_name' and 'store') not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        store = req_ret['store']
        target_name = req_ret['target_name']

        if request.method == "GET":
            return_dict["target_name"] = target_name
            return_dict["store"] = store
            return django.shortcuts.render_to_response("delete_iscsi_lun_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = iscsi_stgt.delete_lun(target_name, store)
            if not ret:
                if err:
                    raise Exception(err)
                else:
                    raise Exception("Unknown error.")
            audit_str = "Deleted ISCSI LUN %s from target %s" % (
                store, target_name)
            url = '/view_iscsi_target?name=%s&ack=lun_deleted' % target_name
            audit.audit("delete_iscsi_lun", audit_str, request)
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Remove an ISCSI LUN'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error removing an ISCSI LUN'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_iscsi_user_authentication(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['target_name', 'authentication_type'])
        if err:
            raise Exception(err)
        if ('target_name' and 'authentication_type') not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        authentication_type = req_ret['authentication_type']
        target_name = req_ret['target_name']

        if authentication_type not in ['incoming', 'outgoing']:
            raise Exception("Invalid user type. Please use the menus.")

        if request.method == "GET":
            # Return the form
            initial = {}
            initial['authentication_type'] = authentication_type
            initial['target_name'] = target_name
            form = iscsi_stgt_forms.IscsiAuthenticationForm(initial=initial)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_iscsi_target_user.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            form = iscsi_stgt_forms.IscsiAuthenticationForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ret, err = iscsi_stgt.add_user_authentication(
                    cd['target_name'], cd['authentication_type'], cd["username"], cd["password"])
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Error adding the ISCSI target user.")
                if cd['authentication_type'] == 'incoming':
                    audit_str = "Added ISCSI initiator authentication user %s for target %s" % (
                        cd["username"], cd['target_name'])
                    url = '/view_iscsi_target?name=%s&ack=added_initiator_authentication' % target_name
                else:
                    audit_str = "Added ISCSI target authentication user %s for target %s" % (
                        cd["username"], cd['target_name'])
                    url = '/view_iscsi_target?name=%s&ack=added_target_authentication' % target_name
                audit.audit("add_iscsi_target_authentication",
                            audit_str, request)
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_iscsi_target_user.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Add ISCSI authentication user'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error adding ISCSI authentication user'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_iscsi_user_authentication(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['target_name', 'authentication_type', 'username'])
        if err:
            raise Exception(err)
        if ('target_name' and 'authentication_type' and 'username') not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        authentication_type = req_ret['authentication_type']
        target_name = req_ret['target_name']
        username = req_ret['username']

        if authentication_type not in ['incoming', 'outgoing']:
            raise Exception("Invalid user type. Please use the menus.")

        if request.method == "GET":
            return_dict["target_name"] = target_name
            return_dict["username"] = username
            return_dict["authentication_type"] = authentication_type
            return django.shortcuts.render_to_response("delete_iscsi_user_auth_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = iscsi_stgt.remove_user_authentication(
                target_name, username, authentication_type)
            if not ret:
                if err:
                    raise Exception(err)
                else:
                    raise Exception("Unknown error.")
            if authentication_type == 'incoming':
                audit_str = "Removed ISCSI initiator authentication user %s for target %s" % (
                    username, target_name)
                url = '/view_iscsi_target?name=%s&ack=removed_initiator_authentication' % target_name
            else:
                audit_str = "Removed ISCSI target authentication user %s for target %s" % (
                    username, target_name)
                url = '/view_iscsi_target?name=%s&ack=removed_target_authentication' % target_name
            audit.audit("remove_iscsi_target_authentication",
                        audit_str, request)
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Remove ISCSI authentication user'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error removing ISCSI authentication user'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_iscsi_acl(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'target_name'])
        if err:
            raise Exception(err)
        if 'target_name' not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        target_name = req_ret['target_name']

        target, err = iscsi_stgt.get_target(target_name)
        if err:
            raise Exception(err)
        if not target:
            raise Exception('Specified target not found')

        if request.method == "GET":
            # Return the form
            initial = {}
            initial['target_name'] = target_name
            form = iscsi_stgt_forms.IscsiAclForm(initial=initial)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_iscsi_acl.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            form = iscsi_stgt_forms.IscsiAclForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ret, err = iscsi_stgt.add_acl(cd['target_name'], cd['acl'])
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Unknown error.")
                audit_str = "Added ISCSI ACL %s for target %s" % (
                    cd["acl"], cd['target_name'])
                url = '/view_iscsi_target?name=%s&ack=added_acl' % target_name
                audit.audit("add_iscsi_acl", audit_str, request)
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_iscsi_acl.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Add ISCSI ACL'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'Error adding ISCSI ACL'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_iscsi_acl(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(
            request, ['target_name', 'acl'])
        if err:
            raise Exception(err)
        if ('target_name' and 'acl') not in req_ret:
            raise Exception(
                "Invalid request, please use the menus.")

        target_name = req_ret['target_name']
        acl = req_ret['acl']

        if request.method == "GET":
            return_dict["target_name"] = target_name
            return_dict["acl"] = acl
            return django.shortcuts.render_to_response("delete_iscsi_acl_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            ret, err = iscsi_stgt.remove_acl(target_name, acl)
            if not ret:
                if err:
                    raise Exception(err)
                else:
                    raise Exception("Unknown error.")
            audit_str = "Removed ISCSI ACL %s for target %s" % (
                acl, target_name)
            url = '/view_iscsi_target?name=%s&ack=removed_acl' % target_name
            audit.audit("remove_iscsi_acl", audit_str, request)
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = "shares_base.html"
        return_dict["page_title"] = 'Remove ISCSI ACL'
        return_dict['tab'] = 'view_iscsi_targets_tab'
        return_dict["error"] = 'error Removing ISCSI ACL'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
