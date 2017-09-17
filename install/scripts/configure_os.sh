#!/bin/bash

hardware_vendor=""
[ -n "$1" ] && hardware_vendor=$1

# Add users and groups
groupadd integralstor -g 1000
useradd integralstor -g 1000
useradd replicator -g 1000
groupadd console -g 1002
useradd console -g 1002
groupadd nagios -g 1003
useradd nagios -g 1003

echo "integralstor123" | passwd --stdin integralstor
echo "replicator123" | passwd --stdin replicator
echo "console123" | passwd --stdin console
echo "nagios123" | passwd --stdin nagios
echo "integralstor    ALL=(ALL)    ALL" >> /etc/sudoers
echo "replicator    ALL=(ALL)    NOPASSWD: /usr/sbin/zfs,/usr/bin/rsync,/bin/rsync,/usr/bin/ssh" >> /etc/sudoers
echo "console    ALL=(ALL)    NOPASSWD: ALL" >> /etc/sudoers


# Change MIN_UID and MIN_GID to start from 1500 for local users
sed -i "s/^UID_MIN.*/UID_MIN                  1500/g" /etc/login.defs
sed -i "s/^GID_MIN.*/GID_MIN                  1500/g" /etc/login.defs


# Allow Network Manager to control network interfaces
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-eno*
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-enp*
sed -i 's/NM_CONTROLLED=no/NM_CONTROLLED=yes/' /etc/sysconfig/network-scripts/ifcfg-em*


# Avoid tty for clean ZFS remote replication process
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers


# Create required Integralstor specific directories
mkdir -p /var/log/integralstor/logs/
mkdir -p /var/log/integralstor/logs/scripts/
mkdir -p /var/log/integralstor/logs/tasks/
mkdir -p /var/log/integralstor/logs/cron/
mkdir -p /var/log/integralstor/logs/exported/
mkdir -p /var/log/integralstor/archives/
mkdir -p /var/log/integralstor/archives/config/
mkdir -p /var/log/integralstor/archives/logs/
mkdir -p /var/log/integralstor/reports/
mkdir -p /var/log/integralstor/reports/urbackup/
mkdir -p /var/log/integralstor/reports/integralstor_status/

mkdir -p /opt/integralstor/integralstor/config
mkdir -p /opt/integralstor/integralstor/config/db
mkdir -p /opt/integralstor/integralstor/config/status
mkdir -p /opt/integralstor/integralstor/config/pki
mkdir -p /opt/integralstor/integralstor/config/conf_files

chmod -R 777 /var/log/integralstor
chmod -R 755 /opt/integralstor/integralstor/scripts/python/*
chmod -R 755 /opt/integralstor/integralstor/scripts/shell/*

touch /var/log/integralstor/logs/scripts/scripts.log
touch /var/log/integralstor/logs/scripts/integral_view.log
touch /var/log/integralstor/logs/scripts/ramdisks


# Set platform and hardware vendor
if [ -z "$hardware_vendor" ]; then
  printf '{"platform": "integralstor"}\n' > /opt/integralstor/integralstor/platform
else
  printf '{"platform": "integralstor",\n "hardware_vendor": "%s"}\n' "$hardware_vendor" > /opt/integralstor/integralstor/platform
fi

ln -s /opt/integralstor/integralstor/platform /opt/integralstor


# Anacron
sed -i 's/RANDOM_DELAY=45/RANDOM_DELAY=5/' /etc/anacrontab
sed -i 's/START_HOURS_RANGE=3-22/START_HOURS_RANGE=0-1/' /etc/anacrontab


# Set ownership to nagios
# TODO: Required?
chown -R nagios:nagios /usr/local/nagios &> /dev/null


# Create Integralstor databases
rm -rf /opt/integralstor/integralstor/config/db/*
cp /opt/integralstor/integralstor/install/conf-files/db/*.db /opt/integralstor/integralstor/config/db/
sqlite3 /opt/integralstor/integralstor/config/db/integralstor.db < /opt/integralstor/integralstor/install/conf-files/db/integralstor_db.schema

# Populate cron entries
# ALERT: clears existing entries
crontab -r
cat /opt/integralstor/integralstor/install/scripts/cron_entries.list | crontab -

# Link site-packages with python libraries dir
ln -s /opt/integralstor/integralstor/site-packages/integralstor /usr/lib/python2.7/site-packages/integralstor

# Disable printing kernel messages(dmesg) to console
cat >> /etc/rc.d/rc.local << __eof__
dmesg -n 1
__eof__

