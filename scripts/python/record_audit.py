from integralstor import audit
import sys

''' Used to record an audit from a shell script '''

def main():
    if len(sys.argv) != 3:
        print 'Usage : python record_audit.py audit_code audit_string'
        sys.exit(0)
    retval, err = audit.audit(sys.argv[1], sys.argv[2], None, system_initiated=True)
    if err:
        print err
        sys.exit(-1)
    sys.exit(0)

if __name__ == '__main__':
    main()

