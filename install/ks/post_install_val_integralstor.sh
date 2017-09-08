#!/bin/sh
echo '''
	#################################################
	#						#
	#						#
	#     ///***UNICELL VALIDATION SCRIPT***\\\     #	
	#						#
	#						#
	#################################################
'''
echo "######################	Partition Scheme Validation 		######################"
df -h /boot -t ext4 >> /tmp/tmp_part_info || echo "Partitioning '/boot --fstype ext4' is NOT done"
df -h /home -t ext4 >> /tmp/tmp_part_info || echo "Partitioning '/home --fstype ext4' is NOT done"
df -h /opt -t ext4 >> /tmp/tmp_part_info || echo "Partitioning '/opt --fstype ext4' is NOT done"
df -h /var/log -t ext4 >> /tmp/tmp_part_info || echo "Partitioning '/opt --fstype ext4' is NOT done"
df -h / -t ext4 >> /tmp/tmp_part_info || echo "Partitioning '/ --fstype ext4' is NOT done"
swapon -s >> /tmp/tmp_part_info || echo "No swap Created"

echo "######################	End of Partition Scheme			######################"

echo "######################	PACKAGES VALIDATION PART 		######################"

PACKAGE_LIST="core salt-master salt-minion python-pip ypbind ypserv ntp uwsgi nginx kexec-tools fractalio_django python-devel vsftpd sg3_utils perl-Config-General scsi-target-utils nfs-utils smartmontools samba-client samba samba-winbind samba-winbind-clients ipmitool OpenIPMI zfs krb5-workstation perl zlib python-setuptools gcc vsftpd smbldap-tools openldap-clients openldap-servers nss-pam-ldapd kmod-mv94xx"

for pkg in $PACKAGE_LIST; do
    if ! rpm -qa | grep $pkg ; then
        echo "$pkg : Not Installed"
    fi
done
echo "######################	END OF PACKAGE VALIDATION PART 		######################"

echo "######################	Default Username and Group 		######################"
grep integralstor /etc/passwd >>/tmp/tmp_users_info || echo "No user Called 'Integralstor'"
grep integralstor /etc/group >>/tmp/tmp_users_info || echo "No Group Called 'Integralstor'"
grep integralstor /etc/sudoers >>/tmp/tmp_users_info || echo "No Sudoer Called 'Integralstor'"
grep replicator /etc/passwd >>/tmp/tmp_users_info || echo "No user Called 'Replicator'"
grep replicator /etc/group >>/tmp/tmp_users_info || echo "No Group Called 'Replicator'"
grep replicator /etc/sudoers >>/tmp/tmp_users_info || echo "No Sudoer Called 'Replicator'"
echo "######################	End of Username and Group 		######################"
echo "######################	Active Interfaces			######################"
ip addr show dev lo >> /tmp/tmp_net || echo "'lo' interface does not exist"
ip addr show dev eth0 >> /tmp/tmp_net || echo "'eth0' interface does not exist"
ip addr show dev eth1 >> /tmp/tmp_net || echo "'eth0' interface does not exist"
ip addr show dev eth2 >> /tmp/tmp_net || echo "'eth1' interface does not exist"
ip addr show dev eth3 >> /tmp/tmp_net || echo "'eth2' interface does not exist"
ACTIVE_IP=`ifconfig | awk -vRS= -vFS="\n" '{ if ( $0 ~ /inet\ addr:/ ) { print }}' | sed 's/[ \t].*//;/^\(lo\|\)$/d'`
grep $ACTIVE_IP /etc/sysconfig/network-scripts/ifcfg-* >>/tmp/tmp_net || echo "No Active Interfaces"
GATEWAY_IP=`netstat -nr | awk '{ if ($4 ~/UG/) print; }' | awk -v CUR_IF=$IF '$NF==CUR_IF {print $2};'`
if [ ! -z "$GATEWAY_IP" ] ; then
    echo "No Gateway IP"
fi
echo "######################	End of Active Interfaces		######################"
echo "######################	Hostname				######################"
STRING=$(ifconfig | grep eth0 | head -1 | awk '{print $5}' | awk -F ':' '{print tolower($5 $6)}')
hnpart="integralstor-"$STRING
name="$hnpart.integralstor.lan"
grep $name /etc/sysconfig/network >>/tmp/tmp_host_name || echo "Error setting Hostname"
echo "######################	End of Hostname				######################"
echo "######################	Hosts					######################"
ip=$(ifconfig | awk -F':' '/inet addr/&&!/127.0.0.1/{split($2,_," ");print _[1]}')
STRING=$(ifconfig | grep eth0 | head -1 | awk '{print $5}' | awk -F ':' '{print tolower($5 $6)}')
hnpart="integralstor-"$STRING
name="$hnpart.integralstor.lan"
#grep $ip /etc/hosts >>/tmp/tmp_hosts || echo "No Host's IP is Set"
grep $name /etc/hosts >>/tmp/tmp_hosts || echo "No Host's NAME is Set"
grep $hnpart /etc/hosts >>/tmp/tmp_hosts || echo "No Host's HNPART is Set"
echo "######################	Hosts End				######################"
echo "######################	SSHD Status 				######################"
chkconfig --list sshd >> /tmp/tmp_ssh || echo "No SSH service"
grep integralstor /etc/ssh/sshd_config >> /tmp/tmp_allowd_ssh_user || echo "User 'Integralstor' is Not Allowed SSH user"
grep replicator /etc/ssh/sshd_config >> /tmp/tmp_allowd_ssh_user || echo "User 'Replicator' is Not Allowed SSH user"
grep "PermitRootLogin no" /etc/ssh/sshd_config >> /tmp/tmp_allowd_ssh_user || echo "User 'Root' is ALLOWED for SSH"
echo "######################	End of SSHD status			######################"
echo "######################	End of CentOS-Base repo status		######################"
grep enabled=0 /etc/yum.repos.d/CentOS-Base.repo >> /tmp/tmp_Base_repo || echo "'CentOS-Base.repo' Repositories Not Disabled"
echo "######################	End of CentOS-Base repo status		######################"
echo "######################	Directory and File Creation check	######################"

DIR_LIST="/opt/integralstor /opt/integralstor/pki /opt/integralstor/integralstor/tmp /run/samba /var/log/integralstor/integralstor /opt/integralstor/integralstor/config/status /opt/integralstor/integralstor /opt/integralstor/integralstor_utils /usr/lib/python2.6/site-packages/integralstor_utils /usr/lib/python2.6/site-packages/integralstor /etc/nginx/sites-enabled /etc/uwsgi/vassals /lib/modules/2.6.32-504.el6.x86_64/extra/mv94xx"

for path in $DIR_LIST; do
    if [[ ! -d "$path" ]]; then
	echo "'$path' Directory Does Not Exist"
    fi
done

FILE_LIST="/opt/integralstor/ramdisks.conf /opt/integralstor/platform /var/log/integralstor/logs/scripts/integral_view.log /etc/init/start-ttys.conf /etc/init/integralstor_menu.conf /etc/nginx/sites-enabled/integral_view_nginx.conf /etc/uwsgi/vassals/integral_view_uwsgi.ini /etc/init.d/ramdisk /etc/vsftpd/vsftpd.conf /etc/modprobe.d/zfs.conf /etc/sysconfig/shellinaboxd /etc/nsswitch.conf /etc/nginx/sites-enabled/integral_view_nginx.conf /etc/xinetd.d/rsync /etc/uwsgi/vassals/integral_view_uwsgi.ini /etc/init.d/uwsgi /etc/init.d/ramdisk /etc/modprobe.d/zfs.conf /etc/zfs/zed.d/zed.rc /etc/vsftpd/vsftpd.conf"

for path in $FILE_LIST; do
    if [[ ! -e "$path" ]]; then
        echo "'$path' File Does Not Exist"
    fi
done

echo "######################	End of Directory and File Creation Chk	######################"


echo "######################	File Perms				######################"

echo "######################	End of file Perms			######################"

echo "######################	Zip files				######################"
cat /usr/bin/iostat >> /tmp/tmp_systat || /usr/bin/sadf >> /tmp/tmp_systat || echo "No Systat Installed"
cat /usr/lib/python2.6/site-packages/setuptools-11.3.1-py2.6.egg >> /tmp/tmp_setuptool || echo "No Setuptools Installed"
grep uwsgi /usr/sbin/uwsgi >> /tmp/tmp_uwsgi || echo "No UWSGI Installed"
cat /usr/lib64/python2.6/site-packages/netifaces-0.10.4-py2.6-linux-x86_64.egg >> /tmp/tmp_netifaces || echo "No Netifaces Installed"
cat /usr/bin/crontab >> /tmp/tmp_crontab || echo "No Crontab Installed"
cat /usr/local/sbin/zfs-auto-snapshot >> /tmp/tmp_zfs_auto_snap || echo "No zfs-auto-snapshot Installed"
echo "######################	End of Zip files			######################"


echo "######################	/etc/nginx/nginx.conf			######################"
grep sites-enabled /etc/nginx/nginx.conf >> /tmp/tmp_sites_enabled || echo "No Sites_enabled in nginx.conf"
echo "######################	/etc/nginx/nginx.conf			######################"

echo "######################		/etc/nsswitch.conf       	######################"
grep nsswitch.conf /etc/nsswitch.conf >> /tmp/tmp_nsswitch || echo "No nsswitch.conf"
echo "######################		end of /etc/nsswitch		######################"

echo "######################	rc.local of /usr/bin/uwsgi		######################"
grep /var/log/integralstor/logs/scripts/integral_view.log /etc/rc.local >> /tmp/tmp_rc.local || echo "'rc.local' not written /usr/bin/uwsgi"
grep /sbin/zed /etc/rc.local >> /tmp/tmp_rc.local || echo "'rc.local' not written /sbin/zed"
grep "modprobe ipmi_devintf" /etc/rc.local >> /tmp/tmp_rc.local || echo "'rc.local' not written modprobe ipmi_devintf"
grep "/sbin/modprobe zfs" /etc/rc.local >> /tmp/tmp_rc.local || echo "'rc.local' not written '/sbin/modprobe zfs'"
echo "######################	End of rc.local of /usr/bin/uwsgi	######################"

echo "######################	Other Services Status			######################"
chkconfig --list nfs >> /tmp/tmp_ssh || echo "No NFS service"
chkconfig --list smb >> /tmp/tmp_ssh || echo "No SMB service"
chkconfig --list tgtd >> /tmp/tmp_ssh || echo "No TGTD service"
chkconfig --list winbind >> /tmp/tmp_ssh || echo "No WINBIND service"
chkconfig --list ntpd >> /tmp/tmp_ssh || echo "No NTPD service"
chkconfig --list ramdisk >> /tmp/tmp_ssh || echo "No RAMDISK service"
echo "######################	End of Other Services			######################"
echo "######################		********END********		######################"
