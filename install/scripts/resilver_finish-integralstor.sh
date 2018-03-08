#!/bin/sh
#
# Send notification in response to a RESILVER_FINISH or SCRUB_FINISH.
#
# By default, "zpool status" output will only be included for a scrub_finish
# zevent if the pool is not healthy; to always include its output, set
# ZED_NOTIFY_VERBOSE=1.
#
# Exit codes:
#   0: notification sent
#   1: notification failed
#   2: notification not configured
#   3: notification suppressed
#   9: internal error

[ -f "${ZED_ZEDLET_DIR}/zed.rc" ] && . "${ZED_ZEDLET_DIR}/zed.rc"
. "${ZED_ZEDLET_DIR}/zed-functions.sh"

[ -n "${ZEVENT_POOL}" ] || exit 9
[ -n "${ZEVENT_SUBCLASS}" ] || exit 9

if   [ "${ZEVENT_SUBCLASS}" = "resilver_finish" ]; then
    action="data rebuild"
    audit_code="resilver_zfs_pool_completed"
else
    zed_log_err "unsupported event class \"${ZEVENT_SUBCLASS}\""
    exit 9
fi

audit_str="ZFS has completed a ${action} on pool ${ZEVENT_POOL} at ${ZEVENT_TIME_STRING}."

python /opt/integralstor/integralstor/scripts/python/record_audit.py ${audit_code} "${audit_str}"
