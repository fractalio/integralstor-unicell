#!/bin/bash

ISTOR_ROOT="/opt/integralstor/integralstor"
APP_DIR="$ISTOR_ROOT/integral_view/applications"
SITE_DIR="$ISTOR_ROOT/site-packages/integralstor/applications"

if [[ ! -e "$ISTOR_ROOT/config/conf_files/applications.json" ]];then                        
        cp $ISTOR_ROOT/install/conf-files/others/applications.json $ISTOR_ROOT/config/conf_files/
else
        echo "$ISTOR_ROOT/config/conf_files/applications.json already exists not overwriting it.." 
fi      

if [[ -d "$APP_DIR/storage_insights/site-packages/storage_insights" ]];then
        ln -s $APP_DIR/storage_insights/site-packages/storage_insights $SITE_DIR/storage_insights
else
        echo "$APP_DIR/storage_insights/site-packages/storage_insights does not exist"
        exit 1
fi

if [[ ! -e "$APP_DIR/storage_insights/db/storage_insights.db" ]];then
        sqlite3 $APP_DIR/storage_insights/db/storage_insights.db < $APP_DIR/storage_insights/db/storage_insights.schema
        echo "Created storage_insights.db"
else
        echo "$APP_DIR/storage_insights/db/storage_insights.db already exists!"
        read -p "Do you want to remove it and create a new storage_insights.db file?(y/n) " input
        if [[ $input == 'y' ]] || [[ $input == 'Y' ]];then
                mv $APP_DIR/storage_insights/db/storage_insights.db $APP_DIR/storage_insights/db/storage_insights.db.`date +%d%m%y%H%M`
                echo "Backed up current storage_insights.db as storage_insights.db.`date +%d%m%y%H%M`"
                sqlite3 $APP_DIR/storage_insights/db/storage_insights.db < $APP_DIR/storage_insights/db/storage_insights.schema
                echo "Created new storage_insights.db"
        else
                exit 1
        fi
fi
