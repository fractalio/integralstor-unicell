#!/bin/bash

### change the version number, release number and architecture whenever we create rpm ###
version_number=1.4.0
release_number=1
arch=noarch
working_dir=/root/integralstor_rpm

if [ $(id -u) != "0" ]; then
    echo "You must be the superuser to run this script" >&2
    exit 1
fi

### creating local working directory to store files ###
if [[ ! -d "$working_dir" ]]; then
    echo
    echo "Creating integralstor working Directory..."
    mkdir -p $working_dir
    echo "Creating integralstor working Directory...Done"
else
    echo "integralstor working Directory exist continuing..."
fi

### pulling integralstor code from git ###
# Changing dir to /tmp dir
echo
cd /tmp
rm -rf /tmp/integralstor*
rm -rf /tmp/integralstor_utils*

# To clone the integral-view.git
git clone https://github.com/integralstor/integralstor_utils.git
git clone https://github.com/integralstor/integralstor.git
echo

echo "Want to pull specific BRANCH and/or TAG? Press <YES> else Press <ENTER> to pull automatically the latest tag for Both Uniccell and common:"
read input1
    if [[ $input1 == "y" || $input1 == "Y" || $input1 == "yes" || $input1 == "Yes" || $input1 == "YES" ]] ; then

        echo "You are in 'integralstor_utils' now. To pull from any branch, enter 'branch' else enter 'tag'"
        read input2
        if [[ $input2 == "branch" ]] ; then
                cd /tmp/integralstor_utils
                echo "Available Git 'branches' are:"
                echo
                git branch -a
            echo
            read -p "Enter required branch from above: " branchcmmn     # change the branch name as per the requirement
            echo
                git checkout $branchcmmn
                touch /tmp/integralstor_utils/version
            echo "$branchcmmn" > /tmp/integralstor_utils/version
            echo "Downloaded from Branch :"
                git branch
                cd /tmp
                rm -rf /tmp/integralstor_utils/.git*
                yes | cp -rf /tmp/integralstor_utils $working_dir
        elif [[ $input2 == "tag" ]] ; then
                cd /tmp/integralstor_utils
            echo "Available Git 'tags' are:"
            echo
                git tag -l
            echo
            read -p "Enter required tag from above: " tagcmmn   # change the branch name as per the requirement
                git checkout tags/$tagcmmn
                touch /tmp/integralstor_utils/version
            echo "$tagcmmn" > /tmp/integralstor_utils/version
            echo "Downloaded from Tag: $tagcmmn"
                #git tag
                cd /tmp
                rm -rf /tmp/integralstor_utils/.git*
                yes | cp -rf /tmp/integralstor_utils $working_dir
        else
                echo "Go back and enter appropriate input."
        fi
        echo "You are in 'integralstor' now. To pull from branch, enter 'branch' else enter 'tag'"
        read input3
        if [[ $input3 == "branch" ]] ; then
                cd /tmp/integralstor
            echo "Available Git 'branches' are:"
            echo
                git branch -a
            echo
            read -p "Enter required branch from above : " branchuni # change the branch name as per the requirement
            echo
                git checkout $branchuni
                touch /tmp/integralstor/version
            echo "$branchuni" > /tmp/integralstor/version
            sed -i "s/version=.*/version=$branchuni/g"  /tmp/integralstor/install/ks/ksintegralstor.cfg
            sed -i "s/version=.*/version=$branchuni/g"  /tmp/integralstor/install/ks/centos7/ksintegralstor.cfg
            echo "Downloaded from Branch:"
                git branch
                cd /tmp
                rm -rf /tmp/integralstor/.git*
                yes | cp -rf /tmp/integralstor $working_dir
        elif [[ $input3 == "tag" ]] ; then
                cd /tmp/integralstor
            echo "Available Git 'tags' are :"
                git tag -l
            echo
            read -p "Enter required tag from above : " taguni   # change the branch name as per the requirement
                cd /tmp/integralstor/
                git checkout tags/$taguni
                touch /tmp/integralstor/version
            echo "$taguni" > /tmp/integralstor/version
            sed -i "s/version=.*/version=$taguni/g"  /tmp/integralstor/install/ks/ksintegralstor.cfg
            sed -i "s/version=.*/version=$taguni/g"  /tmp/integralstor/install/ks/centos7/ksintegralstor.cfg
            echo "Downloaded from Tag: $taguni"
                #git tag
                cd /tmp
                rm -rf /tmp/integralstor/.git*
                yes | cp -rf /tmp/integralstor $working_dir
        else
                echo "Go back and enter appropriate input."
        fi

    elif [[ $input1 == "n" || $input1 == "N" || $input1 == "no" || $input1 == "No" || $input1 == "NO" || $input1 == "" || $input1 == " " ]] ; then

        cd /tmp/integralstor_utils
        TAGCMMN=$(git describe $(git rev-list --tags --max-count=1))
        git checkout tags/$TAGCMMN
        touch /tmp/integralstor_utils/version
        echo "$TAGCMMN" > /tmp/integralstor_utils/version
        echo "Downloaded from Tag: $TAGCMMN"
        #git tag
        cd /tmp
        rm -rf /tmp/integralstor_utils/.git*
        yes | cp -rf /tmp/integralstor_utils $working_dir

        cd /tmp/integralstor
        TAGUNI=$(git describe $(git rev-list --tags --max-count=1))
        git checkout tags/$TAGUNI
        touch /tmp/integralstor/version
        echo "$TAGUNI" > /tmp/integralstor/version
        sed -i "s/version=.*/version=$TAGUNI/g"  /tmp/integralstor/install/ks/ksintegralstor.cfg
        sed -i "s/version=.*/version=$TAGUNI/g"  /tmp/integralstor/install/ks/centos7/ksintegralstor.cfg
        echo "Downloaded from Tag: $TAGUNI"
        cd /tmp
        rm -rf /tmp/integralstor/.git*
        yes | cp -rf /tmp/integralstor $working_dir
    else
        echo "Go back and enter appropriate input."
    fi

### copying non-rpm spftware files ###
cp -rf /var/www/html/netboot/distros/centos/7.2/x86_64/integralstor/v1.0/integralstor_tar_installs $working_dir

### Integralstor rpm creation part ###
rm -rf $working_dir/rpmbuild		# to delete any old data

### Create RPM Build Environment ###
echo
echo "Creating RPM Building environment .."
rpm_path="$working_dir/rpmbuild/"

mkdir -p $working_dir/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
mkdir -p $working_dir/rpmbuild/RPMS/{i386,i586,i686,noarch,x86_64}
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $working_dir)/rpmbuild
%_tmppath  %{_topdir}/tmp
%_unpackaged_files_terminate_build      0
%_binaries_in_noarch_packages_terminate_build   0
EOF

### Directory & files creation part ###

if [[ ! -d "$working_dir/integralstor-$version_number" ]]; then
    echo
    echo "Creating integralstor RPM Directory..."
    mkdir -p $working_dir/integralstor-$version_number
else
    echo "integralstor RPM Directory exist continuing..."
fi

echo
echo "Creating integralstor specific Directories..."

DIR_LIST="$working_dir/integralstor-${version_number}/opt/integralstor $working_dir/integralstor-${version_number}/opt/integralstor/pki $working_dir/integralstor-${version_number}/run/samba $working_dir/integralstor-${version_number}/var/log/integralstor/integralstor $working_dir/integralstor-${version_number}/opt/integralstor/integralstor/tmp $working_dir/integralstor-${version_number}/opt/integralstor/integralstor/config/status $working_dir/integralstor-${version_number}/etc/nginx/sites-enabled $working_dir/integralstor-${version_number}/etc/uwsgi/vassals $working_dir/integralstor-${version_number}/etc/logrotate.d_old $working_dir/integralstor-${version_number}/opt/integralstor/integralstor/config/logs/cron_logs $working_dir/integralstor-${version_number}/opt/integralstor/integralstor/config/logs/task_logs"

for dir in $DIR_LIST; do
    if [[ ! -d "$dir" ]]; then
        echo "'$dir' Directory Does Not Exist creating '$dir'"
	mkdir -p $dir
    fi
done

echo
echo "Creating integralstor specific Files..."

FILE_LIST="$working_dir/integralstor-${version_number}/var/log/integralstor/integralstor/integral_view.log $working_dir/integralstor-${version_number}/opt/integralstor/ramdisks.conf $working_dir/integralstor-${version_number}/var/log/integralstor/integralstor/ramdisks"
for file in $FILE_LIST; do
    if [[ ! -e "$file" ]]; then
        echo "'$file' File Does Not Exist Creating..."
	touch $file
    fi
done

### MANAGE FILE ###
cp -rf $working_dir/integralstor_utils $working_dir/integralstor-${version_number}/opt/integralstor
cp -rf $working_dir/integralstor $working_dir/integralstor-${version_number}/opt/integralstor

cp -rf $working_dir/integralstor_tar_installs.tar.gz $working_dir/integralstor-${version_number}/opt/integralstor
#cp -rf $working_dir/integralstor_rpm_post.sh $working_dir/integralstor-$version_number/opt/integralstor #comment if its in repo
#cp -rf $working_dir/initial_setup.sh $working_dir/integralstor-$version_number/opt/integralstor #comment if its in repo

### NOW MOVE THE $working_dir/integralstor-$version_number/ to where ? ###
cd $working_dir/
tar -cvzf integralstor-${version_number}.tar.gz integralstor-${version_number}/
yes | cp -rf $working_dir/integralstor-${version_number}/ $working_dir/rpmbuild/SOURCES/
yes | cp -rf $working_dir/integralstor-${version_number}.tar.gz $working_dir/rpmbuild/SOURCES/

# INSERT THE .spec FILE INTO ~/rpmbuild/SPECS/
cat <<EOF > $working_dir/rpmbuild/SPECS/integralstor.spec

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Summary:       IntegralSTOR - A NAS - unified storage platform.  
Name:          integralstor
Version:       ${version_number}
Release:       ${release_number}
License:       Fractalio Custom Licence
Group:         Development/Tools
Requires:      yum-utils = 1.1.31,sg3_utils = 1.37,perl-Config-General = 2.61,scsi-target-utils = 1.0.55,nfs-utils = 1:1.3.0,smartmontools = 1:6.2,samba-client = 4.2.10,samba = 4.2.10,samba-winbind = 4.2.10,samba-winbind-clients = 4.2.10,ipmitool = 1.8.13,OpenIPMI = 2.0.19,zfs = 0.6.5.7,krb5-workstation = 1.13.2,perl = 4:5.16.3,python-setuptools = 0.9.8,python2-pip = 8.1.2,ypbind = 3:1.37.1,ypserv = 2.31,ntp = 4.2.6p5,nginx = 1:1.6.3,uwsgi = 2.0.12,python-devel = 2.7.5,gcc = 4.8.5,vsftpd = 3.0.2,xinetd = 2:2.3.15,shellinabox = 2.19,urbackup-server = 2.0.38.1660,bind-utils = 32:9.9.4,rsync = 3.0.9,telnet = 1:0.17,vim-enhanced = 2:7.4.160,iptraf-ng = 1.1.4,pytz = 2012d,tzdata = 2017b,fio = 2.2.8,iftop = 1.0,iperf3 = 3.1.6,inotify-tools = 3.14
SOURCE0:       %{name}-%{version}.tar.gz
URL:           http://www.fractalio.com/
BuildRoot:     %{_tmppath}/%{name}-%{version}-root
BuildArch:     $arch

%description
This package installs the IntegralView - a management Graphical User Interface (GUI) for the IntegralSTOR and complete software.
IntegralStor is a high-performance, feature-rich & affordable unified storage platform for a wide range of business applications.
With block & file access in a single appliance, as well as support for a wide range of services and protocols, IntegralStor is a versatile general purpose data storage platform.
Whether as central storage for file sharing, off-site replication, business continuity, backup repository for mission-critical VMs, shared storage for video editing or central storage for video surveillance, IntegralStor is a reliable, fast, and easy-to-manage unified storage solution. 

%prep
%setup -q

%build
#Empty section.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%preun

%files
%defattr(-,root,root,-)
/opt/integralstor
/etc/nginx/sites-enabled
/etc/uwsgi/vassals
/var/
/run/samba/

%post -p /bin/bash 

echo ">>> Inside post <<<"
   
sleep 2
#chown root /opt/integralstor/integralstor_rpm_post.sh
#chmod 700 /opt/integralstor/integralstor_rpm_post.sh
#chmod +x /opt/integralstor/integralstor_rpm_post.sh

sh /opt/integralstor/integralstor/install/rpm/integralstor_rpm_post.sh >/tmp/rpm_post_script_log
#sh /opt/integralstor/integralstor_rpm_post.sh >/tmp/rpm_post_script_log
if [ $? -ne 0 ]; then
echo "CRITICAL: Running post install script Failed!"
exit 1
fi 
sleep 2

%changelog

* Fri Jun 09 2017 Naveenkumar<naveen@fractalio.com> 1.4.0
- Rewritten all for integralstor directory changes and for dependencies update.
* Wed Feb 15 2017 Naveenkumar<naveen@fractalio.com> 1.0-1
- Rewritten all for Centos 7.2 and for hosting repository.
- First Build - Centos 7.2
* Thu Sep 29 2016 Naveenkumar<naveen@fractalio.com> 1.0
- Created neccessary directories and linked files for respective directories as per the ks file
- First Build

EOF

### To create a rpm
rpmbuild -ba $working_dir/rpmbuild/SPECS/integralstor.spec

if [ $? -ne 0 ]; then
  echo "CRITICAL: RPM creation Failed!!!"
  exit 1
else
  echo "Successfully created IntegralSTOR RPM!"
  echo "Location:'$working_dir/rpmbuild/RPMS/$arch/'"
  ls $working_dir/rpmbuild/RPMS/$arch

### post rpm creation operation ###
# copying to all dependencies directory
  yes | cp -rf $working_dir/rpmbuild/RPMS/$arch/integralstor-${version_number}-${release_number}.$arch.rpm $working_dir/integralstor_rpms

### taking rpm backup ###
  cd $working_dir/
  mkdir -p $working_dir/integralstor_rpm_files/${version_number}-${release_number}
  yes | cp -rf $working_dir/rpmbuild/RPMS/$arch/integralstor-${version_number}-${release_number}.$arch.rpm $working_dir/integralstor_rpm_files/${version_number}-${release_number}		
  yes | cp -rf $working_dir/rpmbuild/SRPMS/integralstor-${version_number}-${release_number}.src.rpm $working_dir/integralstor_rpm_files/${version_number}-${release_number}

### extra ###
  tar -czf integralstor_tar_installs.tar.gz integralstor_tar_installs
  #cp $working_dir/initial_setup.sh $working_dir/integralstor_rpms
  tar -czf integralstor_rpms.tar.gz integralstor_rpms/
fi 
