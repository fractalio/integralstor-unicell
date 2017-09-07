import os
import subprocess
import shlex
import pwd


def execute(cmd=None, shell=False):
    """Given a command specified in the parameter, it spawns a subprocess to execute it and returns the output" and errors"""

    ret = None
    try:

        if not cmd:
            raise Exception('No command supplied')

        comm_list = cmd.split()

        proc = subprocess.Popen(
            comm_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        ret = proc.communicate()

    except Exception, e:
        return None, 'Error executing command : %s' % str(e)
    else:
        return ret, None


def _demote(uid, gid):
    """Change the uid/gid of the running process."""
    def result():
        os.setgid(gid)
        os.setuid(uid)
    return result


def execute_with_rc(cmd=None, shell=False, run_as_user_name=None):
    """Given a command specified in the parameter, it spawns a subprocess to execute it and returns the output and errors"""

    ret = None
    rc = -1

    try:
        if not cmd:
            raise Exception('No command supplied')

        if shell:
            comm_list = cmd
        else:
            # Converting to str as the older python version of shlex in
            # gridcell does not support unicode
            comm_list = shlex.split(str(cmd))
            # print 'comm_list is ', comm_list

        if run_as_user_name is not None:
            # print 'demoting to ', run_as_user_name
            pw_record = pwd.getpwnam(run_as_user_name)
            # print pw_record
            if not pw_record:
                raise Exception('Specified run as user does not exist!')
            user_uid = pw_record.pw_uid
            user_gid = pw_record.pw_gid
            # print user_uid
            # print user_gid
            proc = subprocess.Popen(comm_list, preexec_fn=_demote(
                user_uid, user_gid), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        else:
            proc = subprocess.Popen(
                comm_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        ret = proc.communicate()

        if proc:
            rc = proc.returncode
    except Exception, e:
        return None, 'Error executing command with rc : %s' % str(e)
    else:
        return (ret, rc), None


def execute_with_conf(cmd=None, response='y'):
    """ Given a command specified in the parameter, it spawns a subprocess to execute it and returns the output" and errors.
    The difference between this and execute() is that is used for commands that require a y/n confirmation."""

    ret = None
    try:
        if not cmd:
            raise Exception('No command supplied')

        comm_list = cmd.split()
        response = "%s\n" % response

        proc = subprocess.Popen(
            comm_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.write(response)
        ret = proc.communicate()
    except Exception, e:
        return None, 'Error executing command with conf  : %s' % str(e)
    else:
        return ret, None


def execute_with_conf_and_rc(cmd=None, response='y'):
    """ Given a command specified in the parameter, it spawns a subprocess to execute it and returns the output" and errors.
    The difference between this and execute() is that is used for commands that require a y/n confirmation."""

    rc = -1
    ret = None
    try:
        if not cmd:
            raise Exception('No command supplied')
        comm_list = cmd.split()
        response = "%s\n" % response

        proc = None
        proc = subprocess.Popen(
            comm_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.write(response)
        ret = proc.communicate()

        if proc:
            rc = proc.returncode
    except Exception, e:
        return None, 'Error executing command with conf  : %s' % str(e)
    else:
        return (ret, rc), None


def get_command_output(cmd, check_rc=True, shell=False, run_as_user_name=None):
    """ A wrapper around execute to return the output (and errors) of a command only if there is no error."""

    ol = None
    lines = None
    try:
        ret = None
        rc = -1
        tup, err = execute_with_rc(cmd, shell, run_as_user_name)
        if tup:
            (ret, rc) = tup
        if err:
            raise Exception(err)
        if check_rc:
            # Since only some commands give a 0 vs non 0 return code..
            if rc == 0:
                lines, er = get_output_list(ret)
                if er:
                    raise Exception(er)
            else:
                err = ''
                tl, er = get_output_list(ret)
                if er:
                    raise Exception(er)
                if tl:
                    err = ''.join(tl)
                tl, er = get_error_list(ret)
                if er:
                    raise Exception(er)
                if tl:
                    err = err + ''.join(tl)
                raise Exception(err)
        else:
            lines, er = get_output_list(ret)
            if er:
                raise Exception(er)
    except Exception, e:
        return None, 'Error returning output after executing command %s : %s' % (e, cmd)
    else:
        return lines, None


def get_output_list(tup):
    """ Given the tuple returned by execute(), it returns the output list"""
    output_list = []
    try:
        if tup and tup[0]:
            for line in tup[0].splitlines():
                output_list.append(line)
    except Exception, e:
        return None, 'Error returning command output list: %s' % str(e)
    else:
        return output_list, None


def get_error_list(tup):
    """ Given the tuple returned by execute(), it returns the error list"""
    err_list = []
    try:
        if tup and tup[1]:
            for line in tup[1].splitlines():
                err_list.append(line)
    except Exception, e:
        return None, 'Error returning command error list: %s' % str(e)
    else:
        return err_list, None


def get_conf_output_list(tup):
    """ Given the tuple returned by execute_with_conf(), it returns the output list. 
    Requires a kudge because we need to ignore the first line which may be the prompt from the command"""
    output_list = []
    try:
        first_line = True
        if tup and tup[0]:
            for line in tup[0].splitlines():
                if first_line:
                    index = line.find(r'(y/n)')
                    output_list.append(line[index + 5:])
                    # output_list.append(line)
                    first_line = False
                else:
                    output_list.append(line)
    except Exception, e:
        return None, 'Error returning command conf output list: %s' % str(e)
    else:
        return output_list, None


def get_conf_error_list(tup):
    """ Given the tuple returned by execute_with_conf(), it returns the error list. 
    Requires a kudge because we need to ignore the first line which may be the prompt from the command"""

    err_list = []
    try:
        # kludge!!
        first_line = True
        if tup and tup[1]:
            for line in tup[1].splitlines():
                if not first_line:
                    err_list.append(line)
                first_line = False
    except Exception, e:
        return None, 'Error returning command conf error list: %s' % str(e)
    else:
        return err_list, None


def main():

    c = 'gluster volume info all --xml'
    # print 'Executing : '+c
    t1 = execute(c)

    el = get_error_list(t1)
    if el:
        print 'Errors'
        for i in el:
            print i

    print 'Output'
    ol = get_output_list(t1)
    if ol:
        for i in ol:
            print i


if __name__ == "__main__":
    main()


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
