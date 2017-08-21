# set -o xtrace
rsync_cmd=$1
rename_snap=$2
create_snap=$3
# echo $rsync_cmd
exit_code=""

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

exit $exit_code

