from integralstor import command, alerts, disk_enclosures
import re, sys

def main():
    try:
        vendor_info = 'N.A'
        product_info = 'N.A'
        alert_list = []
        psu_status, err = disk_enclosures.get_psu_status()
        if err:
            raise Exception(err)

        if psu_status:
            for psu_num, status_line in enumerate(psu_status):
                if 'status: Critical' in status_line:
                    faulty_psu = psu_num
            encls, err = disk_enclosures.get_enclosure_devices()
            if err:
                raise Exception(err)
            for encl in encls:
                tmp_cmd_output, err = command.get_command_output('sginfo %s' % encl)
                if err:
                    raise Exception(err)
                for line in tmp_cmd_output:
                    vendor = re.findall(r'(^Vendor: *)(\w+)', line)
                    if vendor:
                        vendor_info = vendor[0][1]
                    product = re.findall(r'(^Product: *)(\w+)', line)
                    if product:
                        product_info = product[0][1]
            alert_str = '%s has gone down on %s %s' % (faulty_psu, vendor_info, product_info)
            alert_list.append({'subsystem_type_id': 5, 'severity_type_id': 3,
                                'component': 'Power Supply', 'alert_str': alert_str})
            ret, err = alerts.record_alerts(alert_list)
            if err:
                raise Exception(err)
    except Exception, e:
        return None, "Error recording PSU alert : %s" % str(e)

if __name__ == "__main__":
    ret = main()
    print ret
    if ret is not None:
        sys.exit(1)
    else:
        sys.exit(0)

#vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
