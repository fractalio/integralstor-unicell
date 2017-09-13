#!/bin/bash

hardware_vendor=""
[ -n "$1" ] && hardware_vendor=$1

echo "/opt/integralstor/integralstor/install/scripts/configure_os.sh $hardware_vendor" | /bin/bash
echo "/opt/integralstor/integralstor/install/scripts/configure_services.sh" | /bin/bash
