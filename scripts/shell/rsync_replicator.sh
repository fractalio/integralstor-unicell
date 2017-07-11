# set -o xtrace
cmd=$1
# echo $cmd
exit_code=""

echo "$cmd" | /bin/bash
rsync_rc=$?

echo "Return code from rsync: $rsync_rc"

if (( "$rsync_rc"=="23" || "$rsync_rc"=="24" || "$rsync_rc"=="25" )); then
  echo "Deliberately ignoring the error code $rsync_rc. Exiting with return code 0 instead."
  exit_code=0
else
  exit_code=$rsync_rc
fi

exit $exit_code

