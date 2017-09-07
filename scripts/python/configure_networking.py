import os
import socket
import re
import sys
import time
from integralstor import networking, command, config


def configure_interface():

    try:
        os.system('clear')
        interfaces, err = networking.get_interfaces()
        if err:
            raise Exception(
                'Error retrieving interface information : %s' % err)
        if not interfaces:
            raise Exception('No interfaces detected')
        print
        print
        print 'IntegralSTOR interface configuration'
        print '--------------------------------------------'
        print
        print
        print 'Current network interfaces : '
        print
        for if_name, iface in interfaces.items():
            if if_name.startswith('lo'):
                continue
            print '- %s' % if_name
        print

        valid_input = False
        while not valid_input:
            ifname = raw_input(
                'Enter the name of the interface that you wish to configure : ')
            if ifname not in interfaces or ifname.startswith('lo'):
                print 'Invalid interface name'
            else:
                valid_input = True
        print
        ip_info, err = networking.get_ip_info(ifname)
        '''
    if err:
      raise Exception('Error retrieving interface information : %s'%err)
    '''
        if ip_info:
            ip = ip_info["ipaddr"]
            netmask = ip_info["netmask"]
            if "default_gateway" in ip_info:
                gateway = ip_info["default_gateway"]
            else:
                gateway = None
        else:
            ip = None
            netmask = None
            gateway = None

        old_boot_proto, err = networking.get_interface_bootproto(ifname)
        if err:
            raise Exception(
                'Error retrieving interface information : %s' % err)
            time.sleep(5)

        config_changed = False

        str_to_print = "Configure for DHCP or static addressing (dhcp/static)? : "
        valid_input = False
        while not valid_input:
            input = raw_input(str_to_print)
            if input:
                if input.lower() in ['static', 'dhcp']:
                    valid_input = True
                    boot_proto = input.lower()
                    if boot_proto != old_boot_proto:
                        config_changed = True
            if not valid_input:
                print "Invalid value. Please try again."
        print

        if boot_proto == 'static':
            if ip:
                str_to_print = "Enter IP address (currently %s, press enter to retain current value) : " % ip
            else:
                str_to_print = "Enter IP address (currently not set) : "
            valid_input = False
            while not valid_input:
                input = raw_input(str_to_print)
                if input:
                    ok, err = networking.validate_ip(input)
                    if err:
                        raise Exception('Error validating IP : %s' % err)
                    if ok:
                        valid_input = True
                        ip = input
                        config_changed = True
                elif ip:
                    valid_input = True
                if not valid_input:
                    print "Invalid value. Please try again."
            print

            if netmask:
                str_to_print = "Enter netmask (currently %s, press enter to retain current value) : " % netmask
            else:
                str_to_print = "Enter netmask (currently not set) : "
            valid_input = False
            while not valid_input:
                input = raw_input(str_to_print)
                if input:
                    ok, err = networking.validate_netmask(input)
                    if err:
                        raise Exception('Error validating netmask : %s' % err)
                    if ok:
                        valid_input = True
                        netmask = input
                        config_changed = True
                elif netmask:
                    valid_input = True
            if not valid_input:
                print "Invalid value. Please try again."
            print

            if gateway:
                str_to_print = "Enter gateway (currently %s, press enter to retain current value) : " % gateway
            else:
                str_to_print = "Enter gateway (currently not set) : "
            valid_input = False
            while not valid_input:
                input = raw_input(str_to_print)
                if input:
                    ok, err = networking.validate_ip(input)
                    if err:
                        raise Exception('Error validating gateway : %s' % err)
                    if ok:
                        valid_input = True
                        gateway = input
                        config_changed = True
                elif gateway:
                    valid_input = True
                if not valid_input:
                    print "Invalid value. Please try again."
            print
        if config_changed:
            d = {}
            d['addr_type'] = boot_proto
            if boot_proto == 'static':
                d['ip'] = ip
                d['netmask'] = netmask
                d['default_gateway'] = gateway
            ret, err = networking.update_interface_ip(ifname, d)
            if not ret:
                if err:
                    raise Exception(
                        'Error changing interface address : %s' % err)
                else:
                    raise Exception('Error changing interface address')

            restart = False
            print
            print
            valid_input = False
            while not valid_input:
                str_to_print = 'Restart network services now (y/n) :'
                print
                input = raw_input(str_to_print)
                if input:
                    if input.lower() in ['y', 'n']:
                        valid_input = True
                        if input.lower() == 'y':
                            restart = True
                if not valid_input:
                    print "Invalid value. Please try again."
            print

            if restart:
                ret, err = networking.restart_networking()
                if not ret:
                    if err:
                        raise Exception(err)
                    else:
                        raise Exception("Couldn't restart.")

                use_salt, err = config.use_salt()
                if err:
                    raise Exception(err)
                if use_salt:
                    (r, rc), err = command.execute_with_rc(
                        'service salt-minion restart')
                    if err:
                        raise Exception(err)
                    if rc == 0:
                        print "Salt minion service restarted succesfully."
                    else:
                        print "Error restarting salt minion services."
                        raw_input('Press enter to return to the main menu')
                        return -1
        else:
            print
            print
            raw_input(
                'No changes have been made to the configurations. Press enter to return to the main menu.')
            return 0

    except Exception, e:
        print "Error configuring network settings : %s" % e
        return -1
    else:
        return 0


if __name__ == '__main__':

    # print sys.argv
    if len(sys.argv) != 2:
        print 'Incorrect usage. Usage : configure_networking interface|dns|gateway'
        sys.exit(-1)
    if sys.argv[1] not in ['interface']:
        print 'Incorrect usage. Usage : configure_networking interface|dns|gateway'
        sys.exit(-1)
    if sys.argv[1] == 'interface':
        rc = configure_interface()
    sys.exit(rc)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
