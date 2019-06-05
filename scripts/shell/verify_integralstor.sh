#!/bin/bash

echo "Checking whether necessary users are present.."
users="integralstor replicator console nagios"

for user in $users;
do
	if id "$user" > /dev/null 2>&1;then
		echo "$user - OK";
	
	else
		echo "$user does not exist"
		echo "Creating user $user.."

		if [ $user == "integralstor" ];then
			useradd integralstor -g 1000
			groupadd integralstor -g 1000
			echo "integralstor123" | passwd --stdin integralstor

		elif [ $user == "replicator" ];then
			useradd replicator -g 1000
			echo "replicator123" | passwd --stdin replicator

		elif [ $user == "console" ];then
			useradd console -g 1002
			groupadd console -g 1002
			echo "console123" | passwd --stdin console
 
		elif [ $user == "nagios" ];then
			useradd nagios -g 1003
			groupadd nagios -g 1003
			echo "nagios123" | passwd --stdin nagios
		fi	
	fi
	done
		
# Min and Max UID is set to 1500 to distinguish between system and integralstor users
echo "Checking whether Min and Max UID is set to 1500"
MIN_UID=$( grep -i "UID_MIN" /etc/login.defs | head -1 | awk '{print $2}' )
MIN_GID=$( grep -i "GID_MIN" /etc/login.defs | head -1 | awk '{print $2}' )

if [ $MIN_UID != 1500 ];then
	echo "Minimum UID is $MIN_UID, setting it to 1500.."
	sed -i "s/^UID_MIN.*/UID_MIN                  1500/g" /etc/login.defs
else
	echo "MIN UID - OK"
fi

if [ $MIN_GID != 1500 ];then
	echo "Minimum GID is $MIN_GID, setting it to 1500.."

else
	echo "MIN GID - OK"
fi

# Allow Network Manager to control network interfaces
echo "Setting Network Manager control over interfaces.."
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-em*

# Avoid tty for clean ZFS remote replication process
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers

# Check and move integralstor site-packages to /usr/lib/python2.7/site-packages/
LIB_PATH="/usr/lib/python2.7/site-packages/integralstor"

echo "Checking if integralstor site-packages are in place.."

if [ -e $LIB_PATH ];then
	echo "Checked - OK"
else
        echo "$LIB_PATH not in place, creating symlink.."
	ln -s /opt/integralstor/integralstor/site-packages/integralstor /usr/lib/python2.7/site-packages/integralstor
fi

# Add nfs-local user and group if not present
echo "Checking for nfs-local user and group"
nfs_usr=`python -c "from integralstor import config; name, err = config.get_local_nfs_user_name(); print name;"`
nfs_grp=`python -c "from integralstor import config; name, err = config.get_local_nfs_group_name(); print name;"`

if id "$nfs_usr" > /dev/null 2>&1;then
        echo "nfs user - OK"
else
        echo "nfs user not present, creating.."
        useradd "$nfs_usr" -g 1500 -u 1500
        echo "$nfs_usr""123" | passwd --stdin "$nfs_usr"
fi

if grep -q $nfs_grp /etc/group;then
        echo "nfs group - OK"
else
        echo "nfs group not present, creating.."
        groupadd "$nfs_grp" -g 1500
fi

# Check and create necessary directories

echo "Checking if necessary integralstor specific directories are present.."

dirs="/var/log/integralstor/logs /var/log/integralstor/logs/scripts /var/log/integralstor/logs/tasks /var/log/integralstor/logs/cron /var/log/integralstor/logs/exported /var/log/integralstor/archives /var/log/integralstor/archives/config /var/log/integralstor/archives/logs /var/log/integralstor/reports /var/log/integralstor/reports/urbackup /var/log/integralstor/reports/integralstor_status /var/log/integralstor/reports/remote-replication /opt/integralstor/integralstor/config /opt/integralstor/integralstor/config/db /opt/integralstor/integralstor/config/status /opt/integralstor/integralstor/config/pki /opt/integralstor/integralstor/config/conf_files /opt/integralstor/integralstor/config/run /opt/integralstor/integralstor/config/run/tasks /opt/integralstor/integralstor/config/run/tasks/foo"

for dir in $dirs
do
        if [ ! -d $dir ];then
                echo "$dir not present, creating.."
                mkdir -p $dir
        fi
done             

# Check re-enforce permissions.

echo "Re-enforcing permissions.."

chmod -R 777 /var/log/integralstor
chmod -R 755 /opt/integralstor/integralstor/scripts/python/*
chmod -R 755 /opt/integralstor/integralstor/scripts/shell/*
chmod -R 775 /opt/integralstor/integralstor/config/run
chown -R nagios:nagios /usr/local/nagios &> /dev/null

# Create empty log files if they're not present

echo "Checking if log files are created.."

files="/var/log/integralstor/logs/scripts/scripts.log /var/log/integralstor/logs/scripts/integral_view.log /var/log/integralstor/logs/scripts/ramdisks"

for file in $files
do
	if [ ! -f $file ];then
		touch $file
	fi
done

echo "Checking hardware vendor.."

# Check for platform file, set hardware_vendor to dell if using dell hardware, leave it empty if not.

if [ ! -e /opt/integralstor/integralstor/platform ]; then
	echo "platform file not present, generating.."
	hardware_vendor=$(cat /root/hardware_vendor | cut -d':' -f2)
	if [ -z "$hardware_vendor" ]; then
 		 echo
	else
		sed -i /hardware_vendor/d /opt/integralstor/integralstor/platform
		printf ' "hardware_vendor":"%s"}\n' "$hardware_vendor" >> /opt/integralstor/integralstor/platform
	fi
	ln -s /opt/integralstor/integralstor/platform /opt/integralstor > /dev/null 2>&1
else
	echo "Checked - Ok"
fi

echo "Checking anacron.."

if [ -e /etc/anacrontab ]; then
	if [ $(grep -i 'RANDOM_DELAY=' /etc/anacrontab) != 'RANDOM_DELAY=5' ]; then
		echo "Setting RANDOM_DELAY.."
		sed -i 's/RANDOM_DELAY=45/RANDOM_DELAY=5/' /etc/anacrontab
	fi
	if [ $(grep -i 'START_HOURS_RANGE=' /etc/anacrontab) != 'START_HOURS_RANGE=0-1' ]; then
		echo "Setting START_HOURS_RANGE.."
		sed -i 's/START_HOURS_RANGE=3-22/START_HOURS_RANGE=0-1/' /etc/anacrontab
	fi
	echo "checked - OK"
fi 

echo "Checking db files.."

db_files="django.db inotify.db integralstor_db.schema integralstor.db"

for db_file in $db_files;
do
	if [ ! -e /opt/integralstor/integralstor/config/db/$db_file ] && [ $db_file == 'integralstor.db' ];then
		echo "integralstor.db missing, creating it now.."
		sqlite3 /opt/integralstor/integralstor/config/db/integralstor.db < /opt/integralstor/integralstor/install/conf-files/db/integralstor_db.schema
	fi

	if [ ! -e /opt/integralstor/integralstor/config/db/$db_file ];then
		echo "$db_file is missing, copying it now.."
		cp /opt/integralstor/integralstor/install/conf-files/db/$db_file /opt/integralstor/integralstor/config/db/
	else
		echo "$db_file - Exists"
	fi	
done

# Check and update crontab if it is empty.

echo "Checking cron entry.. "

if [ $(crontab -l | wc -l) -lt 30  ]; then
        echo "Updating cron entries.."
        cat /opt/integralstor/integralstor/install/scripts/cron_entries.list | crontab -
else
        echo "Checked - OK"
 fi


echo "checking if printing kernel messages(dmesg) to console is disabled..."

if [ -z $(grep -i "dmesg -n 1" /etc/rc.d/rc.local | head -1 | awk '{print $1}') ]; then
	echo "dmesg -n 1" >> /etc/rc.d/rc.local

else
	echo "Checked - OK"
fi

# Verify configure_services.sh

base_dir="/opt/integralstor/integralstor"
install_dir="$base_dir/install"         
conf_dir="$install_dir/conf-files"     
services_dir="$conf_dir/services"     
others_dir="$conf_dir/others"       

echo "Verifying service configurations.."

# zed 

if [ ! -f /usr/libexec/zfs/zed.d/scrub_finish-integralstor.sh ]; then
	echo "Missing scrub_finish-integralstor.sh, copying now..."
	cp $install_dir/scripts/scrub_finish-integralstor.sh /usr/libexec/zfs/zed.d
	chmod 755 /usr/libexec/zfs/zed.d/scrub_finish-integralstor.sh
	ln -s /usr/libexec/zfs/zed.d/scrub_finish-integralstor.sh /etc/zfs/zed.d/scrub_finish-integralstor.sh > /dev/null 2>&1
else
	echo "scrub_finish-integralstor.sh - Ok"
fi

if [ ! -f /usr/libexec/zfs/zed.d/resilver_finish-integralstor.sh ]; then
	echo "Missing resilver_finish-integralstor.sh, copying now.."
	cp $install_dir/scripts/resilver_finish-integralstor.sh /usr/libexec/zfs/zed.d
	chmod 755 /usr/libexec/zfs/zed.d/resilver_finish-integralstor.sh
	ln -s /usr/libexec/zfs/zed.d/resilver_finish-integralstor.sh /etc/zfs/zed.d/resilver_finish-integralstor.sh > /dev/null 2>&1
else
	echo "resilver_finish-integralstor.sh - Ok"
fi

# shellinaboxd  

if [ ! -f /etc/sysconfig/BAK.shellinaboxd ]; then
	echo "shellinaboxd not copied, copying now.."
	mv /etc/sysconfig/shellinaboxd /etc/sysconfig/BAK.shellinaboxd
	cp $services_dir/shellinaboxd /etc/sysconfig/shellinaboxd
else
	echo "Shellinaboxd - Ok"
fi

# nsswitch

if [ ! -f  /etc/BAK.nsswitch.conf ]; then
	echo "nsswitch not copied, copying now.."
	mv /etc/nsswitch.conf /etc/BAK.nsswitch.conf
	cp $services_dir/nsswitch.conf /etc/nsswitch.conf
else
	echo "nsswitch - Ok"
fi

# nginx

if [ ! -d /etc/nginx/sites-enabled ]; then
	echo "/etc/nginx/sites-enabled does not exist, creating.."
	mkdir -p /etc/nginx/sites-enabled
fi

if [ -d /etc/nginx ]; then
	if [ ! -f /etc/nginx/BAK.nginx.conf ]; then
		echo "nginx.conf not copied, copying now.."
		mv /etc/nginx/nginx.conf /etc/nginx/BAK.nginx.conf
		cp $services_dir/nginx.conf /etc/nginx/nginx.conf
		sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf
	fi

	if [ ! -f /etc/nginx/sites-enabled/integral_view_nginx.conf ]; then
		echo "integral_view_nginx.conf not copied, copying now.."
		cp $services_dir/integral_view_nginx.conf /etc/nginx/sites-enabled/integral_view_nginx.conf
	fi
else
	echo "Nginx - Ok"

fi

# xinetd

if [ ! -f /etc/xinetd.d/BAK.rsync ]; then
	echo "xinetd/rsync not copyied, copying now.."
	mv /etc/xinetd.d/rsync /etc/xinetd.d/BAK.rsync
	cp $services_dir/rsync /etc/xinetd.d/rsync
fi

# uwsgi

if [ ! -d /etc/uwsgi/vassals ]; then
	echo "/etc/uwsgi/vassals does not exist, creating.."
	mkdir -p /etc/uwsgi/vassals
fi

if [ ! -e /etc/uwsgi/vassals/integral_view_uwsgi.ini ]; then
		echo "/etc/uwsgi/vassals/integral_view_uwsgi.ini not present, copying now.."
		cp $services_dir/integral_view_uwsgi.ini /etc/uwsgi/vassals/
fi

if [ ! -e /usr/lib/systemd/system/uwsginew.service ]; then
	echo "/usr/lib/systemd/system/uwsginew.service not present, copying now.."
	cp $services_dir/uwsginew.service /usr/lib/systemd/system/
fi

if [ ! -e /etc/systemd/system/multi-user.target.wants/uwsginew.service ]; then
	echo "/etc/systemd/system/multi-user.target.wants/uwsginew.service not present, copying now.."  
	cp $services_dir/uwsginew.service /etc/systemd/system/multi-user.target.wants/
fi

# ramdisk

if [ ! -e /etc/rc.d/init.d/ramdisk ]; then
	echo "/etc/rc.d/init.d/ramdisk not present, copying now.."
	cp $others_dir/ramdisk /etc/rc.d/init.d/ramdisk
fi

if [ ! -e /etc/systemd/system/multi-user.target.wants/ramdisk.service ]; then
	echo "/etc/systemd/system/multi-user.target.wants/ramdisk.service not present, copying now.."
	cp $services_dir/ramdisk.service /etc/systemd/system/multi-user.target.wants/
else
	echo "ramdisk.service - Ok"
fi

# vsftpd

if [ ! -e /etc/vsftpd/BAK.vsftpd.conf ]; then
	echo "vsftpd.conf not copied, copying now.."
	mv /etc/vsftpd/vsftpd.conf /etc/vsftpd/BAK.vsftpd.conf
	cp $services_dir/vsftpd.conf /etc/vsftpd/
else
	echo "vsftp - Ok"
fi

# logrotate

if [ ! -e /etc/logrotate.d/integralstor-log-rotate ]; then
	echo "integralstor-log-rotate not copied, copying now.."
	cp $services_dir/integralstor-log-rotate /etc/logrotate.d/integralstor-log-rotate
fi

if [ ! -e /etc/zfs/zed.d/zed.rc ]; then
	cp $services_dir/zed.rc /etc/zfs/zed.d/zed.rc
	cp $services_dir/zfs.modules /etc/sysconfig/modules/zfs.modules
else
	echo "Zed - Ok"
fi

# plymouth

if [ ! -e /usr/share/plymouth/themes/text/BAK.text.plymouth ]; then
	echo "/usr/share/plymouth/themes/text/text.plymouth not copied, copying now"
	mv /usr/share/plymouth/themes/text/text.plymouth /usr/share/plymouth/themes/text/BAK.text.plymouth
	cp $others_dir/text.plymouth /usr/share/plymouth/themes/text/text.plymouth
fi

# issue

if [ ! -e /etc/BAK.issue ]; then
	mv /etc/issue /etc/BAK.issue
	cp $others_dir/issue /etc/issue
fi

# Check and setup usb-mount, usb-mount automatically mounts a usb drive when plugged in. It will be mounted under /media/devXX

if [ ! -e /etc/systemd/system/usb-mount@.service ]; then
	echo "usb-mount service not copied, copying now.."
	cp $services_dir/usb-mount@.service /etc/systemd/system/usb-mount@.service
else
	echo "usb-mount [1/2] - Ok"
fi

f=$(grep "/bin/systemctl start usb-mount@%k.service" /etc/udev/rules.d/99-local.rules | head -1 | awk '{print $2}' | cut -d ',' -f1
SUBSYSTEMS=="usb")

if [ -z $f ]; then
	echo "USB mount udev entry not present, adding now.."
	cat $services_dir/99-local.rules.usb-mount >> /etc/udev/rules.d/99-local.rules
else
	echo "usb-mount [2/2] - Ok"
fi

# first-boot systemd service file

if [ ! -e /etc/systemd/system/ ]; then
	cp $services_dir/first-boot.service /etc/systemd/system/
fi

# Export/Share /var/log for support purposes.

varlog_smb_share=$(grep "system_logs" /etc/samba/smb.conf | cut -d '[' -f2 | cut -d ']' -f1)
varlog_nfs_export=$(grep "/var/log" /etc/exports | awk '{print $1}')

if [ -z $varlog_nfs_export ]; then
	echo "/var/log not exported, exporting.."
	mv /etc/exports /etc/BAK.exports
	echo "/var/log *(ro,root_squash)" >> /etc/exports
else
	echo "/var/log exported"
fi

if [ -z $varlog_smb_share ]; then
	echo "smb share for /var/log does not exist, creating.."
	mv /etc/samba/smb.conf /etc/samba/BAK.smb.conf
	echo -e "[system_logs]\n vfs objects = shadow_copy2\n inherit permissions = yes\n inherit acls = yes\n comment = Integralstor system logs share\n path = /var/log\n kernel share modes = no\n" >> /etc/samba/smb.conf
else
	echo "/var/log shared"
fi

# Start and enable services
systemctl start rpcbind &> /dev/null; systemctl enable rpcbind &> /dev/null
systemctl start nfs-server &> /dev/null; systemctl enable nfs-server &> /dev/null
systemctl start winbind &> /dev/null; systemctl enable winbind &> /dev/null
systemctl start smb &> /dev/null; systemctl enable smb &> /dev/null
systemctl start tgtd &> /dev/null; systemctl enable tgtd &> /dev/null
systemctl start ntpd &> /dev/null; systemctl enable ntpd &> /dev/null
systemctl start crond &> /dev/null; systemctl enable crond &> /dev/null
systemctl start ramdisk &> /dev/null; systemctl enable ramdisk &> /dev/null
systemctl start vsftpd &> /dev/null; systemctl enable vsftpd &> /dev/null
systemctl start shellinaboxd &> /dev/null; systemctl enable shellinaboxd &> /dev/null
systemctl start uwsginew &> /dev/null; systemctl enable uwsginew &> /dev/null
systemctl start nginx &> /dev/null; systemctl enable nginx &> /dev/null
systemctl stop first-boot &> /dev/null; systemctl disable first-boot &> /dev/null
systemctl restart zed &> /dev/null
systemctl preset zfs.target zfs-import-cache zfs-import-scan zfs-mount zfs-share zfs-zed &> /dev/null

systemctl daemon-reload
udevadm control --reload-rules
