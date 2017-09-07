import os
import subprocess
import sys
import time

from integralstor import command, config


def _header():
    try:
        os.system('clear')
        print
        print 'IntegralSTOR USB utilities'
        print '----------------------------'
        print
        print
    except Exception, e:
        return None, str(e)
    else:
        return True, None

def mount_list():
    try:
        ret, err = _header()
        if err:
            print err

        mount_points, err = command.get_command_output(
            "cat /var/log/usb-mount.track | cut -d ':' -f 1", shell=True)
        if err:
            raise Exception(err)
        if not mount_points:
            raise Exception(' Nothing mounted!')
        dev_names, err = command.get_command_output(
            "cat /var/log/usb-mount.track | cut -d ':' -f 2", shell=True)
        if err:
            raise Exception(err)

        for i, mount in enumerate(mount_points, start=1):
            print ' %s. %s of /dev/%s' % (i, mount, dev_names[i - 1])
        print

    except Exception, e:
        print str(e)
        raw_input('\nPress any key to continue')
    else:
        raw_input('\nPress any key to continue')

def unmount():
    try:
        ret, err = _header()
        if err:
            print err

        mount_points, err = command.get_command_output(
            "cat /var/log/usb-mount.track | cut -d ':' -f 1", shell=True)
        if err:
            raise Exception(err)
        if not mount_points:
            raise Exception(' Nothing to unmount!')
        dev_names, err = command.get_command_output(
            "cat /var/log/usb-mount.track | cut -d ':' -f 2", shell=True)
        if err:
            raise Exception(err)

        count = []
        for i, mount in enumerate(mount_points, start=1):
            count.append(str(i))
            print ' %s. %s of /dev/%s' % (i, mount, dev_names[i - 1])
        print

        ch = ''
        while True:
            ch = raw_input(
                'Provide a number to unmount its corresponding device(0 to exit): ')
            if ch != '0' and ch not in count:
                print '\t- Provide a valid number'
            else:
                break

        shell_scripts_path, err = config.get_shell_scripts_path()
        if err:
            raise Exception(err)

        if ch != '0':
            ret, err = command.get_command_output(
                "/bin/bash %s/usb-mount.sh remove %s" % (shell_scripts_path, dev_names[int(ch) - 1]))
            if err:
                raise Exception(err)
            for r in ret:
                print '\n- %s' % r

    except Exception, e:
        print str(e)
        raw_input('\nPress any key to continue')
    else:
        raw_input('\nPress any key to continue')


def copy_to_from():
    try:
        source_path = ''
        target_path = ''
        while True:
            ret, err = _header()
            if err:
                print err

            print ' 1. Copy from USB drive'
            print ' 2. Copy to USB drive'
            print
            ch = raw_input(
                ' Please provide the appropriate choice (0 to exit): ')
            if ch == '0':
                raise Exception
            if ch not in ['1', '2']:
                continue
            else:
                break

        mount_points, err = command.get_command_output(
            "cat /var/log/usb-mount.track | cut -d ':' -f 1", shell=True)
        if err:
            raise Exception(err)
        if not mount_points:
            raise Exception(' No USB drive has been mounted!')

        cp_type = ''
        if ch == '1':
            cp_type = 'pull'
            ret, err = _header()
            print '[Copy from USB drive]'
        elif ch == '2':
            cp_type = 'push'
            ret, err = _header()
            print '[Copy to USB drive]'

        task_count = 0
        is_done_once = False
        sel_path = mount_points
        while True:
            # When task_count is 1, selecting USB path has been done.
            # Now change cp_type and begin to select ZFS data set path.
            if task_count == 1 and is_done_once == False:
                is_done_once = True
                ds_list, err = command.get_command_output(
                    'zfs get -H -o value mountpoint -t filesystem', shell=True)
                if err:
                    raise Exception(err)
                if not ds_list:
                    raise Exception('\tNo ZFS pools found.')

                sel_path = []
                for ds in ds_list:
                    if ds.count('/') > 1:
                        sel_path.append(ds)
                if not sel_path:
                    raise Exception('\tNo ZFS data sets found.')

                t = cp_type
                if t == 'pull':
                    print '\nSource path has been confirmed:\t%s' % source_path
                    print '\n\n'
                    print 'Proceed to select target path!'
                    cp_type = 'push'
                else:
                    print '\nTarget path has been confirmed:\t%s' % target_path
                    print '\n\n'
                    print 'Proceed to select source path!'
                    cp_type = 'pull'

            # When task_count is 2, source and target paths have been
            # selected, break out of the loop.
            if task_count == 2:
                break

            ch = ''
            print
            count = []
            for i, path in enumerate(sel_path, start=1):
                count.append(str(i))
                print ' %s. %s' % (i, path)
            print
            if cp_type == 'pull':
                print '\tCurrent path:\t%s' % source_path
                ch = raw_input(
                    'Select source path(number) to copy from (0 to exit, "done" to confirm): ')
            else:
                print '\tCurrent path:\t%s' % target_path
                ch = raw_input(
                    'Select target path(number) to copy to (0 to exit, "done" to confirm): ')
            if ch == '0':
                raise Exception
            elif str(ch).upper() == 'DONE':
                if cp_type == 'pull' and not source_path:
                    print '\nSource path cannot be left empty!'
                    continue
                elif cp_type == 'push' and not target_path:
                    print '\nTarget path cannot be left empty!'
                    continue
                task_count += 1
                continue

            if ch not in count:
                print '\t- Provide a valid number'
            else:
                print
                if cp_type == 'pull':
                    if not source_path:
                        source_path = '%s/' % sel_path[int(ch) - 1]
                    else:
                        source_path = '%s%s' % (
                            source_path, sel_path[int(ch) - 1])
                    print '\tSelected path:\t%s' % source_path
                    if not source_path.endswith('/'):
                        print '\tSelected a file'
                        task_count += 1
                        continue
                else:
                    if not target_path:
                        target_path = '%s/' % sel_path[int(ch) - 1]
                    else:
                        target_path_bak = target_path
                        target_path = '%s%s' % (
                            target_path, sel_path[int(ch) - 1])
                    print '\tSelected path:\t%s' % target_path
                    if not target_path.endswith('/'):
                        print '\tTarget needs to be a directory, not a file.'
                        target_path = target_path_bak
                        continue

                is_deeper = str(raw_input('\t- Traverse deeper? (y/n) : '))
                if is_deeper.upper() in ['Y']:
                    search_str = ''
                    if cp_type == 'pull':
                        search_str = 'ls --group-directories-first -p -1 %s' % source_path
                    else:
                        search_str = 'ls --group-directories-first -p -1 %s' % target_path

                    sel_path, err = command.get_command_output(
                        search_str, shell=True)
                    if err:
                        raise Exception(err)
                    if not sel_path:
                        print '\n\tEmpty directory, can not traverse further.'
                        task_count += 1
                        continue
                else:
                    task_count += 1
                    continue

        is_okay = False
        while True:
            print
            print 'Selected source path:\t%s' % source_path
            print 'Selected target path:\t%s' % target_path
            print
            ch = raw_input('\n\t- Confirm? (y/n) : ')
            if str(ch).upper() not in ['Y', 'N']:
                print 'Enter y/Y to confirm or n/N to exit'
                continue
            elif str(ch).upper() == 'Y':
                is_okay = True
                break
            else:
                raise Exception('\n\tExiting with out copying')

        if is_okay == True:
            #(ret, rc), err = command.execute_with_rc(['/usr/bin/rsync -avirPO --delete %s %s' % (source_path, target_path)],shell=True, run_as_user_name='root')
            # print ret, rc, err
            print
            cmd = '/usr/bin/rsync -avirPO --stats %s %s' % (
                source_path, target_path)
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

            while True:
                out = p.stderr.read(1)
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    sys.stdout.write(out)
                    sys.stdout.flush()

    except Exception, e:
        print str(e)
        raw_input('\nPress any key to continue')
    else:
        raw_input('\nPress any key to continue')


if __name__ == '__main__':
    try:
        while True:
            ret, err = _header()
            if err:
                print err
                raise Exception
            print ' 1. Mount list'
            print ' 2. Copy to/from USB drive'
            print ' 3. Unmount USB drive'
            print
            ch = raw_input(
                'Enter a number to perform the corresponding operation (0 to exit): ')
            if ch == '0':
                break
            elif ch not in ['1', '2', '3']:
                print '\t- Please provide a valid choice from the list.'
                time.sleep(2)
                continue
            elif ch == '1':
                mount_list()
            elif ch == '2':
                copy_to_from()
            elif ch == '3':
                unmount()

    except Exception, e:
        sys.exit(1)
    else:
        sys.exit(0)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
