from integralstor import command, alerts
import re, sys

def get_enclosure_devices():
    # Returns a list of /dev/sgX path for Connected Storage Enclosures
    enclosures = []
    try:
        sg_devs, err = command.get_command_output('sg_map -i')
        if err:
            raise Exception(err)

        if sg_devs:
            for sg_dev in sg_devs:
                    encl = re.findall('ENCL', sg_dev, re.IGNORECASE)
                    if encl:
                        res = re.findall(r'^\/\w+\/\w+', sg_dev)
                        enclosures += res
    except Exception, e:
        return None, "Error retrieving enclosures : %s" % str(e)
    else:
        return enclosures, None

def get_psu_status():
    psu_status = {}
    try:
        encls, err = get_enclosure_devices()
        if err:
            raise Exception(err)

        if encls:
            for encl in encls:
                for psu in range(2):
                    tmp, err = command.get_command_output('sg_ses --index=ps,%d %s' % (psu, encl))
                    if err:
                        raise Exception(err)
                    if tmp:
                        for status in tmp:
                            result = re.findall(r'status: \w+', status)
                            if result:
                                psu_status['PSU-%d' % psu] = result[0]
    except Exception, e:
        return None, "Error retrieving JBOD PSU status : %s" % str(e)
    else:
        return psu_status, None

def main():
    try:
        psu_status, err = get_psu_status()
        if err:
            raise Exception(err)

        if psu_status:
            if 'status: Critical' in psu_status.values():
                alert_list = []
                for psu in psu_status:
                    if psu_status[psu] == 'status: Critical':
                        faulty_psu = psu
                encls, err = get_enclosure_devices()
                if err:
                    raise Exception(err)
                for encl in encls:
                    tmp, err = command.get_command_output('sginfo %s' % encl)
                    if err:
                        raise Exception(err)
                    for strg in tmp:
                        v = re.findall(r'(^Vendor: *)(\w+)', strg)
                        if v:
                            vendor = v[0][1]
                        p = re.findall(r'(^Product: *)(\w+)', strg)
                        if p:
                            product = p[0][1]
                alert_str = '%s has gone down on %s %s' % (faulty_psu, vendor, product)
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
