import os, sys
from integralstor_common import networking

def create_bond ():
  try:
    os.system ('clear')
    interfaces, err = networking.get_interfaces ()
    if err:
      raise Exception ('Error retrieving interface information : %s' %err)
    if not interfaces:
      raise Exception ('No interfaces detected')

    print '\n\nIntegralstor Unicell NIC Bonding'
    print '---------------------------------\n\n'
    print 'Available interfaces: \n'

    bm, err = networking.get_bonding_masters ()
    if err:
      raise Exception (err)
    bid, err = networking.get_bonding_info_all()
    if err:
      raise Exception(err) 
    
    avail_if = []
    for if_name, iface in interfaces.items():
      ret, err = networking.get_ip_info (if_name)
      if ret:
        continue
      if if_name.startswith('lo') or if_name in bm or if_name in bid['by_slave']:
        continue
      print '\t- %s'%if_name
      avail_if.append (if_name)
    print "\n"
  
    bond_name = None
    is_name = False
    while is_name is False:
      bond_name = raw_input ('Provide bond name: ')
      if bond_name in interfaces or bond_name.startswith('lo'):
        print "\t- Can't assign %s, it's been taken already. Please provide another one.\n" %bond_name
      else:
        is_name = True

    print "\n"
    slaves = []
    is_ok = False
    while is_ok is False:
      s = raw_input ("\nEnter slaves from the shown interface list, separated by comma. - ").split (",") 
      slaves = [inner.strip () for inner in s]
      for slave in slaves:
        if slave not in avail_if:
          break

      else:
        is_ok = True
        print ("\nSelecetd slaves: %s") %slaves
        confirm = raw_input ("\t- Confirm selected slaves (y/n)? ")
        if confirm.lower () in ["n"]:
          is_ok = False
    
    print "\n"
    is_ok = False
    while is_ok is False:
      mode = raw_input ("Available modes [4]802.3ad, [6]balance-alb] - 4 or 6?: ")
      if mode in ["4", "6"]:
        is_ok = True
    
    ret, err = networking.create_bond (bond_name, slaves, int(mode))
    if not ret:
        if err:
          raise Exception('Error creating bond: %s' %err)
        else:
          raise Exception("Couldn't create bond")
    if ret:
        print "\nBond created!\n"
    
  except Exception, e:
    print "Error: %s" %e
    return -1
  else:
    return 0


if __name__ == '__main__':

  rc = create_bond ()
  sys.exit (rc)
      
