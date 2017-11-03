import django.template
import django
from django.contrib.auth.decorators import login_required
import django.http

import os
import os.path

from integralstor import tasks_utils, django_utils, audit, config, command, datetime_utils


def view_background_tasks(request):
    return_dict = {}
    try:
        if "ack" in request.GET:
            if request.GET["ack"] == "deleted":
                return_dict['ack_message'] = "Background task successfully removed"
            if request.GET["ack"] == "stopped":
                return_dict['ack_message'] = "Background task successfully stopped"
        tasks, err = tasks_utils.get_tasks()
        if err:
            raise Exception(err)
        for task in tasks:
            initiate_time_str, err = datetime_utils.convert_from_epoch(
                task['initiate_time'], return_format='str', str_format='%c', to='local')
            if err:
                raise Exception(err)
            create_time_str, err = datetime_utils.convert_from_epoch(
                task['create_time'], return_format='str', str_format='%c', to='local')
            if err:
                raise Exception(err)
            task['initiate_time'] = initiate_time_str
            task['create_time'] = create_time_str

        return_dict["tasks"] = tasks
        return django.shortcuts.render_to_response("view_background_tasks.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "scheduler_base.html"
        return_dict["page_title"] = 'Background tasks'
        return_dict['tab'] = 'view_background_tasks_tab'
        return_dict["error"] = 'Error retriving background tasks'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def delete_background_task(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'task_id'])
        if err:
            raise Exception(err)
        if 'task_id' not in req_ret:
            raise Exception('Invalid request. Please use the menus.')

        task, err = tasks_utils.get_task(req_ret['task_id'])
        if err:
            raise Exception(err)

        ret, err = tasks_utils.delete_task(req_ret['task_id'])
        if err:
            raise Exception(err)

        audit.audit("remove_background_task",
                    task['description'], request)
        return django.http.HttpResponseRedirect('/view_background_tasks?ack=deleted')
    except Exception, e:
        return_dict['base_template'] = "scheduler_base.html"
        return_dict["page_title"] = 'Background tasks'
        return_dict['tab'] = 'view_background_tasks_tab'
        return_dict["error"] = 'Error removing background task'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def stop_background_task(request):
    return_dict = {}
    try:
        req_ret, err = django_utils.get_request_parameter_values(request, [
                                                                 'task_id'])
        if err:
            raise Exception(err)
        if 'task_id' not in req_ret:
            raise Exception('Invalid request. Please use the menus.')

        task, err = tasks_utils.get_task(req_ret['task_id'])
        if err:
            raise Exception(err)

        ret, err = tasks_utils.stop_task(req_ret['task_id'])
        if err:
            raise Exception(err)

        audit.audit("stop_background_task",
                    task['description'], request)
        return django.http.HttpResponseRedirect('/view_background_tasks?ack=stopped')
    except Exception, e:
        return_dict['base_template'] = "scheduler_base.html"
        return_dict["page_title"] = 'Background tasks'
        return_dict['tab'] = 'view_background_tasks_tab'
        return_dict["error"] = 'Error stopping background task'
        return_dict["error_details"] = str(e)
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


def view_task_details(request, task_id):
    return_dict = {}
    try:
        task, err = tasks_utils.get_task(int(task_id))
        if err:
            raise Exception(err)
        return_dict['task'] = task
        subtasks, err = tasks_utils.get_subtasks(int(task_id))
        if err:
            raise Exception(err)
        return_dict["subtasks"] = subtasks
        # print subtasks, err
        task_output = ""
        log_dir, err = config.get_tasks_log_dir_path()
        if err:
            raise Exception(err)
        log_file_path = '%s/%d.log' % (log_dir, int(task_id))
        if os.path.isfile(log_file_path):
            lines, err = command.get_command_output("wc -l %s" % log_file_path)
            no_of_lines = lines[0].split()[0]
            # print no_of_lines
            if int(no_of_lines) <= 41:
                # This code always updates the 0th element of the command list.
                # This is assuming that we will only have one long running
                # command.
                with open(log_file_path) as output:
                    task_output = task_output + ''.join(output.readlines())
            else:
                first, err = command.get_command_output(
                    "head -n 5 %s" % log_file_path, shell=True)
                if err:
                    print err
                last, err = command.get_command_output(
                    "tail -n 20 %s" % log_file_path, shell=True)
                if err:
                    print err
                # print last
                task_output = task_output + '\n'.join(first)
                task_output = task_output + "\n.... \n ....\n"
                task_output = task_output + '\n'.join(last)
        return_dict['task_output'] = task_output

        return django.shortcuts.render_to_response("view_task_details.html", return_dict, context_instance=django.template.context.RequestContext(request))
    except Exception, e:
        return_dict['base_template'] = "scheduler_base.html"
        return_dict["page_title"] = 'Background jobs'
        return_dict['tab'] = 'view_background_tasks_tab'
        return_dict["error"] = 'Error retriving background task details'
        return_dict["error_details"] = e
        return django.shortcuts.render_to_response("logged_in_error.html", return_dict, context_instance=django.template.context.RequestContext(request))


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
