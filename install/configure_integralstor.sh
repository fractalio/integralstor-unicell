#!/bin/bash

hardware_vendor=""
[ -n "$1" ] && hardware_vendor=$1

/bin/bash -c '/opt/integralstor/integralstor/install/scripts/configure_os.sh $hardware_vendor'
/bin/bash -c '/opt/integralstor/integralstor/install/scripts/configure_services.sh'
