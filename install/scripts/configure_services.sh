#!/bin/bash

# Place services and other configuration files appropriately

base_dir="/opt/integralstor/integralstor"
install_dir="$base_dir/install"         # /opt/integralstor/integralstor/install
conf_dir="$install_dir/conf-files"      # /opt/integralstor/integralstor/install/conf-files
services_dir="$conf_dir/services"       # /opt/integralstor/integralstor/install/conf-files/services
db_dir="$conf_dir/db"                   # /opt/integralstor/integralstor/install/conf-files/db
others_dir="$conf_dir/others"           # /opt/integralstor/integralstor/install/conf-files/others


# shellinabox
mv /etc/sysconfig/shellinaboxd /etc/sysconfig/BAK.shellinaboxd
cp $services_dir/shellinaboxd /etc/sysconfig/shellinaboxd

# nsswitch
mv /etc/nsswitch.conf /etc/BAK.nsswitch.conf
cp $services_dir/nsswitch.conf /etc/nsswitch.conf

# nginx
mkdir -p /etc/nginx/sites-enabled
mv /etc/nginx/nginx.conf /etc/nginx/BAK.nginx.conf
cp $services_dir/nginx.conf /etc/nginx/nginx.conf
cp $services_dir/integral_view_nginx.conf /etc/nginx/sites-enabled/integral_view_nginx.conf
sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf

# xinetd
mv /etc/xinetd.d/rsync /etc/xinetd.d/BAK.rsync
cp $services_dir/rsync /etc/xinetd.d/rsync

# uwsgi
mkdir -p /etc/uwsgi/vassals
cp $services_dir/integral_view_uwsgi.ini /etc/uwsgi/vassals/
cp $services_dir/uwsginew.service /usr/lib/systemd/system/
cp $services_dir/uwsginew.service /etc/systemd/system/multi-user.target.wants/

# ramdisk
touch $services_dir/ramdisks.conf
cp $others_dir/ramdisks /etc/rc.d/init.d/ramdisks
cp $services_dir/ramdisk.service /etc/systemd/system/multi-user.target.wants/

# vsftpd
mv /etc/vsftpd/vsftpd.conf /etc/vsftpd/BAK.vsftpd.conf
cp $services_dir/vsftpd.conf /etc/vsftpd/

# Log rotate Integralstor
cp $services_dir/integralstor-log-rotate /etc/logrotate.d/integralstor-log-rotate

# ZFS & zed
cp $services_dir/zed.rc /etc/zfs/zed.d/zed.rc
cp $services_dir/zfs.modules /etc/sysconfig/modules/zfs.modules

# plymouth theme
# TODO:Required?
mv /usr/share/plymouth/themes/text/text.plymouth /usr/share/plymouth/themes/text/BAK.text.plymouth
cp $others_dir/text.plymouth /usr/share/plymouth/themes/text/text.plymouth

# Display pre login message(header)
mv /etc/issue /etc/BAK.issue
cp $others_dir/issue /etc/issue

# USB 
# Systemd unit file for USB automount/unmount 
cp $services_dir/usb-mount@.service /etc/systemd/system/usb-mount@.service
# Create udev rule to start/stop usb-mount@.service on hotplug/unplug
cat $services_dir/99-local.rules.usb-mount >> /etc/udev/rules.d/99-local.rules

# first-boot systemd service file
cp $services_dir/first-boot.service /etc/systemd/system/

# Remove execute permissions from service files
chmod -x /usr/lib/systemd/system/urbackup-server.service
chmod -x /usr/lib/systemd/system/tgtd.service
sed -i "s/^TasksMax.*/ /g" /usr/lib/systemd/system/urbackup-server.service

# Share /var/log over SMB and NFS
mv /etc/exports /etc/BAK.exports
cp $services_dir/exports /etc/
mv /etc/samba/smb.conf /etc/samba/BAK.smb.conf
cp $services_dir/smb.conf /etc/samba/


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

systemctl daemon-reload
udevadm control --reload-rules

