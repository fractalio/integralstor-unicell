
from integralstor import networking, command
import os
import socket
import sys


def display_config():

    try:
        hostname = socket.gethostname()
        if hostname:
            print "Hostname : %s" % hostname
        else:
            print "Hostname : Not set"
        print
        interfaces, err = networking.get_interfaces()
        if interfaces:
            for name, interface in interfaces.items():
                if name.startswith('lo'):
                    continue
                print 'Interface : %s. ' % name
                if 'AF_INET' in interface['addresses']:
                    print 'IP Address : %s, Netmask %s. ' % (interface['addresses']['AF_INET'][0]['addr'], interface['addresses']['AF_INET'][0]['netmask']),
                else:
                    print 'No address assigned. ',
                if 'slave_to' in interface:
                    print 'NIC bonded slave to %s.' % interface['slave_to'],
                if 'bonding_master' in interface:
                    print 'NIC bonded master. ',
                    bonding_type, err = networking.get_bonding_type(name)
                    if bonding_type:
                        print 'Bonding type %d. ' % bonding_type
                print 'Carrier status : %s. ' % interface['carrier_status'],
                print 'NIC status : %s. ' % interface['up_status']
                print
        else:
            if err:
                print 'Error retrieving interface information : %s' % err

        dns_list, err = networking.get_name_servers()
        if dns_list:
            print "DNS lookup servers :",
            print ', '.join(dns_list)
            print
    except Exception, e:
        print "Error displaying system configuration : %s" % e
        return -1
    else:
        return 0


if __name__ == '__main__':

    os.system('clear')
    print
    print
    print
    print
    print "IntegralSTOR Node configuration"
    print "----------------------------------"
    rc = display_config()
    print
    print
    sys.exit(rc)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
