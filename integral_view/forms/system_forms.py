from django import forms
import common_forms
import pytz
import datetime
from integralstor import networking


class DateTimeForm(forms.Form):
    system_time = forms.CharField(required=False)
    system_date = forms.CharField(required=False)
    system_timezone = forms.ChoiceField(choices=[(item, item + ' ' + datetime.datetime.now(
        pytz.timezone(item)).strftime('%Z (GMT%z)')) for item in pytz.common_timezones], required=False)

    def clean(self):
        cd = super(DateTimeForm, self).clean()
        if ('system_time' not in cd or cd['system_time'] == '') and ('system_date' not in cd or cd['system_date'] == '') and ('system_timezone' not in cd or cd['system_timezone'] == ''):
            raise forms.ValidationError(
                "Atleast date, time or timezone should be present")
        else:
            if 'system_date' in cd:
                if cd['system_date'] == '':
                    cd['system_date'] = None
            if 'system_time' in cd:
                if cd['system_time'] == '':
                    cd['system_time'] = None
            if 'system_timezone' in cd:
                if cd['system_timezone'] == '':
                    cd['system_timezone'] = None
            return cd


class RemoteMonitoringServerForm(forms.Form):

    ip = forms.GenericIPAddressField(protocol='IPv4')
    name = forms.CharField()


class OrgInfoForm(forms.Form):
    org_name = forms.CharField(required=False)
    unit_name = forms.CharField(required=False)
    unit_id = forms.CharField(required=False)
    subunit_name = forms.CharField(required=False)
    subunit_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        initial = None
        if kwargs:
            if 'initial' in kwargs:
                initial = kwargs.pop('initial')
        super(OrgInfoForm, self).__init__(*args, **kwargs)
        if initial:
            if initial['org_name']:
                self.fields['org_name'] = forms.CharField(
                    required=False, initial=str(initial['org_name']))
            if initial['unit_name']:
                self.fields['unit_name'] = forms.CharField(
                    required=False, initial=str(initial['unit_name']))
            if initial['unit_id']:
                self.fields['unit_id'] = forms.CharField(
                    required=False, initial=str(initial['unit_id']))
            if initial['subunit_name']:
                self.fields['subunit_name'] = forms.CharField(
                    required=False, initial=str(initial['subunit_name']))
            if initial['subunit_id']:
                self.fields['subunit_id'] = forms.CharField(
                    required=False, initial=str(initial['subunit_id']))

    def clean(self):
        cd = super(OrgInfoForm, self).clean()
        org_name = str(cd.get('org_name')).strip()
        unit_name = str(cd.get('unit_name')).strip()
        unit_id = str(cd.get('unit_id')).strip()
        subunit_name = str(cd.get('subunit_name')).strip()
        subunit_id = str(cd.get('subunit_id')).strip()
        # Though the fields are not mandatory, accept only if atleast one field
        # has a character value
        if (org_name == '') and (unit_name == '') and (unit_id == '') and (subunit_name == '') and (subunit_id == ''):
            raise forms.ValidationError(
                'Please provide a value for atleast one of the fields')
        return self.cleaned_data


class FactoryDefaultsForm(forms.Form):
    delete_cifs_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_nfs_exports = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_rsync_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_iscsi_targets = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)

    delete_org_info = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class others'}), required=False)

    delete_local_users = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class users_groups_class'}), required=False)
    delete_local_groups = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class users_groups_class'}), required=False)

    delete_dns_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_interface_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_bonds = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    delete_network_vlans = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    reset_hostname = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)
    default_ip = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class networking_class'}), required=False)

    delete_ssl_certificates = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)
    delete_ssh_authorized_keys = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)
    delete_ssh_fingerprints = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class ssl_ssh_class'}), required=False)

    delete_audits = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)
    delete_alerts = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)
    delete_logs = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class logs_class'}), required=False)

    delete_remote_replications = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class replication_tasks_class'}), required=False)
    delete_tasks_and_logs = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class replication_tasks_class'}), required=False)

    reset_cifs_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    reset_ntp_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    reset_ftp_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)
    delete_email_settings = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class services_class'}), required=False)

    delete_zfs_pools = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'data_class zfs_class'}), required=False)
    delete_zfs_datasets_and_snapshots = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'data_class zfs_class'}), required=False)
    delete_zfs_zvols_and_snapshots = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'data_class zfs_class'}), required=False)

    def clean_default_ip(self):
        is_default_ip = self.cleaned_data['default_ip']
        is_delete_nic = self.cleaned_data['delete_network_interface_settings']
        is_delete_bonds = self.cleaned_data['delete_network_bonds']
        if is_default_ip is True:
            if (is_delete_nic and is_delete_bonds) is not True:
                self._errors['delete_network_interface_settings'] = self.error_class(
                    ["This should be selected if default IP must be set on reboot"])
                self._errors['delete_network_bonds'] = self.error_class(
                    ["This should be selected if default IP must be set on reboot"])
        return is_default_ip

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
