#!/bin/bash

echo ">>> Inside post script <<<"

### disable selinux and firewall ###
echo "Disabling selinux..."
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
echo "Disabling selinux...Done"
echo "Disabling all repositories..."
yum-config-manager --disable "*" 

systemctl stop firewalld
systemctl disable firewalld
systemctl stop ip6tables
systemctl disable ip6tables

### installing non-rpm files ###
echo "Switching to working directory..."
echo ""
cd /opt/integralstor
echo "Started installing NON-RPM installs..."
echo ""
tar xzf integralstor_tar_installs.tar.gz

if [[ -d "integralstor_tar_installs" ]]; then
    cd /opt/integralstor/integralstor_tar_installs

    echo "Installing sysstat..."
    cd sysstat-11.0.5
    ./configure --prefix=/usr
    make
    make install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'sysstat' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing sysstat...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf sysstat-11.0.5

    echo "Installing setuptools..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf setuptools-11.3.1.tar.gz
    cd setuptools-11.3.1
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'setuptools' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing setuptools...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf setuptools-11.3.1.tar.gz

    echo "Installing uwsgi..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf uwsgi-2.0.9.tar.gz
    cd uwsgi-2.0.9
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'uwsgi' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing uwsgi...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf uwsgi-2.0.9.tar.gz

    echo "Installing netifaces..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf netifaces-0.10.4.tar.gz
    cd netifaces-0.10.4
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'netifaces' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing netifaces...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf netifaces-0.10.4.tar.gz

    echo "Installing six..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf six-1.10.0.tar.gz
    cd six-1.10.0
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'six' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing six...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf six-1.10.0.tar.gz
    
    echo "Installing python-dateutil..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf python-dateutil-2.4.2.tar.gz
    cd python-dateutil-2.4.2
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'python-dateutil' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing python-dateutil...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf python-dateutil-2.4.2.tar.gz

    echo "Installing python-crontab..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf python-crontab-1.9.3.tar.gz
    cd python-crontab-1.9.3
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'python-crontab' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing python-crontab...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf python-crontab-1.9.3.tar.gz

    echo "Installing mbuffer..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf mbuffer-20161115.tgz
    cd mbuffer-20161115
    ./configure
    make && make install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'mbuffer' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing mbuffer...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf mbuffer-20161115.tgz

    echo "Installing zfs-auto-snapdhot..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf zfs-auto-snapshot.tar.gz
    cd zfs-auto-snapshot
    make install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'zfs-auto-snapdhot' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing zfs-auto-snapshot...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf zfs-auto-snapshot.tar.gz

    echo "Installing Django..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf Django-1.8.16.tar.gz
    cd Django-1.8.16
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'Djhango' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing Django...Done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf Django-1.8.16.tar.gz

    echo "Installing cron_descriptor..."
    cd /opt/integralstor/integralstor_tar_installs
    tar xzf cron_descriptor-1.2.6.tar.gz
    cd cron_descriptor-1.2.6
    python setup.py install
    if [ $? -ne 0 ]; then
	echo ""
        echo "CRITICAL:'cron_descripter' installation Failed!"
        exit 1
    else
	echo ""
        echo "Installing cron_descriptor...done."
	echo "********************************"
    fi
    sleep 1
    cd /opt/integralstor/integralstor_tar_installs
    rm -rf cron_descriptor-1.2.6.tar.gz

else
    echo "'integralstor_tar_installs' Directory Does Not Exist so exiting..."
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "CRITICAL: NON-RPM installation Failed!"
    exit 1
else
    echo "Successfully installed NON-RPM installs."
    echo ""
fi
   
sleep 2

echo "***	Started post install operations		***"
echo ""

### Adding neccesary users and groups ###
groupadd integralstor -g 1000
useradd integralstor -g 1000
groupadd replicator -g 1001
useradd replicator -g 1001
groupadd console -g 1002
useradd console -g 1002

echo "integralstor123" | passwd --stdin integralstor
echo "replicator123" | passwd --stdin replicator
echo "console123" | passwd --stdin console
echo "nagios123" | passwd --stdin nagios
echo "integralstor    ALL=(ALL)    ALL" >> /etc/sudoers
echo "replicator    ALL=(ALL)    NOPASSWD: /usr/sbin/zfs" >> /etc/sudoers
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

#Do not want network manager to add DNS servers received from DHCP to /etc/resolv.conf
sed -i '/\[main\]/a dns=none' /etc/NetworkManager/NetworkManager.conf
echo "NETWORKING=yes" >> /etc/sysconfig/network
echo "127.0.0.1   localhost   localhost.localdomain   localhost4    localhost4.localdomain4" > /etc/hosts

### SSHD configuration ###
systemctl stop sshd
sed '' /etc/ssh/sshd_config > /etc/ssh/original_sshd_config
sed '/#PermitRootLogin/a PermitRootLogin no' /etc/ssh/sshd_config > /etc/ssh/temp_file
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers    #serach for requiretty and comment. This is to avoid tty for replication in zfs send/receive
rm -f /etc/ssh/sshd_config
mv /etc/ssh/temp_file /etc/ssh/sshd_config
systemctl start sshd
ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''
mkdir /home/replicator/.ssh
ssh-keygen -t rsa -f /home/replicator/.ssh/id_rsa -N ''

mkdir -p /etc/logrotate.d_old

### Linking integralstor code to respective paths
ln -s /opt/integralstor/integralstor_utils/site-packages/integralstor_utils /usr/lib/python2.7/site-packages/integralstor_utils
ln -s /opt/integralstor/integralstor/site-packages/integralstor /usr/lib/python2.7/site-packages/integralstor

### Updating platform file
ln -s /tmp/platform /opt/integralstor
ln -fs /opt/integralstor/platform /opt/integralstor/integralstor

### Shellinabox file updates
mv /etc/sysconfig/shellinaboxd /etc/sysconfig/shellinaboxd.bak
ln -s /opt/integralstor/integralstor/config/shellinabox/shellinaboxd /etc/sysconfig

### Chhanging scripts files for appropriate permission
chmod 755 /opt/integralstor/integralstor/scripts/python/*
chmod 755 /opt/integralstor/integralstor/scripts/shell/*
mkdir -p /opt/integralstor/integralstor/config/logs/cron_logs
mkdir -p /opt/integralstor/integralstor/config/logs/task_logs
chmod 777 /opt/integralstor/integralstor/config/logs/cron_logs
chmod 777 /opt/integralstor/integralstor/config/logs/task_logs

### changing anacron to start cron jobs between 12AM-1AM
sed -i 's/RANDOM_DELAY=45/RANDOM_DELAY=5/' /etc/anacrontab
sed -i 's/START_HOURS_RANGE=3-22/START_HOURS_RANGE=0-1/' /etc/anacrontab

rm -rf /etc/nsswitch.conf
cp /opt/integralstor/integralstor/install/conf_files/nsswitch.conf /etc

### Configure nginx ###
ln -s /opt/integralstor/integralstor/integral_view/integral_view_nginx.conf /etc/nginx/sites-enabled/
cp -rf /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
yes | cp -rf /opt/integralstor/integralstor_tar_installs/nginx.conf /etc/nginx
sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf

### Cinfigure xinetd ###
cd /etc/xinetd.d/
mv rsync rsync.bak
ln -s /opt/integralstor/integralstor/install/conf_files/rsync /etc/xinetd.d/
#sed -i 's/disable = yes/disable = no/' /etc/xinetd.d/rsync

### Configure uwsgi ###
ln -s /opt/integralstor/integralstor/integral_view/integral_view_uwsgi.ini /etc/uwsgi/vassals/
cd /usr/lib/systemd/system
yes | cp -f /opt/integralstor/integralstor_tar_installs/uwsginew.service .
ln -s /usr/lib/systemd/system/uwsginew.service /etc/systemd/system/multi-user.target.wants/

### Configure ramdisks ###
#Change the ramdisks conf file name and location, move it into /opt/integralstor so it can be common to integralstor and gridcell
touch /opt/integralstor/ramdisks.conf
touch /var/log/integralstor/integralstor/ramdisks
#ln -fs /opt/integralstor/integralstor_utils/install/scripts/ramdisk /etc/init.d/
ln -s /usr/lib/systemd/system/ramdisk.service /etc/systemd/system/multi-user.target.wants/

###configure crontab ###
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

###configure ZFS ###
rm -f /etc/modprobe.d/zfs.conf
ln -fs /opt/integralstor/integralstor_utils/install/conf_files/zfs.conf /etc/modprobe.d
cp -rf /opt/integralstor/integralstor/install/conf_files/zed.rc /etc/zfs/zed.d

### configuring Vsftpd ###
rm -f /etc/vsftpd/vsftpd.conf
ln -fs /opt/integralstor/integralstor/install/conf_files/vsftpd.conf /etc/vsftpd

#Log rotation 
cp -f /etc/logrotate.d/* /etc/logrotate.d_old/
cp -f /opt/integralstor/integralstor/install/log_rotate_files/* /etc/logrotate.d/

### configuring zed for zfs ###
ln -s /opt/integralstor/integralstor/install/conf_files/zed.conf /etc/init/

### Configure rc.local ###
modprobe ipmi_devintf
modprobe 8021q

if grep "dell" /opt/integralstor/platform > /dev/null
then
  (crontab -l 2>/dev/null; echo "@reboot srvadmin-services.sh restart > /tmp/srvadmin_logs >> /tmp/srvadmin_errors") | crontab -
  echo "copying integralstor repository..."
  echo "Please install dell specific dependencies(srvadmin-all&dell-system-update) when you have dell hardware"
#  cd /etc/yum.repos.d
#  /usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/integralstor.repo
#  echo "copying integralstor repository...Done"
#  echo "installing dell specific dependencies..."
#  yum install srvadmin-all dell-system-update -y
#  echo "installing dell specific dependencies...Done"
#  echo "disabling integralstor repository..."
#  sed -i '/\[updates\]/a enabled=0' /etc/yum.repos.d/integralstor.repo 
#  echo "disabling integralstor repository...Done":w
else
  echo "Non dell hardware. Exiting..."
fi

### Grub and other file modification to show title/name Integralstor instead Centos 7.2 ###
cd /etc
mv issue issue.bak
mv /usr/share/plymouth/themes/text/text.plymouth /usr/share/plymouth/themes/text/text.plymouth.bak
cp -f /opt/integralstor/integralstor/install/conf_files/text.plymouth /usr/share/plymouth/themes/text/

### Display pre login message ###
cp -f /opt/integralstor/integralstor/install/conf_files/issue /etc/

# Run login_menu.sh after user login
ln -s /opt/integralstor/integralstor/scripts/shell/login_menu.sh /etc/profile.d/spring_up.sh

### creating integralstor config dg ###
cd /opt/integralstor/integralstor/config/db/
rm -f integral_view_config.db
sqlite3 integral_view_config.db < schemas

### removing execute permission on these service files ###
chmod -x /usr/lib/systemd/system/urbackup-server.service
chmod -x /usr/lib/systemd/system/tgtd.service
sed -i "s/^TasksMax.*/ /g" /usr/lib/systemd/system/urbackup-server.service

### Removing install files after install
cd /opt/integralstor
echo "Removing installation files..."
rm -rf initial_setup.sh integralstor_rpm_post.sh integralstor_tar_installs*
echo "Removing installation files...Done"

sleep 2

### Turn on other services ###
echo "Start and Enabling necessary services..."
systemctl start rpcbind && systemctl enable rpcbind
systemctl start nfs-server && systemctl enable nfs-server
systemctl start winbind && systemctl enable winbind
systemctl start smb && systemctl enable smb
systemctl start tgtd && systemctl enable tgtd
systemctl start ntpd && systemctl enable ntpd
systemctl start crond && systemctl enable crond
systemctl start ramdisk && systemctl enable ramdisk
systemctl start vsftpd && systemctl enable vsftpd
systemctl start shellinaboxd && systemctl enable shellinaboxd
systemctl start uwsginew && systemctl enable uwsginew
systemctl start nginx && systemctl enable nginx
systemctl daemon-reload
echo "Start and Enabling necessary services...Done"

echo "Completed post install operations. Reboot the machine to changes take affect."
