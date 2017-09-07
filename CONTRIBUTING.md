
## Welcome!

IntegralSTOR has been initiated to provide an rock solid, easy to use, high performance and extendable storage system for anyone to use. This takes a lot of doing and we are just starting off so there are many possibilities to chip in! 



## How can I help?

So whether you are a potential storage system user, an experienced hacker or someone new to open source contribution, there are many areas in which you can help. Some of the areas where you can contribute are listed below:

* Make it more open - We would like it to be as inclusive and open a development environment as possible. If you feel there is something wrong or if you can help set the bar higher, it would he highly appreciated.  

* Find problems - If you have used IntegralSTOR, please file an issue that you have found to help make it more solid.

* Domain expertise - If you are experienced with any of the underlying components or protocols then you can dive in to that particular component to make sure  it is being used most effectively. Some of the components/protocols include ZFS on Linux, Samba, NTP, rsync, CIFS, NFS, iSCSI, tgtd, LIO(upcoming), authentication and authorization systems like Active Directory/LDAP/NIS/Kerberos, SSH, vsFTP, nginx, uwsgi, Django, etc.

* Distro specific expertise - Packaging (deb/rpm/kickstart, etc.) and testing against various Linux distributions would be very welcome.

* Technical documentation - Any system is only as good as its documentation and ease of understanding. Admin manuals, architecture documentation, etc. will need constant updating and review.

* General Python skills - Much of the admin interface has been developed using Python/Django. 

* I18N - Unfortunately, IntegralSTOR is currently only in english. It would be great if you could help architect a way in which we can make it international.

* Web development - If you are a front end web developer, your skills in HTML5/ajax/bootstrap, etc. would be valuable.

* User experience design - Is IntegralSTOR really as intuitive as it can be? Help answer this question.

## Code of conduct
Please respect other contributors and first read the [Code of conduct](CODE_OF_CONDUCT.md) before starting.

Please go through this document to understand what IntegralSTOR does and how it is built

## How do I get the source code?
If you would like to start exploring the code, then [fork IntegralSTOR](https://help.github.com/articles/fork-a-repo) onto your computer. The main IntegralSTOR repository is located [here](https://github.com/integralstor/integralstor). 

## How is the code origanized?
The IntegralSTOR repository is structured as:

* integral_view - The django app for IntegralView - the admin interface
* integralview/forms - Django forms
* integral_view/views - Django views
* integral_view/templates - Django templates
* integral_view/static - javascript, html, image files.
* integral_view/urls.py - Django url definitions
* integral_view/settings.py - Django settings file
* integral_view/context_processors.py - Django context processors
* integral_view/integral_view_uwsgi.ini - uwsgi settings file
* integral_view/integral_view_nginx.conf - nginx settings file
* config/ - The directory that will contain all the IntegralSTOR configuration, status and log files
* scripts/python/ - All python scripts that are typically run from the cron
* scripts/shell/ - All shell scripts that are typically run from the cron
* site-packages/ - IntegralSTOR specific utility functions


## Installing IntegralSTOR
Currently IntegralSTOR has been tested only on CentOS 6 and 7. There are two ways to install it:
1. Download the ISO file, burn it onto a DVD and install from it. This will install the base OS as well.
2. Install CentOS 6 or 7, install ZFS on Linux (this is a more involved process as it requires you to have the kernel headers packages that match the underlying kernel version) and then download the IntegralSTOR rpm file and install it.

Detailed installation instructions for both methods are found [here(to be updated)](..)

## Development environment
As IntegralSTOR works only on CentOS 6/7, you will need a machine running either of these distros in order to test any changes that you make. Python 2.7 and Django 1.8.16 are currently used for IntegralView (the admin interface).

## Python coding standards

Please follow the [PEP-8 Python style guide](https://www.python.org/dev/peps/pep-0008/) for all python code.
