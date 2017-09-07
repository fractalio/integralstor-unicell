import django
import django.template

from integral_view.forms import pki_forms
from integralstor import audit, django_utils, pki

import os


def view_ssl_certificates(request):
    return_dict = {}
    try:
        cert_list, err = pki.get_ssl_certificates()
        if err:
            raise Exception(err)

        if "ack" in request.GET:
            if request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "The certificate has been successfully deleted"
            elif request.GET["ack"] == "created_self_signed_cert":
                return_dict['ack_message'] = "A self signed SSL certificate has been successfully created"
            elif request.GET["ack"] == "uploaded_cert":
                return_dict['ack_message'] = "A new SSL certificate has been successfully uploaded"
        return_dict["cert_list"] = cert_list
        return django.shortcuts.render_to_response('view_ssl_certificates.html', return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'SSL certificates'
        return_dict['tab'] = 'certificates_tab'
        return_dict["error"] = 'Error loading SSL certificates'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_ssl_certificate(request):

    return_dict = {}
    try:
        ret, err = django_utils.get_request_parameter_values(request, ['name'])
        if err:
            raise Exception(err)
        if 'name' not in ret:
            raise Exception("Invalid request, please use the menus.")
        name = ret['name']
        return_dict["name"] = name

        if request.method == "GET":
            # Return the conf page
            return django.shortcuts.render_to_response("delete_ssl_certificate_conf.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:

            ret, err = pki.delete_ssl_certificate(name)
            if err:
                raise Exception(err)

            audit_str = "Deleted SSL certificate name '%s'" % name
            audit.audit("delete_certificate", audit_str,
                        request)
            return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Delete a SSL certificate'
        return_dict['tab'] = 'certificates_tab'
        return_dict["error"] = 'Error deleting SSL certificate'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def create_self_signed_ssl_certificate(request):
    return_dict = {}
    try:
        if request.method == "GET":
            # Return the conf page
            form = pki_forms.CreateSelfSignedCertForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response("create_self_signed_ssl_certificate.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = pki_forms.CreateSelfSignedCertForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("create_self_signed_ssl_certificate.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            ret, err = pki.generate_self_signed_ssl_certificate(cd)
            if err:
                raise Exception(err)

            audit_str = "Created a self signed SSL certificate named %s" % cd['name']
            audit.audit("create_self_signed_certificate",
                        audit_str, request)
            return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=created_self_signed_cert')
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Create a self signed SSL certificate'
        return_dict['tab'] = 'certificates_tab'
        return_dict["error"] = 'Error creating a self signed SSL certificate'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_ssl_certificate(request):
    return_dict = {}
    try:
        if request.method == "GET":
            # Return the conf page
            form = pki_forms.UploadCertForm()
            return_dict['form'] = form
            return django.shortcuts.render_to_response("upload_ssl_certificate.html", return_dict, context_instance=django.template.context.RequestContext(request))
        else:
            form = pki_forms.UploadCertForm(request.POST)
            return_dict['form'] = form
            if not form.is_valid():
                return django.shortcuts.render_to_response("upload_ssl_certificate.html", return_dict, context_instance=django.template.context.RequestContext(request))
            cd = form.cleaned_data
            ret, err = pki.upload_ssl_certificate(cd)
            if err:
                raise Exception(err)

            audit_str = "Uploaded a SSL certificate named %s" % cd['name']
            audit.audit("upload_certificate", audit_str,
                        request.META)
            return django.http.HttpResponseRedirect('/view_ssl_certificates?ack=uploaded_cert')
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Upload a SSL certificate'
        return_dict['tab'] = 'certificates_tab'
        return_dict["error"] = 'Error uploading a SSL certificate'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_ssh_user_key(request):
    return_dict = {}
    try:
        user = request.GET.get('user', 'replicator')
        return_dict["selected_user"] = user
        if request.method == 'POST':
            # This works for user deleting the key files. This should be moved
            # to a new function in itself
            authorized_key = request.POST.get('authorized_key', None)
            if authorized_key:
                description = ""
                user = request.POST.get("selected_user")
                key = request.POST.get("authorized_key")
                description = "%s" % (user)
                audit.audit("remove_ssh_user_key", description, request)
                files = open((pki._get_authorized_file(user)), 'r').readlines()
                authorized_keys = open(pki._get_authorized_file(user), 'w')
                for file in files:
                    if key.strip() != file.strip():
                        authorized_keys.write(file)
                ack_message = "key_deleted"
            # This works for user uploading new keys
            else:
                desscription = ""
                authorized_key = request.FILES.get('pub_key')
                user = request.POST.get('user')
                description = "%s  %s" % (user, authorized_key)
                audit.audit("upload_ssh_user_key", description, request)

                with open('/%s/authorized_keys' % (pki._get_ssh_dir(user)), 'ab') as destination:
                    for chunk in authorized_key.chunks():
                        destination.write(chunk)
                perm, err = pki.update_ssh_dir_permissions(user)
                if err:
                    raise Exception(err)
                ack_message = "key_added"
            return django.http.HttpResponseRedirect("/view_user_ssh_keys/?ack=%s&user=%s" % (ack_message, user))
        elif request.method == 'GET':
            return django.shortcuts.render_to_response("upload_ssh_user_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Upload a Public Key'
        return_dict['tab'] = 'upload_public_key_tab'
        return_dict["error"] = 'Error adding Public key. Please check the value'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def upload_ssh_host_key(request):
    return_dict = {}
    try:
        user = request.GET.get('user', 'replicator')
        return_dict["selected_user"] = user

        if request.method == 'POST':
            authorized_key = request.POST.get('authorized_key', None)
            # This is a delete operation. authorized_key in post is delete and
            # as a file is file upload
            if authorized_key:
                user = request.POST.get("selected_user")
                key = request.POST.get("authorized_key")
                description = "%s" % (user)
                audit.audit("remove_ssh_host_key", description, request)

                files = open((pki._get_known_hosts(user)), 'r').readlines()
                authorized_keys = open(pki._get_known_hosts(user), 'w')
                for file in files:
                    if key.strip() != file.strip():
                        authorized_keys.write(file)
                ack_message = "host_deleted"
            else:
                authorized_key = request.FILES.get('pub_key')
                ip = request.POST.get('ip')
                user = request.POST.get('user', 'replicator')
                description = "%s %s  %s" % (user, ip, authorized_key)
                audit.audit("upload_ssh_host_key", description, request)

                hosts_file = pki._get_known_hosts(user)
                # print hosts_file
                with open("/tmp/hosts_file", 'wb+') as destination:
                    for chunk in authorized_key.chunks():
                        destination.write(chunk)
                with open("/tmp/hosts_file", 'r') as key:
                    data = key.read()
                # print data
                with open(hosts_file, 'ab') as key:
                    key.write(ip + " " + data)
                perm, err = pki.update_ssh_dir_permissions(user)
                if err:
                    raise Exception(err)
                ack_message = "host_added"
            return django.http.HttpResponseRedirect("/view_known_hosts_ssh_keys/?ack=%s&user=%s" % (ack_message, user))
        elif request.method == 'GET':
            return django.shortcuts.render_to_response("upload_ssh_host_key.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Upload a Host Key'
        return_dict['tab'] = 'host_ssh_keys_tab'
        return_dict["error"] = 'Error adding host key. Please check the value'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_user_ssh_keys(request):
    return_dict = {}
    try:
        user = request.GET.get('user', 'replicator')
        return_dict["selected_user"] = user

        key, err = pki.get_ssh_key(user)
        if err:
            raise Exception(err)
        return_dict['ssh_key'] = key

        # Get all the users authorized key files
        authorized_keys_file = pki._get_authorized_file(user)
        if os.path.isfile(authorized_keys_file):
            return_dict["authorized_keys"] = open(
                authorized_keys_file, 'r').readlines()

        if "ack" in request.GET:
            if request.GET["ack"] == "key_deleted":
                return_dict['ack_message'] = "The Public Key has been successfully deleted"
            if request.GET["ack"] == "key_added":
                return_dict['ack_message'] = "The Public Key has been successfully added"

        return django.shortcuts.render_to_response("view_user_ssh_keys.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'User SSH keys'
        return_dict['tab'] = 'user_ssh_keys_tab'
        return_dict["error"] = 'Error fetching public keys'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_known_hosts_ssh_keys(request):
    return_dict = {}
    try:
        user = request.GET.get('user', 'replicator')
        return_dict["selected_user"] = user

        host_key, err = pki.get_ssh_host_identity_key()
        if err:
            raise Exception(err)
        return_dict['host_key'] = host_key

        # Get users host key files
        hosts_keys_file = pki._get_known_hosts(user)
        if os.path.isfile(hosts_keys_file):
            return_dict["hosts_keys"] = open(hosts_keys_file, 'r').readlines()

        if "ack" in request.GET:
            if request.GET["ack"] == "host_deleted":
                return_dict['ack_message'] = "The Host Key has been successfully deleted"
            if request.GET["ack"] == "host_added":
                return_dict['ack_message'] = "The Host Key has been successfully added"

        return django.shortcuts.render_to_response("view_known_hosts_ssh_keys.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "key_management_base.html"
        return_dict["page_title"] = 'Known hosts SSH fingerprint'
        return_dict['tab'] = 'host_ssh_keys_tab'
        return_dict["error"] = 'Error fetching known hosts SSH fingerprints'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
