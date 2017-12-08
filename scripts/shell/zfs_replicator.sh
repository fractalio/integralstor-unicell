#!/bin/bash
# set -o xtrace

source_pool=$1
source_dataset=$2
destination=$3
user=$4
ip=$5
rr_id=$6
exit_code=-1

# get the process group id of this process
pgid=$(ps -o pgid= $$ | grep -o [0-9]*)

# get the process id
pid=$(ps -o pid= $$ | grep -o [0-9]*)

# store the process group id
printf '%s' "$pgid" > /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pgid

# store the process id
printf '%s' "$pid" > /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pid

source=$source_pool/$source_dataset
#echo $source $destination

# The first and the last snapshot on the source server
# Sort by creation date so that you always get the latest snapshot by date and not name
primary_initial=""
primary_initial_shapshot=""
primary_last=""
primary_last_snapshot=""
secondary_last=""
secondary_last_snapshot=""

get_primary_snapshot () {
  primary_last=$(sudo zfs list -t snapshot -o name -s creation | grep $source | grep zrr_ | tail -1)
  primary_initial=$(sudo zfs list -t snapshot -o name -s creation | grep $source | grep zrr_ | head -1)

  #Get the snapshot names. The Hack. Needs a better code.
  IFS=’@’ read -a primary_initial_snapshot <<< "${primary_initial}"
  echo "Earliest source snapshot : $source@${primary_initial_snapshot[1]}"
  IFS=’@’ read -a primary_last_snapshot <<< "${primary_last}"
  echo "Latest source remote replication snapshot: $source@${primary_last_snapshot[1]}"
} 
get_secondary_snapshot () {

  #Last successful snapshot from destination server
  # Sort by creation date so that you always get the latest snapshot by date and not name
  secondary_last=$(ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs list -t snapshot -o name -s creation | grep $destination/$source_dataset | grep zrr_ | tail -1")
  IFS=’@’ read -a secondary_last_snapshot <<< "${secondary_last}"
  if [[ -z "${secondary_last_snapshot[1]}" ]]; then
    echo "No remote replication snapshots found on the destination."
  else
    echo "Latest destination remote replication snapshot: $source@${secondary_last_snapshot[1]}"
  fi
}

get_primary_snapshot
get_secondary_snapshot

if [[ -z "${secondary_last_snapshot[1]}" ]]; then
  # Sync the initial snapshot
  echo "No remote replication snapshots on the destination so performing a complete send of the earliest source snapshot $source@${primary_initial_snapshot[1]}"
  sudo zfs send -v $source@${primary_initial_snapshot[1]} | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs receive -Fdv $destination"
  #sudo zfs send -v $source@${primary_initial_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination"
  rc=$?
  echo "Return code from the initial send command : $rc"
  exit_code=$rc
else
  #Secondary snapshot is not none
  if [ "${secondary_last_snapshot[1]}" != "${primary_last_snapshot[1]}" ]; then
    echo "The destination has some remote replication snapshots already so performing a differential send from $source@${secondary_last_snapshot[1]} to $source@${primary_last_snapshot[1]}"
    #If the destination and the source last snapshots are the not the same, then incremental sync of snapshots
    #echo "${secondary_last_snapshot} ${primary_last_snapshot}"
    sudo zfs send -vI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} | mbuffer -s 128k -m 512M 2>/dev/null|  gzip | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "gunzip | mbuffer -s 128k -m 512M | sudo zfs receive -Fdv $destination"
    #sudo zfs send -vI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} |  ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs receive -Fdv $destination"
    #sudo zfs send -vI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination"
    rc=$?
    echo "Return code from the differential send command : $rc"
    exit_code=$rc
  else
    echo "The source and destination snapshots are in sync. No replication required"
    exit_code=0
  fi
fi

# remove the process group id and pid files
rm -f /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pgid
rm -f /opt/integralstor/integralstor/config/run/tasks/rr."$rr_id".pid

exit $exit_code
