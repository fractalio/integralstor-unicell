#set -o xtrace
source_pool=$1
source_dataset=$2
destination=$3
user=$4
ip=$5
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

primary_snapshot () {
  primary_last=$(sudo zfs list -t snapshot -o name -s creation | grep $source | tail -1)
  primary_initial=$(sudo zfs list -t snapshot -o name -s creation | grep $source | head -1)

  #Get the snapshot names. The Hack. Needs a better code.
  IFS=’@’ read -a primary_initial_snapshot <<< "${primary_initial}"
  echo "Earliest source snapshot : $source@${primary_initial_snapshot[1]}"
  IFS=’@’ read -a primary_last_snapshot <<< "${primary_last}"
  echo "Latest source snapshot: $source@${primary_last_snapshot[1]}"
} 
secondary_snapshot () {

  #Last successful snapshot from destination server
  # Sort by creation date so that you always get the latest snapshot by date and not name
  secondary_last=$(ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs list -t snapshot -o name -s creation | grep $destination/$source_dataset | tail -1")
  IFS=’@’ read -a secondary_last_snapshot <<< "${secondary_last}"
  if [[ -z "${secondary_last_snapshot[1]}" ]]; then
    echo "No snapshots found on the destination."
  else
    echo "Latest destination snapshot: $source@${secondary_last_snapshot[1]}"
  fi
}

primary_snapshot
secondary_snapshot

if [[ -z "${secondary_last_snapshot[1]}" ]]; then
  # Sync the initial snapshot
  echo "No snapshots on the destination so performing a complete send of the earliest source snapshot $source@${primary_initial_snapshot[1]}"
  sudo zfs send -v $source@${primary_initial_snapshot[1]} | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs receive -Fdv $destination"
  #sudo zfs send -v $source@${primary_initial_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination"
  rc=$?
  echo "Return code from the initial send command : $rc"
  exit $rc
else
  #Secondary snapshot is not none
  if [ "${secondary_last_snapshot[1]}" != "${primary_last_snapshot[1]}" ]; then
    echo "The destination has some snapshots already so performing a differential send from $source@${secondary_last_snapshot[1]} to $source@${primary_last_snapshot[1]}"
    #If the destination and the source last snapshots are the not the same, then incremental sync of snapshots
    #echo "${secondary_last_snapshot} ${primary_last_snapshot}"
    sudo zfs send -vI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} |  ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "sudo zfs receive -Fdv $destination"
    #sudo zfs send -vI $source@${secondary_last_snapshot[1]} $source@${primary_last_snapshot[1]} | mbuffer -s 128k -m 1G 2>/dev/null | ssh -o ServerAliveInterval=300 -o ServerAliveCountMax=3 $user@$ip "mbuffer -s 128k -m 1G | sudo zfs receive -Fdv $destination"
    rc=$?
    echo "Return code from the differential send command : $rc"
    exit $rc
  else
    echo "The source and destination snapshots are in sync. No replication required"
    exit 0
  fi
fi
