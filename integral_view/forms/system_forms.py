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


class FactoryDefaultsForm(forms.Form):
    delete_cifs_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_nfs_exports = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_rsync_shares = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)
    delete_iscsi_targets = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'settings_class shares_class'}), required=False)

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

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
