from django import forms
import logging
from integralstor_utils import config


class DownloadLogsForm(forms.Form):
    """ Form to get the info about which log to download"""

    #ch = [('boot', 'Boot log'), ('dmesg', 'Dmesg log'), ('message', 'Message log'), ('smb', 'Samba logs'),
    #      ('winbind', 'Samba Winbind logs'), ('alerts', 'Alerts log'), ('audit', 'Audit log')]
    ch = [('system', 'System logs'), ('alerts', 'Alerts log'), ('audit', 'Audit log')]
    hw_platform, err = config.get_hardware_platform()
    if hw_platform and hw_platform == 'dell':
        ch.append(('hardware', 'Hardware log'))
    log_type = forms.ChoiceField(choices=ch)


class ViewLogsForm(forms.Form):
    """ Form to get the info about which log to view"""

    ch = [('alerts', 'Alerts log'), ('audit', 'Audit log')]
    hw_platform, err = config.get_hardware_platform()
    if hw_platform and hw_platform == 'dell':
        ch.append(('hardware', 'Hardware log'))
    log_type = forms.ChoiceField(choices=ch)


class IntegralViewLoggingForm(forms.Form):

    ch = [(logging.DEBUG, 'Debug'), (logging.INFO,
                                     'Information'), (logging.WARNING, 'Errors')]
    log_level = forms.ChoiceField(choices=ch)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
