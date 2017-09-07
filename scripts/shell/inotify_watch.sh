#!/bin/bash
inotifywait --fromfile /opt/integralstor/integralstor/config/inotify_watch_dirs -c -r -e access,modify,create,delete,move -m |while read output_str; do
        #ts=$(date -u +"%C%y-%m-%d %H:%M:%S")
	/usr/bin/python /opt/integralstor/integralstor/site-packages/integralstor_utils/inotify.py $output_str
done
exit 0
