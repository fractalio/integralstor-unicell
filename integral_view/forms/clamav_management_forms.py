from django import forms
from integralstor_common import clamav
from os import listdir


class ClamavConfiguration(forms.Form):
    dct,err = clamav.get_clamav_conf('clamd')
    max_files = forms.CharField(label='MaxFiles', max_length=100, initial = dct['MaxFiles'])
    max_scan_size = forms.CharField(label='MaxScanSize', max_length=100, initial = dct['MaxScanSize'])
    max_file_size = forms.CharField(label='MaxFileSize', max_length=100, initial = dct['MaxFileSize'])
    dct_updater,err = clamav.get_clamav_conf('freshclam')
    checks = forms.CharField(label='Checks', max_length=100, initial = dct_updater['Checks'])

class QuarantineList(forms.Form):
    def __init__(self,  *args, **kwargs):
        super(QuarantineList, self).__init__(*args, **kwargs)
        virus_list,err = clamav.get_quarantine_list()
        if virus_list == []:
            virus_list = 'Empty'
        else :
            for virus_file in virus_list:
                self.fields[virus_file] = forms.BooleanField(required=False)

