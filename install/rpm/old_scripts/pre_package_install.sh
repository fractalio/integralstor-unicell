#!bin/bash

echo "Switching to working directory..."
cd /opt/integralstor
tar xzf integralstor_rpms.tar.gz

echo "Creating and Enabling fractalio repository..."
cat << EOF > /etc/yum.repos.d/fractalio.repo
[fractalio]
enabled=0
name= Fractalio - Base
baseurl=file:///opt/integralstor/integralstor_rpms
gpgcheck=0
EOF

cd /tmp

yum-config-manager --disable "*"
yum-config-manager --enable "fractalio"

echo "Started installing dependencies..."
echo
PACKAGE_LIST="salt-master salt-minion python-pip ypbind ypserv ntp uwsgi nginx kexec-tools fractalio_django python-devel vsftpd sg3_utils perl-Config-General scsi-target-utils nfs-utils smartmontools samba-client samba samba-winbind samba-winbind-clients ipmitool OpenIPMI zfs krb5-workstation perl zlib python-setuptools gcc kmod-mv94xx xinetd shellinabox wget"

for pkg in $PACKAGE_LIST; do
    if ! rpm -qa | grep $pkg ; then
	echo "$pkg is not found, installing locally..."
        yes | yum install $pkg 
	echo "...Done." 
    fi
done

echo "Dependencies installed successfully."

echo "Started installing Non rpm installs..."

cd /opt/integralstor
tar xzf integralstor_tar_installs.tar.gz
cd /opt/integralstor/integralstor_tar_installs

cd sysstat-11.0.5
./configure --prefix=/usr
make
make install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf sysstat-11.0.5

cd /opt/integralstor/integralstor_tar_installs
tar xzf setuptools-11.3.1.tar.gz
cd setuptools-11.3.1
python setup.py install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf setuptools-11.3.1.tar.gz

cd /opt/integralstor/integralstor_tar_installs
tar xzf uwsgi-2.0.9.tar.gz
cd uwsgi-2.0.9
python setup.py install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf uwsgi-2.0.9.tar.gz

cd /opt/integralstor/integralstor_tar_installs
tar xzf netifaces-0.10.4.tar.gz
cd netifaces-0.10.4
python setup.py install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf netifaces-0.10.4.tar.gz

cd /opt/integralstor/integralstor_tar_installs
tar xzf python-dateutil-2.4.2.tar.gz
cd python-dateutil-2.4.2
python setup.py install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf python-dateutil-2.4.2.tar.gz

cd /opt/integralstor/integralstor_tar_installs
tar xzf python-crontab-1.9.3.tar.gz
cd python-crontab-1.9.3
python setup.py install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf python-crontab-1.9.3.tar.gz

cd /opt/integralstor/integralstor_tar_installs
tar xzf zfs-auto-snapshot.tar.gz
cd zfs-auto-snapshot
make install
sleep 1
cd /opt/integralstor/integralstor_tar_installs
rm -rf zfs-auto-snapshot.tar.gz

cd /opt/integralstor
rm -rf /opt/integralstor/integralstor_*

echo "Successfully installed Non RPM installs."

echo "Intiating Integralstor_integralstor RPM..."

yum-config-manager --disable "*"
