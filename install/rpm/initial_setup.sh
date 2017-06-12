#!/bin/bash

echo "Installing Dependencies for integralstor rpm..."

### Disable selinux and firewall
echo "Disabling selinux..."
sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
systemctl stop iptables
systemctl stop ip6tables
systemctl disable iptables
systemctl disable ip6tables

### any vendor specific entry
echo -n "Enter hardware vendor(ex., dell) else press <ENTER>:"
read vend

if [[ -n "$vend" ]]; then
  echo { \"platform\": \"integralstor\", > /tmp/platform
  echo \"hardware_vendor\" : \"$vend\" } >> /tmp/platform
  echo ""
  echo -n "Entered vendor is: $vend" 
  echo ""
else
  echo { \"platform\": \"integralstor\" } > /tmp/platform
  echo ""
  echo -n "platform is 'integralstor'" 
  echo ""
fi

### Create integralstor.repo
cat <<EOF > /etc/yum.repos.d/integralstor.repo
[integralstor]
enabled=1
name= integralstor - base
baseurl=file:///opt/integralstor/integralstor_rpms
gpgcheck=0
EOF

### Install yum-utils from any of the repositories
echo "Installing yum-utils-1.1.31..."
yum install -y yum-utils-1.1.31

if [ $? -ne 0 ]; then
    echo "CRITICAL: Installing 'yum-utils-1.1.31' Failed!"
    exit 1
else
    echo "Installing yum-utils-1.1.31...Done"
fi

### Disable all other repositories...
echo "Disabling all repositories..."
yum-config-manager --disable "*"

if [ $? -ne 0 ]; then
    echo "CRITICAL: Disabling all repository Failed!"
    exit 1
else
    echo "Disabling all repositories...Done"
fi

### Enable integralstor repository
echo "Enabling integralstor repository..."
yum-config-manager --enable integralstor

if [ $? -ne 0 ]; then
    echo "CRITICAL: Enabling integralstor repository Failed!"
    exit 1
else
    echo "Enabling integralstor repository...Done"
fi

### Install kernel specific headers and devel packages
echo "Installing kernel spaecific kernel-headers and kernel-devel..."
yum install -y kernel-devel-3.10.0 kernel-headers-3.10.0

if [ $? -ne 0 ]; then
    echo "CRITICAL: Installing 'kernel specific kernel-headers and kernel-devel' Failed!"
    exit 1
else
    echo "Installing kernel spaecific kernel-headers and kernel-devel...Done"
fi

### Enable all required repositories if present
echo "Enabling all required repositories..."
yum-config-manager --enable base epel zfs integralstor

if [ $? -ne 0 ]; then
    echo "CRITICAL: Enabling all required repositories Failed!"
    exit 1
else
    echo "Enabling all required repositories...Done"
fi

### Install required dependencies for integralstor rpm
echo "Installing all other required dependencies..."
yum install -y yum-utils-1.1.31 sg3_utils-1.37 perl-Config-General-2.61 scsi-target-utils-1.0.55 nfs-utils-1.3.0 smartmontools-6.2 samba-client-4.2.10 samba-4.2.10 samba-winbind-4.2.10 samba-winbind-clients-4.2.10 ipmitool-1.8.13 OpenIPMI-2.0.19 zfs-0.6.5.7 krb5-workstation-1.13.2 perl-5.16.3 python-setuptools-0.9.8 python2-pip-8.1.2 ypbind-1.37.1 ypserv-2.31 ntp-4.2.6p5 nginx-1.6.3 uwsgi-2.0.12 python-devel-2.7.5 gcc-4.8.5 vsftpd-3.0.2 xinetd-2.3.15 shellinabox-2.19 urbackup-server-2.0.38.1660 bind-utils-9.9.4 rsync-3.0.9 telnet-0.17 vim-enhanced-7.4.160 iptraf-ng-1.1.4 pytz-2012d tzdata-2017b fio-2.2.8 iftop-1.0 iperf3-3.1.6 inotify-tools-3.14

if [ $? -ne 0 ]; then
    echo "CRITICAL: Installing all other required dependencies...Failed!"
    exit 1
else
    echo "Installing all other required dependencies...Done"
fi

sleep 2

echo "Installing Dependencies for integralstor rpm...Done"
echo "Run 'rpm -ivh integralstor-*.rpm to install integralstor."
