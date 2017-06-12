#!/bin/bash

echo '''
         ###############################################################
        #                                               		#
        #                                               		#
        #     ///***IntegralSTOR UniCELL RPM creation SCRIPT***\\\     	#
        #                                               		#
        #                                               		#
         ###############################################################

*NOTE:
"Your Machine must be configured with git basic settings with https or ssh in order to do a clone of integral view. "
"The clone will be taken from https://$github_username@github.com/fractalio/integral-view.git "
"Make sure that the Branch you mention should also be available publically with public repo"
#naveen.mh08@gmail.com
''' 

#### To force the user to be a super-user: root ###
if [[ $EUID != 0 ]]; then
  echo "You must be root to run this script !! Login as \"root\" and try again." 2>&1
  exit -1
fi

### Changing dir to /tmp/integralstor_rpm dir ###
cd /tmp/integralstor_rpm
rm -rf /tmp/integralstor_rpm/integralstor
rm -rf /tmp/integralstor_rpm/integralstor_utils

### To clone the integralstor.git and integralstor_utils.git ###
git clone https://github.com/fractalio/integralstor_utils.git
git clone https://github.com/fractalio/integralstor.git
echo

### Letting user to checkout branch or tag or default will be last tag ###
echo "Do you want to Download specific Branch or Tag...???"
echo "Press 'YES' else press <ENTER> to Download the latest tag for both integralstor and integralstor_utils"
read input1
    if [[ $input1 == "y" || $input1 == "Y" || $input1 == "yes" || $input1 == "Yes" || $input1 == "YES" ]] ; then

	echo "Download BRANCH or TAG for integralstor_utils??? If branch, enter 'branch' else 'tag'"
	read input2
	if [[ $input2 == "branch" ]] ; then
	    	cd /tmp/integralstor_rpm/integralstor_utils
	    echo "Available Git Branches for integralstor_utils:"
	    echo
	    	git branch -a
	    echo
	    read -p "Please enter the branch name for integralstor_utils: " branchcmmn	# change the branch name as per the requirement
	    echo
	    	git checkout $branchcmmn 
	    	touch /tmp/integralstor_rpm/integralstor_utils/version
	    echo "$branchcmmn" > /tmp/integralstor_rpm/integralstor_utils/version	
	    echo "Downloaded from Branch:"
	    	git branch
	elif [[ $input2 == "tag" ]] ; then
	    	cd /tmp/integralstor_rpm/integralstor_utils
	    echo "Available Git Tags for integralstor_utils:"
	    echo
	    	git tag -l
	    echo
	    read -p "Please enter the tag name for integralstor_utils: " tagcmmn	# change the branch name as per the requirement
	    	cd /tmp/integralstor_rpm/integralstor_utils/
	    	git checkout tags/$tagcmmn 
	    	touch /tmp/integralstor_rpm/integralstor_utils/version
	    echo "$tagcmmn" > /tmp/integralstor_rpm/integralstor_utils/version	
	    echo "Downloaded from Tag: $tagcmmn"
	else
		"Go back and enter appropriate input."
	fi
	echo "Download BRANCH or TAG integralstor??? If branch, enter 'branch' else 'tag'"
	read input3
	if [[ $input3 == "branch" ]] ; then
	    	cd /tmp/integralstor_rpm/integralstor
	    echo "Available Git Branches for integralstor:"
	    echo
	    	git branch -a
	    echo
	    read -p "Please enter the branch name for integralstor: " branchuni # change the branch name as per the requirement
	    echo
	    	git checkout $branchuni
	    	touch /tmp/integralstor_rpm/integralstor/version
	    echo "$branchuni" > /tmp/integralstor_rpm/integralstor/version	
	    echo "Downloaded from Branch:"
	    	git branch
	elif [[ $input3 == "tag" ]] ; then
	    	cd /tmp/integralstor_rpm/integralstor
	    echo "Available Git Tags for integralstor:"
	    	git tag -l
	    echo
	    read -p "Please enter the tag name for integrlator_integralstor: " taguni	# change the branch name as per the requirement
	    	cd /tmp/integralstor_rpm/integralstor/
	    	git checkout tags/$taguni
	    	touch /tmp/integralstor_rpm/integralstor/version
	    echo "$taguni" > /tmp/integralstor_rpm/integralstor/version	
	    echo "Downloaded from Tag: $taguni"
	else
		"Go back and enter appropriate input."
	fi

    elif [[ $input1 == "n" || $input1 == "N" || $input1 == "no" || $input1 == "No" || $input1 == "NO" || $input1 == "" || $input1 == " " ]] ; then

	cd /tmp/integralstor_rpm/integralstor_utils
        TAGCMMN=$(git describe $(git rev-list --tags --max-count=1))
	git checkout tags/$TAGCMMN
	touch /tmp/integralstor_rpm/integralstor_utils/version
	echo "$TAGCMMN" > /tmp/integralstor_rpm/integralstor_utils/version	
	echo "Downloaded from Tag: $TAGCMMN"
	
	cd /tmp/integralstor_rpm/integralstor
        TAGUNI=$(git describe $(git rev-list --tags --max-count=1))
	git checkout tags/$TAGUNI
	touch /tmp/integralstor_rpm/integralstor/version
	echo "$TAGUNI" > /tmp/integralstor_rpm/integralstor/version	
	echo "Downloaded from Tag: $TAGUNI"
    else
	"Go back and enter appropriate input."
    fi

### Unicell rpm creation part ###
rm -rf /root/rpmbuild

# To Create RPM Build Environment
echo
echo "Creating RPM Building environment .."
rpm_path="/root/rpmbuild/"

mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $HOME)/rpmbuild
%_tmppath  %{_topdir}/tmp
EOF


# Directory creation
mkdir /tmp/integralstor_rpm/integralstor-1.0
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor/pki
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/run/samba
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/var/log/integralstor/integralstor
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor/integralstor/tmp
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor/integralstor/config/status
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/etc/nginx/sites-enabled
mkdir -p /tmp/integralstor_rpm/integralstor-1.0/etc/uwsgi/vassals
touch /tmp/integralstor_rpm/integralstor-1.0/var/log/integralstor/integralstor/integral_view.log
touch /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor/ramdisks.conf
touch /tmp/integralstor_rpm/integralstor-1.0/var/log/integralstor/integralstor/ramdisks

# MANAGE.PY FILE 
cp -rf /tmp/integralstor_rpm/integralstor_utils /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor
cp -rf /tmp/integralstor_rpm/integralstor /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor
cp -rf /tmp/integralstor_rpm/integralstor_rpms.tar.gz /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor
cp -rf /tmp/integralstor_rpm/integralstor_tar_installs.tar.gz /tmp/integralstor_rpm/integralstor-1.0/opt/integralstor

# NOW MOVE THE /tmp/integralstor_rpm/integralstor-1.0/ to where ?
cd /tmp/integralstor_rpm/
tar -cvzf integralstor-1.0.tar.gz integralstor-1.0/
cp -rf /tmp/integralstor_rpm/integralstor-1.0/ ~/rpmbuild/SOURCES/
cp -rf /tmp/integralstor_rpm/integralstor-1.0.tar.gz ~/rpmbuild/SOURCES/
# INSERT THE .spec FILE INTO ~/rpmbuild/SPECS/

cat <<EOF > /root/rpmbuild/SPECS/integralstor.spec

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:       Installs the IntegralSTOR UniCELL packages and its dependencies for using IntegralSOTR UniCELL (A NAS).  
Name:          integralstor
Version:       1.0
Release:       1
License:       Fractalio Custom Licence
Group:         Development/Tools
SOURCE0:       %{name}-%{version}.tar.gz
URL:           http://www.fractalio.com/
BuildRoot:     %{_tmppath}/%{name}-%{version}-root

%description
This package installs the IntegralView - a management Graphical User Interface (GUI) for the IntegralSTOR Hardware. This package creates /opt/integralstor/.. directory structure and and also adds required entries in the /etc/rc.local file on that machine.

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%preun
#rm -rf /config/*nnth

%files
%defattr(-,root,root,-)
#%dir /config/
/opt/integralstor/
/etc/nginx/sites-enabled
/etc/uwsgi/vassals
#/srv/*
#/usr/lib/python2.6/site-packages/*
/var/
/run/samba/

%post
#!/bin/bash

selinux --disabled
service iptables stop
service ip6tables stop
service firewalld stop
chkconfig iptables off
chkconfig ip6tables off

sh /opt/integralstor/integralstor/install/rpm/pre_package_install.sh

### Adding a user and group called integralstor. ###
groupadd integralstor -g 500
useradd integralstor -g 500
groupadd replicator -g 501
useradd replicator -g 501
echo "integralstor123" | passwd --stdin integralstor
echo "replicator123" | passwd --stdin replicator
echo "integralstor    ALL=(ALL)    ALL" >> /etc/sudoers
echo "replicator    ALL=(ALL)    NOPASSWD: /sbin/zfs" >> /etc/sudoers
#echo "AllowUsers replicator integralstor" >> /etc/ssh/sshd_config #root is allowed temp. untill fixes for replicator.

### Setting hostname ###
STRING=$(ifconfig | grep eth0 | head -1 | awk '{print $5}' | awk -F ':' '{print tolower($5 $6)}')
hnpart="integralstor-"$STRING
hostname="$hnpart.integralstor.lan"
echo "Hostname will be : " $hostname ; echo
echo "HOSTNAME=$hostname" > /etc/sysconfig/network
echo "NETWORKING=yes" >> /etc/sysconfig/network
# Editing /etc/hosts
ip=$(ifconfig | awk -F':' '/inet addr/&&!/127.0.0.1/{split($2,_," ");print _[1]}')
echo "$ip $hnpart $hostname" >> /etc/hosts

### Disabling BOOTPROTO for all interfaces ###
INTERFACES="eth0 eth1 eth2 eth3"
for IF in $INTERFACES
do
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-$IF
done

### SSHD configuration ###
/etc/init.d/sshd stop
sed '' /etc/ssh/sshd_config > /etc/ssh/original_sshd_config
sed '/#PermitRootLogin/a PermitRootLogin no' /etc/ssh/sshd_config > /etc/ssh/temp_file
#echo 'AllowUsers integralstor' >> /etc/ssh/temp_file
sed -e '/requiretty/s/^/#/g' -i /etc/sudoers    #serach for requiretty and comment. This is to avoid tty for replication in zfs send/receive
rm -f /etc/ssh/sshd_config
mv /etc/ssh/temp_file /etc/ssh/sshd_config
/etc/init.d/sshd start
ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ''

### Editing the /etc/yum.repos.d/CentOS-Base.repo ###
# ..to disable base, updates and extras repositories. ###

cp -rf /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/Original-CentOS-Base-repo
sed -i '/\[base\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
sed -i '/\[updates\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo 
sed -i '/\[extras\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
sed -i '/\[centosplus\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo
sed -i '/\[contrib\]/a enabled=0' /etc/yum.repos.d/CentOS-Base.repo

ln -s /opt/integralstor/integralstor_utils/site-packages/integralstor_utils /usr/lib/python2.6/site-packages/integralstor_utils
ln -s /opt/integralstor/integralstor/site-packages/integralstor /usr/lib/python2.6/site-packages/integralstor

ln -s /opt/integralstor/integralstor/platform /opt/integralstor
mv /etc/sysconfig/shellinaboxd /etc/sysconfig/shellinaboxd.bak
ln -s /opt/integralstor/integralstor/config/shellinabox/shellinaboxd /etc/sysconfig
echo "self" >> /opt/integralstor/integralstor/platform
chmod 755 /opt/integralstor/integralstor/scripts/python/*
chmod 755 /opt/integralstor/integralstor/scripts/shell/*
rm -rf /etc/init/start-ttys.conf
cp -f /opt/integralstor/integralstor/install/conf_files/start-ttys.conf /etc/init
cp -f /opt/integralstor/integralstor/install/conf_files/integralstor_menu.conf /etc/init
rm -rf /etc/nsswitch.conf
cp /opt/integralstor/integralstor/install/conf_files/nsswitch.conf /etc

### Configure nginx ###
ln -s /opt/integralstor/integralstor/integral_view/integral_view_nginx.conf /etc/nginx/sites-enabled/
sed -i 's/conf.d/sites-enabled/g' /etc/nginx/nginx.conf

### Cinfigure xinetd ###
cd /etc/xinetd.d/
mv rsync rsync.bak
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor/v1.0/rsync
#sed -i 's/disable = yes/disable = no/' /etc/xinetd.d/rsync

### Configure uwsgi ###
ln -s /opt/integralstor/integralstor/integral_view/integral_view_uwsgi.ini /etc/uwsgi/vassals/
echo "/usr/bin/uwsgi --emperor /etc/uwsgi/vassals --uid root --gid root >/var/log/integralstor/integralstor/integral_view.log 2>&1 &" >> /etc/rc.local
sed -i "/\/usr\/local\/bin\/uwsgi --emperor \/etc\/uwsgi\/vassals --uid root --gid root/d" /etc/rc.local
rm -rf /etc/init.d/uwsgi
ln -s /opt/integralstor/integralstor_utils/scripts/init/uwsgi /etc/init.d/

### Configure ramdisks ###
#Change the ramdisks conf file name and location, move it into /opt/integralstor so it can be common to integralstor and gridcell
rm -rf /etc/init.d/ramdisk
ln -fs /opt/integralstor/integralstor_utils/install/scripts/ramdisk /etc/init.d/
chmod +x /etc/init.d/ramdisk

### copying kmod-mv94xx directory to systems kernel Directory(This is spesific to Marvel servers) ###
cp -rf /lib/modules/2.6.32-431.el6.x86_64/extra/mv94xx /lib/modules/2.6.32-504.el6.x86_64/extra


onfigure crontab ###
(crontab -l 2>/dev/null; echo 'MAILTO=""') | crontab -
(crontab -l 2>/dev/null; echo "SHELL=/bin/sh") | crontab -
(crontab -l 2>/dev/null; echo "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_utils/scripts/python/generate_status.py > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/lib64/sa/sa1 1 1 -S DISK > /tmp/out_status >> /tmp/err_status") | crontab -
(crontab -l 2>/dev/null; echo "10,40 * * * * /usr/bin/python -c 'from integralstor_utils import zfs; zfs.execute_remote_replication()' > /tmp/replication_alerts >> /tmp/replication_errors") | crontab -
(crontab -l 2>/dev/null; echo "*/1 * * * * /opt/integralstor/integralstor_utils/scripts/python/poll_for_alerts.py > /tmp/out_alerts >> /tmp/err_alerts") | crontab -
(crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python -c 'from integralstor_utils import scheduler_utils; scheduler_utils.run_from_shell()' > /tmp/scheduler_alerts >> /tmp/scheduler_errors") | crontab -
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/bin/python -c 'from integralstor_utils import logs; logs.auto_rotate_logs()' > /tmp/auto_rotate_logs_alerts >> /tmp/auto_rotate_errors") | crontab -

###configure ZFS ###
rm -f /etc/modprobe.d/zfs.conf
ln -fs /opt/integralstor/integralstor_utils/install/conf_files/zfs.conf /etc/modprobe.d
cp -rf /opt/integralstor/integralstor/install/conf_files/zed.rc /etc/zfs/zed.d

### configuring Vsftpd ###
rm -f /etc/vsftpd/vsftpd.conf
ln -fs /opt/integralstor/integralstor/install/conf_files/vsftpd.conf /etc/vsftpd

### configuring zed for zfs ###
#cd /etc/zfs
#/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor/v1.0/zed.d
cd /etc/init/
/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor/v1.0/zed.conf
#cd /etc/sysconfig/modules/
#/usr/bin/wget -c http://192.168.1.150/netboot/distros/centos/6.6/x86_64/integralstor/v1.0/zfs.modules #laoding ZFS module

### Configure rc.local ###
modprobe ipmi_devintf
modprobe 8021q
cp -f /sbin/zed /etc/init.d
echo "/sbin/zed" >> /etc/rc.local
echo "modprobe ipmi_devintf" >> /etc/rc.local
echo "/sbin/modprobe zfs" >> /etc/rc.local
chmod 755 /etc/rc.local
ln -sf /etc/rc.local /etc/rc3.d/S99local

#%podstun

%changelog

* Thu Sep 29 2016 Naveenkumar <naveen@fractalio.com> 1.0
- Created neccessary directories and linked files for respective directories as per the ks file
- First Build

####
#Expecting Post install verification script here.
####

EOF

# To create a rpm
rpmbuild -ba /root/rpmbuild/SPECS/integralstor.spec

echo "Successfully created the IntegralSTOR UniCELL RPM!"
ls /root/rpmbuild/RPMS/x86_64/
#echo "Deleting the /tmp/integralstor"
#if [ -e "/tmp/integralstor_rpm/integralstor" ] ; then
#  cp -r /tmp/integralstor/configuration_management/login_menu/* /srv/salt/conf_files/
#  #rm -rf /tmp/integralstor
#  echo "The /tmp/integralstor got deleted."
#  echo "Executing ls -l /tmp/integralstor : " 
#  ls -l /tmp/integralstor
#
#else
#  rm -rf "Directory /tmp/integralstor cannot be deleted. "
#fi
               

