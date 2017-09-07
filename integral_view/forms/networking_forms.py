from django import forms

import common_forms
from integralstor import networking


class EditHostnameForm(forms.Form):
    hostname = forms.CharField()
    domain_name = forms.CharField(required=False)

    def clean(self):
        cd = super(EditHostnameForm, self).clean()
        hostname = cd.get("hostname")
        if hostname is not None:
            if hostname and '.' in hostname:
                self._errors["hostname"] = self.error_class(
                    ["Please enter a hostname without the domain name component (no '.'s allowed)"])
            valid, err = networking.validate_hostname(hostname)
            if err:
                self._errors["hostname"] = self.error_class(
                    ['%s. \tOnly alphabets, digits and hyphens permitted.' % err])
            elif not valid:
                self._errors["hostname"] = self.error_class(
                    ['Invalid hostname. Only alphabets, digits and hyphens permitted.'])
        return cd


class DNSNameServersForm(forms.Form):

    nameservers = common_forms.MultipleServerField()

    def clean(self):
        cd = super(DNSNameServersForm, self).clean()
        nameservers = cd.get("nameservers")
        if nameservers is not None:
            if nameservers and ',' in nameservers:
                slist = nameservers.split(',')
            else:
                slist = nameservers.split(' ')
            for server in slist:
                valid, err = networking.validate_ip(server)
                if err:
                    self._errors["nameservers"] = self.error_class(
                        ["Error validating DNS server IP address %s : %s" % (server, err)])
                    break
                elif not valid:
                    self._errors["nameservers"] = self.error_class(
                        ["Invalid DNS server IP address : %s" % server])
                    break
        return cd


class NICForm(forms.Form):

    name = forms.CharField(widget=forms.HiddenInput)
    ip = forms.GenericIPAddressField(protocol='IPv4', required=False)
    netmask = forms.GenericIPAddressField(protocol='IPv4', required=False)
    default_gateway = forms.GenericIPAddressField(
        protocol='IPv4', required=False)
    mtu = forms.IntegerField(initial=1500, max_value=9000)

    ch = [('static', r'Static'), ('dhcp', r'DHCP')]
    addr_type = forms.ChoiceField(choices=ch, widget=forms.RadioSelect())

    def clean(self):
        cd = super(NICForm, self).clean()
        addr_type = cd['addr_type']
        if addr_type == 'static':
            if 'ip' not in cd or not cd['ip']:
                self._errors["ip"] = self.error_class(
                    ["IP address is required for static addressing"])
            if 'netmask' not in cd or not cd['netmask']:
                self._errors["ip"] = self.error_class(
                    ["Netmask is required for static addressing"])
            netmask = cd['netmask']
            valid, err = networking.validate_netmask(netmask)
            if not valid:
                self._errors["netmask"] = self.error_class(["Invalid netmask"])
        return cd


class CreateVLANForm(forms.Form):

    vlan_id = forms.IntegerField()
    base_interface = forms.CharField(widget=forms.HiddenInput)
    existing_bonds = None

    def __init__(self, *args, **kwargs):
        dsll = None
        if kwargs:
            self.existing_vlans = kwargs.pop('existing_vlans')
        super(CreateVLANForm, self).__init__(*args, **kwargs)

    def clean(self):
        cd = super(CreateVLANForm, self).clean()
        vlan_id = cd['vlan_id']
        if vlan_id in self.existing_vlans:
            self._errors["name"] = self.error_class(
                ["A VLAN of that ID already exists. Please choose another VLAN ID."])
        return cd


class CreateBondForm(forms.Form):

    name = forms.CharField()
    ch = [('4', r'802.3ad'), ('6', r'balance-alb')]
    mode = forms.ChoiceField(widget=forms.Select, choices=ch)
    interfaces = None
    existing_bonds = None

    def __init__(self, *args, **kwargs):
        dsll = None
        if kwargs:
            self.interfaces = kwargs.pop('interfaces')
            self.existing_bonds = kwargs.pop('existing_bonds')
        super(CreateBondForm, self).__init__(*args, **kwargs)

        ch = []
        if self.interfaces:
            for iface in self.interfaces:
                tup = (iface, iface)
                ch.append(tup)
        self.fields["slaves"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(), choices=ch)

    def clean(self):
        cd = super(CreateBondForm, self).clean()
        #name = cd['name']
        name = cd.get("name")

        if name is not None:
            if name and name in self.existing_bonds:
                self._errors["name"] = self.error_class(
                    ["A Bond or interface of this name already exists. Please choose another name."])
            if not name.isalnum():
                self._errors["name"] = self.error_class(
                    ["The name cannot contain special characters."])
                del cd["name"]

            if 'name' in cd and name[0].isdigit():
                self._errors["name"] = self.error_class(
                    ["The name cannot start with a number."])
                del cd["name"]
        return cd


class CreateRouteForm(forms.Form):

    type = forms.ChoiceField(widget=forms.Select, choices=[
                             ('default', 'default')], required=False)
    ip = forms.GenericIPAddressField(protocol='IPv4', required=True)
    netmask = forms.GenericIPAddressField(protocol='IPv4', required=True)
    gateway = forms.GenericIPAddressField(protocol='IPv4', required=True)
    interface = None

    def __init__(self, *args, **kwargs):
        super(CreateRouteForm, self).__init__(*args, **kwargs)
        ch = []
        interfaces, err = networking.get_interfaces()
        for key, value in interfaces.iteritems():
            # print value['addresses']['AF_INET']
            # check if the interface has an ip address assigned to it ?
            if (value['up_status'] == 'up') and ('AF_INET' in value['addresses']):
                # Just make sure the ip addr is not the localhost address. Just
                # in case.
                if value['addresses']['AF_INET'][0]['addr'] != "127.0.0.1":
                    ch.append((key, key))
        self.fields["interface"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(), choices=ch)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
