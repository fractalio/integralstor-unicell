#!/bin/bash

ISTOR_ROOT="/opt/integralstor/integralstor"

if [[ ! -e "$ISTOR_ROOT/config/conf_files/applications.json" ]];then                        
        cp $ISTOR_ROOT/install/conf-files/others/applications.json $ISTOR_ROOT/config/conf_files/
else
        echo "$ISTOR_ROOT/config/conf_files/applications.json already exists not overwriting it.." 
fi      
