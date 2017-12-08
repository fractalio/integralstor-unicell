#!/bin/bash
# set -o xtrace

rsync_cmd=$1
rename_snap=$2
create_snap=$3
rr_id=$4
exit_code=""
# echo $rsync_cmd

# get the process group id of this process
pgid=$(ps -o pgid= $$ | grep -o [0-9]*)

# get the process id
pid=$(ps -o pid= $$ | grep -o [0-9]*)

# store the process group id
printf '%s' "$pgid" > /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pgid

# store the process id
printf '%s' "$pid" > /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pid

echo "$rsync_cmd" | /bin/bash
rsync_rc=$?

echo "Return code from rsync: $rsync_rc"

if (( "$rsync_rc"=="23" || "$rsync_rc"=="24" || "$rsync_rc"=="25" )); then
  echo "Deliberately ignoring the error code $rsync_rc. Exiting with return code 0 instead."
  exit_code=0
else
  exit_code=$rsync_rc
fi

rename_snap_rc=''
create_snap_rc=''
if (( "$exit_code"=="0" )); then
  echo "Syncing snapshots between the source and target."
  echo "$rename_snap" | /bin/bash
  rename_snap_rc=$?
  echo "$create_snap" | /bin/bash
  create_snap_rc=$?

  if (( "$rename_snap_rc"=="0" && "$create_snap_rc"=="0" )); then
    echo "Synced snapshots"
  else
    echo "Could not sync snapshots"
  fi
fi

# remove the process group id and pid files
rm -f /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pgid
rm -f /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pid

exit $exit_code

