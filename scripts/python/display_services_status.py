import os
import sys
from integralstor import services_management


def display_services_status():
    try:
        os.system('clear')
        print "IntegralSTOR Services Status"
        print "-----------------------------"
        print
        services_d, err = services_management.get_sysd_services_status()
        if err:
            raise Exception(err)

        for name, service in services_d.items():
            print
            print "\t%s: %s" % (name, service['info']['status']['status_str'].upper())
        print

        while True:
            print
            check = raw_input(
                "To view detailed status press 'y', otherwise, press any other key to exit: ")
            if check.lower() == 'y':
                os.system('clear')
                for name, service in services_d.items():
                    print
                    print "Service: %s" % name
                    print
                    print "\t%s" % service['info']['status']['output_str']
                    print "--" * 10
            else:
                break

    except Exception, e:
        print "Error: %s" % e
        return -1
    else:
        return 0


if __name__ == '__main__':
    rc = display_services_status()
    sys.exit(rc)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
