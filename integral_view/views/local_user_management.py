
import django
import django.template

import integral_view
from integral_view.forms import local_user_forms

from integralstor import local_users, audit, django_utils, config


def view_local_users(request):
    return_dict = {}
    try:
        user_list, err = local_users.get_local_users()
        if err:
            raise Exception(err)

        return_dict["user_list"] = user_list

        if "ack" in request.GET:
            if request.GET["ack"] == "saved":
                return_dict['ack_message'] = "Local user password successfully updated"
            elif request.GET["ack"] == "created":
                return_dict['ack_message'] = "Local user successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Local user successfully deleted"
            elif request.GET["ack"] == "changed_password":
                return_dict['ack_message'] = "Successfully updated password"
            elif request.GET["ack"] == "groups_changed":
                return_dict['ack_message'] = "Successfully updated group membership"
            elif request.GET["ack"] == "gid_changed":
                return_dict['ack_message'] = "Local user's group successfully updated"

        return django.shortcuts.render_to_response('view_local_users.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Local users'
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = 'Error loading local users list'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_local_groups(request):

    return_dict = {}
    try:
        group_list, err = local_users.get_local_groups()
        if err:
            raise Exception(err)
        return_dict["group_list"] = group_list

        if "ack" in request.GET:
            if request.GET["ack"] == "created":
                return_dict['ack_message'] = "Local group successfully created"
            elif request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Local group successfully deleted"
            elif request.GET["ack"] == "set_membership":
                return_dict['ack_message'] = "Local group membership successfully modified"

        return django.shortcuts.render_to_response('view_local_groups.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Local groups'
        return_dict['tab'] = 'view_local_groups_tab'
        return_dict["error"] = 'Error loading local groups list'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_local_user(request):

    return_dict = {}
    try:
        if 'searchby' not in request.GET:
            raise Exception("Malformed request. Please use the menus.")

        if request.GET['searchby'] == 'username':
            if 'username' not in request.GET:
                raise Exception("Malformed request. Please use the menus.")
            ud, err = local_users.get_local_user(request.GET['username'])
        elif request.GET['searchby'] == 'uid':
            if 'uid' not in request.GET:
                raise Exception("Malformed request. Please use the menus.")
            ud, err = local_users.get_local_user(
                request.GET['username'], False)

        if err:
            raise Exception(err)

        if not ud:
            raise Exception("Specified user not found. Please use the menus.")

        return_dict["user"] = ud

        if "ack" in request.GET:
            if request.GET["ack"] == "gid_changed":
                return_dict['ack_message'] = "Local user's group successfully updated"
            elif request.GET["ack"] == "changed_password":
                return_dict['ack_message'] = "Successfully update password"

        return django.shortcuts.render_to_response('view_local_user.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Local user details'
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = 'Error loading local user details'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_local_group(request):
    return_dict = {}
    try:
        if 'searchby' not in request.GET:
            raise Exception("Malformed request. Please use the menus.")
        if request.GET['searchby'] == 'grpname':
            if 'grpname' not in request.GET:
                raise Exception("Malformed request. Please use the menus.")
            gd, err = local_users.get_local_group(request.GET['grpname'])
        elif request.GET['searchby'] == 'gid':
            if 'gid' not in request.GET:
                raise Exception("Malformed request. Please use the menus.")
            gd, err = local_users.get_local_group(
                request.GET['grpname'], False)

        if err:
            raise Exception(err)

        if not gd:
            raise Exception("Specified group not found. Please use the menus.")

        return_dict["group"] = gd

        if "ack" in request.GET:
            if request.GET["ack"] == "gid_changed":
                return_dict['ack_message'] = "Local user's group successfully updated"
            elif request.GET["ack"] == "changed_password":
                return_dict['ack_message'] = "Successfully update password"
            elif request.GET["ack"] == "set_membership":
                return_dict['ack_message'] = "Local group membership successfully modified"

        return django.shortcuts.render_to_response('view_local_group.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Local group details'
        return_dict['tab'] = 'view_local_groups_tab'
        return_dict["error"] = 'Error loading local group details '
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_local_user_group_membership(request):

    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "created":
                return_dict['ack_message'] = "Local user successfully created"
        t_group_list, err = local_users.get_local_groups()
        if err:
            raise Exception(err)

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'username'])
        if err:
            raise Exception(err)
        if 'username' not in req_ret:
            raise Exception('Invalid request, please use the menus.')

        username = req_ret['username']
        ud, err = local_users.get_local_user(username)
        if err:
            raise Exception(err)
        if not ud:
            raise Exception("Specified user information not found")
        group_list = []
        if t_group_list:
            for g in t_group_list:
                if g['grpname'] == ud['grpname']:
                    continue
                else:
                    group_list.append(g)

        if request.method == "GET":
            # Shd be an edit request

            # Set initial form values
            initial = {}
            initial['username'] = ud['username']
            initial['groups'] = ud['other_groups']

            form = local_user_forms.EditLocalUserGroupMembershipForm(
                initial=initial, group_list=group_list)

            return_dict["form"] = form
            return django.shortcuts.render_to_response('update_local_user_group_membership.html', return_dict, context_instance=django.template.context.RequestContext(request))

        else:

            # Shd be an save request
            form = local_user_forms.EditLocalUserGroupMembershipForm(
                request.POST, group_list=group_list)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                ret, err = local_users.set_local_user_group_membership(cd)
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception(
                            "Error saving user's group membership information")

                audit_str = "Modified local user group membership information %s" % cd[
                    "username"]
                audit.audit("modify_local_user_grp_membership",
                            audit_str, request)

                return django.http.HttpResponseRedirect('/view_local_users?ack=groups_changed')

            else:
                # Invalid form
                return django.shortcuts.render_to_response('update_local_user_group_membership.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Local users additional group membership'
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = 'Error modifying local users additional group membership'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_local_user(request):
    return_dict = {}
    try:
        group_list, err = local_users.get_local_groups()
        if err:
            raise Exception(err)
        if request.method == "GET":
            # Return the form
            #form = local_user_forms.LocalUserForm(group_list = group_list)
            form = local_user_forms.LocalUserForm()
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            #form = local_user_forms.LocalUserForm(request.POST, group_list = group_list)
            form = local_user_forms.LocalUserForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                #ret, err = local_users.create_local_user(cd["username"], cd["name"], cd["password"], cd['gid'])
                group_name, err = config.get_users_default_group()
                if err:
                    raise Exception(err)
                default_gid, err = config.get_system_uid_gid(
                    group_name, 'group')
                if err:
                    raise Exception(err)

                ret, err = local_users.create_local_user(
                    cd["username"], cd["name"], cd["password"], default_gid)
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Error creating the local user.")

                audit_str = "Created a local user %s" % cd["username"]
                audit.audit("create_local_user", audit_str, request)
                if group_list:
                    url = '/update_local_user_group_membership/?username=%s&ack=created' % cd['username']
                else:
                    url = '/view_local_users?ack=created'
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_local_user.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Create a local users'
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = 'Error creating a local user'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_local_group(request):
    return_dict = {}
    try:
        if request.method == "GET":
            # Return the form
            form = local_user_forms.LocalGroupForm()
            return_dict["form"] = form
            return django.shortcuts.render_to_response("create_local_group.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            # print '1'
            form = local_user_forms.LocalGroupForm(request.POST)
            if form.is_valid():
                # print '2'
                cd = form.cleaned_data
                ret, err = local_users.create_local_group(cd["grpname"])
                # print '3'
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Error creating the local group.")
                audit_str = "Created a local group %s" % cd["grpname"]
                audit.audit("create_local_group", audit_str, request)
                #url = '/view_local_groups?ack=created'
                url = '/update_group_membership?grpname=%s&ack=created' % cd['grpname']
                return django.http.HttpResponseRedirect(url)
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("create_local_group.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Create a local user group'
        return_dict['tab'] = 'view_local_groups_tab'
        return_dict["error"] = 'Error create a local user group'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_local_group(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'grpname'])
        if err:
            raise Exception(err)
        if 'grpname' not in req_ret:
            raise Exception('Invalid request, please use the menus.')

        gd, err = local_users.get_local_group(req_ret['grpname'])
        if err or (not gd):
            if err:
                raise Exception(err)
            else:
                raise Exception("Could not retrieve group information")

        if gd['members']:
            raise Exception("Cannot delete this group as it has the following members : %s" % (
                ','.join(gd['members'])))

        if request.method == "GET":
            # Return the form
            return_dict["grpname"] = request.GET["grpname"]
            return django.shortcuts.render_to_response("delete_local_group_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            ret, err = local_users.delete_local_group(request.POST["grpname"])
            if not ret:
                if err:
                    raise Exception('Error deleting group : %s' % err)
                else:
                    raise Exception('Error deleting group')
            audit_str = "Deleted a local group %s" % request.POST["grpname"]
            audit.audit("delete_local_group", audit_str, request)
            url = '/view_local_groups?ack=deleted'
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Delete a local user group'
        return_dict['tab'] = 'view_local_groups_tab'
        return_dict["error"] = 'Error deleting a local user group'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_local_user(request):

    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'username'])
        if err:
            raise Exception(err)
        if 'username' not in req_ret:
            raise Exception('Invalid request, please use the menus.')

        if request.method == "GET":
            # Return the form
            return_dict["username"] = request.GET["username"]
            return django.shortcuts.render_to_response("delete_local_user_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            ret, err = local_users.delete_local_user(request.POST["username"])
            if not ret:
                if err:
                    raise Exception(err)
                else:
                    raise Exception('Error deleting local user')
            audit_str = "Deleted a local user %s" % request.POST["username"]
            audit.audit("delete_local_user", audit_str, request)
            url = '/view_local_users?ack=deleted'
            return django.http.HttpResponseRedirect(url)
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Delete a local user'
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = 'Error deleting a local user'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_local_user_password(request):

    return_dict = {}
    try:
        if request.method == "GET":
            # Return the form
            if "username" not in request.GET:
                raise Exception("Invalid request. No user name specified.")
            d = {}
            d["username"] = request.GET["username"]
            form = local_user_forms.PasswordChangeForm(initial=d)
            return_dict["form"] = form
            return django.shortcuts.render_to_response("update_local_user_password.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            # Form submission so create
            return_dict = {}
            form = local_user_forms.PasswordChangeForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                rc, err = local_users.change_password(
                    cd["username"], cd["password"])
                if not rc:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception(
                            "Error changing the local user password")

                audit_str = "Changed password for local user %s" % cd["username"]
                ret, err = audit.audit("change_local_user_password",
                                       audit_str, request)
                # print ret, err
                if err:
                    raise Exception(err)
                return django.http.HttpResponseRedirect('/view_local_users?ack=changed_password')
            else:
                return_dict["form"] = form
                return django.shortcuts.render_to_response("update_local_user_password.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = "Modify local user's password"
        return_dict['tab'] = 'view_local_users_tab'
        return_dict["error"] = "Error modifying local user's password"
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def update_group_membership(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "created":
                return_dict['ack_message'] = "Local group successfully created"

        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'grpname'])
        if err:
            raise Exception(err)
        if 'grpname' not in req_ret:
            raise Exception('Invalid request, please use the menus.')

        gd, err = local_users.get_local_group(req_ret['grpname'])
        if err or (not gd):
            if err:
                raise Exception(err)
            else:
                raise Exception("Could not retrieve group information")

        # print 'gd - ', gd

        user_list, err = local_users.get_local_users()
        if err:
            raise Exception(err)

        # print 'user_list', user_list

        users = []
        primary_users = []
        permitted_users = []
        for u in user_list:
            if u['gid'] != gd['gid']:
                permitted_users.append(u)
            else:
                primary_users.append(u['username'])
            if u['username'] in gd['members']:
                users.append(u['username'])
        # print 'users', users
        #return_dict['primary_users'] = primary_users

        if request.method == "GET":
            # Return the form
            initial = {}
            initial['grpname'] = request.GET['grpname']
            initial['users'] = users
            form = local_user_forms.ModifyGroupMembershipForm(
                initial=initial, user_list=permitted_users)
            return_dict['form'] = form
            return django.shortcuts.render_to_response("update_group_membership.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = local_user_forms.ModifyGroupMembershipForm(
                request.POST, user_list=permitted_users)
            return_dict["form"] = form
            if form.is_valid():
                cd = form.cleaned_data
                users = cd['users']
                # print users

                audit_str = 'Modified group membership for group "%s". ' % cd['grpname']
                deleted_users = []
                for existing_user in gd['members']:
                    if existing_user not in users and existing_user not in primary_users:
                        deleted_users.append(existing_user)
                        # print 'delete user %s'%existing_user
                added_users = []
                for user in users:
                    if user not in gd['members'] and user not in primary_users:
                        added_users.append(user)
                        # print 'add user %s'%user
                if added_users:
                    audit_str += 'Added user(s) %s. ' % (','.join(added_users))
                if deleted_users:
                    audit_str += 'Removed user(s) %s.' % (
                        ','.join(deleted_users))
                # print audit_str
                #assert False
                ret, err = local_users.set_group_membership(
                    cd['grpname'], cd['users'])
                if err:
                    raise Exception('Error setting group membership: %s' % err)
                #assert False
                audit.audit("set_group_membership", audit_str, request)
                url = '/view_local_groups?ack=set_membership'
                return django.http.HttpResponseRedirect(url)
            else:
                return django.shortcuts.render_to_response("update_group_membership.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = 'users_groups_base.html'
        return_dict["page_title"] = 'Modify group membership'
        return_dict['tab'] = 'view_local_groups_tab'
        return_dict["error"] = 'Error modifying group membership'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


'''
def edit_local_user_gid(request):

  return_dict = {}
  try:
    group_list,err = local_users.get_local_groups()
    if err:
      raise Exception(err)
    req_ret, err = django_utils.get_request_parameter_values(request,['username'])
    if err:
        raise Exception(err)
    if 'username' not in req_ret:
        raise Exception('Invalid request, please use the menus.')

    username = req_ret['username']
    ud,err = local_users.get_local_user(username)
    if err:
      raise Exception(err)
    if not ud:
      raise Exception("Specified user information not found")
  
    if request.method == "GET":
      # Shd be an edit request
  
      # Set initial form values
      initial = {}
      initial['username'] = ud['username']
      initial['gid'] = ud['gid']
  
      form = local_user_forms.EditLocalUserGidForm(initial = initial, group_list = group_list)
  
      return_dict["form"] = form
      return django.shortcuts.render_to_response('edit_local_user_gid.html', return_dict, context_instance=django.template.context.RequestContext(request))
  
    else:
  
      # Shd be an save request
      form = local_user_forms.EditLocalUserGidForm(request.POST, group_list = group_list)
      return_dict["form"] = form
      if form.is_valid():
        cd = form.cleaned_data
        ret, err = local_users.set_local_user_gid(cd)
        if not ret:
          if err:
            raise Exception(err)
          else:
            raise Exception("Error saving user information")
  
        audit_str = "Modified local user's primary group %s"%cd["username"]
        audit.audit("modify_local_user_gid", audit_str, request)
  
        return django.http.HttpResponseRedirect('/view_local_users?ack=gid_changed')
  
      else:
        #Invalid form
        return django.shortcuts.render_to_response('edit_local_user_gid.html', return_dict, context_instance=django.template.context.RequestContext(request))
  except Exception, e:
    return_dict['base_template'] = 'users_groups_base.html'
    return_dict["page_title"] = "Modify local user's primary group"
    return_dict['tab'] = 'view_local_users_tab'
    return_dict["error"] = 'Error modifying local users primary group'
    return_dict["error_details"] = str(e)
    return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))
'''

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
