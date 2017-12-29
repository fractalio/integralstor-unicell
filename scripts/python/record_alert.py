from integralstor import alerts
import sys

''' Used to record an alert from a shell script '''

def main():
    if len(sys.argv) != 5:
        print 'Usage : python record_alert.py subsystem_type_id severity_type_id component_name alert_string'
        sys.exit(0)
    try:
        subsys_id = int(sys.argv[1])
        sev_id = int(sys.argv[2])
    except Exception, e:
        print 'Error reading the subsystem type or severity type : %s'%str(e)
        sys.exit(-1)
    retval, err = alerts.record_alerts([{'subsystem_type_id': subsys_id, 'severity_type_id': sev_id,
                        'component': sys.argv[3], 'alert_str': sys.argv[4]}])
    if err:
        print err
        sys.exit(-1)
    sys.exit(0)

if __name__ == '__main__':
    main()

