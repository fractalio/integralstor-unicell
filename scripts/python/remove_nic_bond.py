import os
import sys
from integralstor import networking, config, command


def remove_bond():
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
        print 'IntegralSTOR NIC Bonding'
        print '---------------------------------'
        print
        print
        print 'Active bond(s): \n'

        bm, err = networking.get_bonding_masters()
        if err:
            raise Exception(err)
        bid, err = networking.get_bonding_info_all()
        if err:
            raise Exception(err)

        avail_if = []
        for if_name, iface in interfaces.items():
            if if_name in bm:
                print '\t- %s' % if_name
                avail_if.append(if_name)
        print "\n"
        if not avail_if:
            raise Exception('There is nothing to remove!')

        bond_name = None
        is_name = False
        while is_name is False:
            bond_name = raw_input('To remove a bond, provide its name: ')
            if bond_name not in avail_if:
                print "\t- Can't remove %s, no such bond exists. Please provide another one.\n" % bond_name
            else:
                is_name = True

        ret, err = networking.delete_bond(bond_name)
        if not ret:
            if err:
                raise Exception('Error removing bond: %s' % err)
            else:
                raise Exception("Couldn't remove bond")
        if ret:
            print "\n\tBond removed!\n"

        print
        print 'Regenerating manifest and status.'
        python_scripts_path, err = config.get_python_scripts_path()
        if err:
            raise Exception(err)
        python_scripts_path, err = config.get_python_scripts_path()
        if err:
            raise Exception(err)
        status_path, err = config.get_system_status_path()
        if err:
            raise Exception(err)

        ret, err = command.get_command_output(
            "python %s/generate_manifest.py %s" % (python_scripts_path, status_path))
        if err:
            raise Exception(err)
        ret, err = command.get_command_output(
            "python %s/generate_status.py %s" % (python_scripts_path, status_path))
        if err:
            raise Exception(err)
        print 'Regenerating manifest and status... Done'
        print
    except Exception, e:
        print "Error: %s" % e
        print
        return -1
    else:
        return 0


if __name__ == '__main__':

    rc = remove_bond()
    sys.exit(rc)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
