
from integralstor import networking, command, config
import os
import socket
import sys


def display_status():

    try:
        hostname = socket.gethostname()
        use_salt, err = config.use_salt()
        if err:
            raise Exception(err)
        if use_salt:
            print "Salt master service status :",
            (r, rc), err = command.execute_with_rc(
                'service salt-master status')
            if err:
                raise Exception(err)
            l, err = command.get_output_list(r)
            if err:
                raise Exception(err)
            if l:
                print '\n'.join(l)
            else:
                l, err = command.get_error_list(r)
                if err:
                    raise Exception(err)
                if l:
                    print '\n'.join(l)
            print "Salt minion service status :",
            (r, rc), err = command.execute_with_rc(
                'service salt-minion status')
            if err:
                raise Exception(err)
            l, err = command.get_output_list(r)
            if err:
                raise Exception(err)
            if l:
                print '\n'.join(l)
            else:
                l, err = command.get_error_list(r)
                if err:
                    raise Exception(err)
                print l
                if l:
                    print '\n'.join(l)
        print "Samba service status :",
        (r, rc), err = command.execute_with_rc('service smb status')
        if err:
            raise Exception(err)
        l, err = command.get_output_list(r)
        if err:
            raise Exception(err)
        if l:
            print '\n'.join(l)
        else:
            l, err = command.get_error_list(r)
            if err:
                raise Exception(err)
            if l:
                print '\n'.join(l)
        print "Winbind service status :",
        (r, rc), err = command.execute_with_rc('service winbind status')
        if err:
            raise Exception(err)
        l, err = command.get_output_list(r)
        if err:
            raise Exception(err)
        if l:
            print '\n'.join(l)
        else:
            l, err = command.get_error_list(r)
            if err:
                raise Exception(err)
            if l:
                print '\n'.join(l)
    except Exception, e:
        print "Error displaying system status : %s" % e
        return -1
    else:
        return 0


if __name__ == '__main__':

    os.system('clear')
    print
    print
    print
    print "IntegralSTOR configuration"
    print "----------------------------------"
    rc = display_status()
    print
    print
    # sys.exit(rc)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
