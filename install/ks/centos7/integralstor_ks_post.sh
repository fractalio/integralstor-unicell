#!/bin/bash

### Adding neccesary users and groups ###
groupadd integralstor -g 1000
useradd integralstor -g 1000
useradd replicator -g 1000
groupadd console -g 1002
useradd console -g 1002
useradd nagios

echo "integralstor123" | passwd --stdin integralstor
echo "replicator123" | passwd --stdin replicator
echo "console123" | passwd --stdin console
echo "nagios123" | passwd --stdin nagios
echo "integralstor    ALL=(ALL)    ALL" >> /etc/sudoers
echo "replicator    ALL=(ALL)    NOPASSWD: /usr/sbin/zfs,/usr/bin/rsync,/bin/rsync" >> /etc/sudoers
echo "console    ALL=(ALL)    NOPASSWD: ALL" >> /etc/sudoers

### Changing MIN_UID and MIN_GID to start from 1500 for local users ###
sed -i "s/^UID_MIN.*/UID_MIN                  1500/g" /etc/login.defs
sed -i "s/^GID_MIN.*/GID_MIN                  1500/g" /etc/login.defs

### Network interface configuration  ###
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-em*
sed -i 's/ONBOOT=no/ONBOOT=yes/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/ONBOOT=no/ONBOOT=yes/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/ONBOOT=no/ONBOOT=yes/' /etc/sysconfig/network-scripts/ifcfg-em*
sed -i 's/NM_CONTROLLED=yes/NM_CONTROLLED=no/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/NM_CONTROLLED=yes/NM_CONTROLLED=no/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/NM_CONTROLLED=yes/NM_CONTROLLED=no/' /etc/sysconfig/network-scripts/ifcfg-em*
sed -i 's/USERCTL=yes/ONBOOT=no/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/USERCTL=yes/ONBOOT=no/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/USERCTL=yes/ONBOOT=no/' /etc/sysconfig/network-scripts/ifcfg-em*
sed -i 's/PEERDNS=no/PEERDNS=yes/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/PEERDNS=no/PEERDNS=yes/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/PEERDNS=no/PEERDNS=yes/' /etc/sysconfig/network-scripts/ifcfg-em*
sed -i 's/IPV6INIT=yes/IPV6INIT=no/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/IPV6INIT=yes/IPV6INIT=no/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/IPV6INIT=yes/IPV6INIT=no/' /etc/sysconfig/network-scripts/ifcfg-em*

### Do not want network manager to add DNS servers received from DHCP to /etc/resolv.conf ###
sed -i '/\[main\]/a dns=none' /etc/NetworkManager/NetworkManager.conf
echo "NETWORKING=yes" >> /etc/sysconfig/network
echo "127.0.0.1   localhost   localhost.localdomain   localhost4    localhost4.localdomain4" > /etc/hosts

### Disabling the OPenGPGCheck and reloading the abrtd service ###
if [ -e "/etc/abrt/abrt-action-save-package-data.conf" ] ; then
  sed -i 's/OpenGPGCheck = yes/OpenGPGCheck = no/' /etc/abrt/abrt-action-save-package-data.conf 
else
  echo "No such file found : /etc/abrt/abrt-action-save-package-data.conf"
fi

### SSHD configuration ###

/usr/sbin/sshd stop
sed '' /etc/ssh/sshd_config > /etc/ssh/original_sshd_config
sed '/#PermitRootLogin/a PermitRootLogin no' /etc/ssh/sshd_config > /etc/ssh/temp_file
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers    #serach for requiretty and comment. This is to avoid tty for replication in zfs send/receive
rm -f /etc/ssh/sshd_config
mv /etc/ssh/temp_file /etc/ssh/sshd_config
/usr/sbin/sshd start

### Editing the /etc/yum.repos.d/CentOS-Base.repo ###
# ..to disable base, updates and extras repositories. ###

cp -rf /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/Original-CentOS-Base-repo
sed -i '/\[base\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
sed -i '/\[updates\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
sed -i '/\[extras\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
sed -i '/\[centosplus\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
sed -i '/\[contrib\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo


### Directory creation ###
/usr/bin/mkdir -p /opt/integralstor
/usr/bin/mkdir -p /opt/integralstor/pki
/usr/bin/mkdir -p /run/samba
/usr/bin/mkdir -p /var/log/integralstor/logs/scripts
/usr/bin/mkdir -p /opt/integralstor/integralstor/tmp
mkdir -p /opt/integralstor/integralstor/config/status
mkdir -p /etc/logrotate.d_old
touch /var/log/integralstor/logs/scripts/integral_view.log

### Install integralstor_utils ###
cd /opt/integralstor
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/integralstor_utils.tar.gz
/bin/tar xzf integralstor_utils.tar.gz
ln -s /opt/integralstor/integralstor_utils/site-packages/integralstor_utils /usr/lib/python2.7/site-packages/integralstor_utils
rm integralstor_utils.tar.gz

### Install integralstor ###
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/integralstor.tar.gz
/bin/tar xzf integralstor.tar.gz
ln -s /opt/integralstor/integralstor/site-packages/integralstor /usr/lib/python2.7/site-packages/integralstor
rm integralstor.tar.gz

### post code copy operationes ###
mv /etc/sysconfig/shellinaboxd /etc/sysconfig/shellinaboxd.bak
ln -s /opt/integralstor/integralstor/config/shellinabox/shellinaboxd /etc/sysconfig
yes | cp -rf /root/platform /opt/integralstor/integralstor
ln -s /opt/integralstor/integralstor/platform /opt/integralstor

chmod 755 /opt/integralstor/integralstor/scripts/python/*
chmod 755 /opt/integralstor/integralstor/scripts/shell/*
mkdir /opt/integralstor/integralstor/config/logs/cron_logs
mkdir /opt/integralstor/integralstor/config/logs/task_logs
chmod 777 /opt/integralstor/integralstor/config/logs/cron_logs
chmod 777 /opt/integralstor/integralstor/config/logs/task_logs
chown nagios.nagios /usr/local/nagios
chown -R nagios.nagios /usr/local/nagios/libexec
sed -i 's/RANDOM_DELAY=45/RANDOM_DELAY=5/' /etc/anacrontab
sed -i 's/START_HOURS_RANGE=3-22/START_HOURS_RANGE=0-1/' /etc/anacrontab

rm -rf /etc/nsswitch.conf
cp /opt/integralstor/integralstor/install/conf_files/nsswitch.conf /etc

# Copy NFS exports file containing default entries
mv /etc/exports /etc/BAK.exports
cp /opt/integralstor/integralstor/install/conf_files/exports /etc/

# Copy smb.conf containing default entries
mv /etc/samba/smb.conf /etc/samba/BAK.smb.conf
cp /opt/integralstor/integralstor/install/conf_files/smb.conf /etc/samba/

### Configure nginx ###
mkdir /etc/nginx/sites-enabled
cd /etc/nginx
mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
ln -s /opt/integralstor/integralstor/install/conf_files/nginx.conf /etc/nginx/
ln -s /opt/integralstor/integralstor/integral_view/integral_view_nginx.conf /etc/nginx/sites-enabled/
sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf

### Cinfigure xinetd ###
mv rsync rsync.bak
ln -s /opt/integralstor/integralstor/install/conf_files/rsync /etc/xinetd.d/

### Configure uwsgi ###
mkdir -p /etc/uwsgi/vassals
ln -s /opt/integralstor/integralstor/integral_view/integral_view_uwsgi.ini /etc/uwsgi/vassals/
cp /opt/integralstor/integralstor/install/conf_files/uwsginew.service /usr/lib/systemd/system
ln -s /usr/lib/systemd/system/uwsginew.service /etc/systemd/system/multi-user.target.wants/

### Configure ramdisks ###
#Change the ramdisks conf file name and location, move it into /opt/integralstor so it can be common to integralstor and gridcell
touch /opt/integralstor/ramdisks.conf
touch /var/log/integralstor/integralstor/ramdisks
ln -fs /opt/integralstor/integralstor_utils/install/scripts/ramdisk /etc/rc.d/init.d/
ln -s /opt/integralstor/integralstor/install/conf_files/ramdisk.service /etc/systemd/system/multi-user.target.wants/

#Download and install the non-rpm based software..
cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/sysstat-11.0.5.tar.xz
/bin/tar xJf sysstat-11.0.5.tar.xz
cd sysstat-11.0.5
./configure --prefix=/usr
make
make install
rm -rf sysstat-11.0.5*
cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/setuptools-29.0.1.tar.gz
/bin/tar xzf setuptools-29.0.1.tar.gz
cd setuptools-29.0.1
python setup.py install
rm -rf setuptools-29.0.1*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/uwsgi-2.0.9.tar.gz
/bin/tar xzf uwsgi-2.0.9.tar.gz
cd uwsgi-2.0.9
python setup.py install
rm -rf uwsgi-2.0.9*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/netifaces-0.10.5.tar.gz
/bin/tar xzf netifaces-0.10.5.tar.gz
cd netifaces-0.10.5
python setup.py install
rm -rf netifaces-0.10.5*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/six-1.10.0.tar.gz
/bin/tar xzf six-1.10.0.tar.gz
cd six-1.10.0
python setup.py install
rm -rf six-1.10.0*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/python-dateutil-2.6.0.tar.gz
/bin/tar xzf python-dateutil-2.6.0.tar.gz
cd python-dateutil-2.6.0
python setup.py install
rm -rf python-dateutil-2.6.0*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/python-crontab-2.1.1.tar.gz
/bin/tar xzf python-crontab-2.1.1.tar.gz
cd python-crontab-2.1.1
python setup.py install
cd /tmp
rm -rf python-crontab-2.1.1*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/mbuffer-20161115.tgz
/bin/tar xzf mbuffer-20161115.tgz
cd mbuffer-20161115
./configure
make && make install
cd /tmp
rm -rf mbuffer-20161115*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/zfs-auto-snapshot.tar.gz
/bin/tar xzf zfs-auto-snapshot.tar.gz
cd zfs-auto-snapshot
make install
cd /tmp
rm -rf zfs-auto-snapshot*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/Django-1.8.16.tar.gz
/bin/tar xzf Django-1.8.16.tar.gz
cd Django-1.8.16
python setup.py install
cd /tmp
rm -rf Django-1.8.16*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/cron_descriptor-1.2.6.tar.gz
/bin/tar xzf cron_descriptor-1.2.6.tar.gz
cd cron_descriptor-1.2.6
python setup.py install
cd /tmp
rm -rf cron_descriptor-1.2.6*

cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/nagios-plugins-2.1.4.tar.gz
/bin/tar -xvf nagios-plugins-2.1.4.tar.gz
cd nagios-plugins-2.1.4
./configure
make
make install
cd /tmp
rm -rf nagios-plugins-2.1.4*
cd /tmp
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/tar_installs/3.0.1.tar.gz
/bin/tar -xvf 3.0.1.tar.gz
cd nrpe-3.0.1/
./configure
make all
make install-groups-users
make install
make install-plugin
make install-daemon
make install-config
make install-init
cd /tmp
rm -rf nrpe*
rm -rf 3.0.1*

### Configure crontab ###
(crontab -l 2>/dev/null; echo 'MAILTO=""') | crontab -
(crontab -l 2>/dev/null; echo "SHELL=/bin/sh") | crontab -
(crontab -l 2>/dev/null; echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/dell/srvadmin/bin") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_utils/scripts/python/generate_status.py > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/lib64/sa/sa1 1 1 -S DISK > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_utils/scripts/python/poll_for_alerts.py > /tmp/out_alerts >> /tmp/err_alerts") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor/scripts/python/poll_for_alerts.py > /tmp/out_integralstor_alerts >> /tmp/err_integralstor_alerts") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /usr/bin/python /opt/integralstor/integralstor_utils/scripts/python/task_processor.py > /tmp/out_task_processor >> /tmp/err_task_processor") | crontab -
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/bin/python -c 'from integralstor_utils import logs; logs.auto_rotate_logs()' > /tmp/auto_rotate_logs_alerts >> /tmp/auto_rotate_errors") | crontab -
(crontab -l 2>/dev/null; echo "@reboot /usr/sbin/modprobe ipmi_devintf > /tmp/logs-ipmi_devinfo_modprobe >> /tmp/errors-ipmi_devinfo_modprobe") | crontab -
(crontab -l 2>/dev/null; echo "@reboot /usr/sbin/modprobe zfs > /tmp/logs-zfs_modprobe >> /tmp/errors-zfs_modprobe") | crontab -

### configuring Vsftpd ###
rm -f /etc/vsftpd/vsftpd.conf
ln -fs /opt/integralstor/integralstor/install/conf_files/vsftpd.conf /etc/vsftpd

#Log rotation 
cp -f /etc/logrotate.d/* /etc/logrotate.d_old/
cp -f /opt/integralstor/integralstor/install/log_rotate_files/* /etc/logrotate.d/

### configuring zed for zfs ###
ln -s /opt/integralstor/integralstor/install/conf_files/zed.rc /etc/zfs/zed.d
ln -s /opt/integralstor/integralstor/install/conf_files/zed.conf /etc/zfs/zed.d
ln -s /opt/integralstor/integralstor/install/conf_files/zfs.modules /etc/sysconfig/modules

### Configure rc.local ###
modprobe ipmi_devintf
modprobe 8021q

if grep "dell" /opt/integralstor/platform > /dev/null
then
  (crontab -l 2>/dev/null; echo "@reboot srvadmin-services.sh restart > /tmp/srvadmin_logs >> /tmp/srvadmin_errors") | crontab -
  echo "copying integralstor repository..."
  cd /etc/yum.repos.d
  /usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/integralstor.repo
  echo "copying integralstor repository...Done"
  echo "installing dell specific dependencies..."
  yum install srvadmin-all dell-system-update -y
  echo "installing dell specific dependencies...Done"
  echo "disabling integralstor repository..."
  sed -i '/\[updates\]/a enabled=0' /etc/yum.repos.d/integralstor.repo 
  echo "disabling integralstor repository...Done"
else
  echo "Non dell hardware. Exiting..."
fi
### Grub and other file modification to show title/name Integralstor instead Centos 7.2 ###
cd /etc
mv issue issue.bak
mv /usr/share/plymouth/themes/text/text.plymouth /usr/share/plymouth/themes/text/text.plymouth.bak
cp -f /opt/integralstor/integralstor/install/conf_files/text.plymouth /usr/share/plymouth/themes/text/

# Display pre login message
cp -f /opt/integralstor/integralstor/install/conf_files/issue /etc/
dracut -f

# Run login_menu.sh at user login
ln -s /opt/integralstor/integralstor/scripts/shell/login_menu.sh /etc/profile.d/spring_up.sh

### Configuring nagios ###
echo "nrpe            5666/tcp                 NRPE" >>/etc/services
iptables -A INPUT -p tcp -m tcp --dport 5666 -j ACCEPT
firewall-cmd --zone=public --add-port=5666/tcp --permanent

### creating integralstor config dg ###
cd /opt/integralstor/integralstor/config/db/
rm -f integral_view_config.db
sqlite3 integral_view_config.db < schemas

### Create systemd unit file to automount/unmount USB ###
cp -f /opt/integralstor/integralstor/install/conf_files/usb-mount@.service /etc/systemd/system/

### Create udev rule to start/stop usb-mount@.service on hotplug/unplug ###
cp -f /opt/integralstor/integralstor/install/conf_files/99-local.rules /etc/udev/rules.d/

### removing execute permission on these service files ###
chmod -x /usr/lib/systemd/system/urbackup-server.service
chmod -x /usr/lib/systemd/system/tgtd.service
sed -i "s/^TasksMax.*/ /g" /usr/lib/systemd/system/urbackup-server.service

### configuring AFP ###
mkdir /tmp/netatalk
cd /tmp/netatalk
echo "Installing AFT Dependencies..."
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/netatalk.tar.gz
/bin/tar xzf netatalk.tar.gz
cat >> /etc/yum.repos.d/integralstor.repo << EOF
[integralstor]
enabled=1
name= integralstor - base
baseurl=file:///tmp/netatalk/netatalk
gpgcheck=0
EOF
yum install avahi dbus nss-mdns gnome-boxes netatalk -y
echo "Installing AFT Dependencies...Done"
cat >> /etc/yum.repos.d/integralstor.repo << EOF
[integralstor]
enabled=0
name= integralstor - base
baseurl=file:///tmp/netatalk/netatalk
gpgcheck=0
EOF

ln -s /opt/integralstor/integralstor/install/conf_files/afpd.service /etc/avahi/services/
ln -s /opt/integralstor/integralstor/install/conf_files/afpd.conf /etc/netatalk/
echo "hosts: files mdns4_minimal dns mdns mdns4" >> /etc/nsswitch.conf

### Turn on other services ###
systemctl start rpcbind &> /dev/null && systemctl enable rpcbind &> /dev/null
systemctl start nfs-server &> /dev/null && systemctl enable nfs-server &> /dev/null
systemctl start winbind &> /dev/null && systemctl enable winbind &> /dev/null
systemctl start smb &> /dev/null && systemctl enable smb &> /dev/null
systemctl start tgtd &> /dev/null && systemctl enable tgtd &> /dev/null
systemctl start ntpd &> /dev/null && systemctl enable ntpd &> /dev/null
systemctl start crond &> /dev/null && systemctl enable crond &> /dev/null
systemctl start ramdisk &> /dev/null && systemctl enable ramdisk &> /dev/null
systemctl start vsftpd &> /dev/null && systemctl enable vsftpd &> /dev/null
systemctl start shellinaboxd &> /dev/null && systemctl enable shellinaboxd &> /dev/null
systemctl start uwsginew &> /dev/null && systemctl enable uwsginew &> /dev/null
systemctl start nginx &> /dev/null && systemctl enable nginx &> /dev/null
systemctl start nrpe &> /dev/null && systemctl enable nrpe &> /dev/null
systemctl start avahi-daemon &> /dev/null && systemctl enable avahi-daemon &> /dev/null
systemctl start netatalk &> /dev/null && systemctl enable netatalk &> /dev/null

systemctl daemon-reload
udevadm control --reload-rules

