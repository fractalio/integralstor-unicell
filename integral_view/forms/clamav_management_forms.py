from django import forms
from integralstor_common import clamav
from os import listdir


class Config(forms.Form):
    dct,err = clamav.get_clamav_conf_file('clamd')
    MaxFiles = forms.CharField(label='MaxFiles', max_length=100, initial = dct['MaxFiles'], help_text='<p><font size=2>Number of files to be scanned within an archive, a document, or any other container file.</font></p><br><br>')
    MaxScanSize = forms.CharField(label='MaxScanSize', max_length=100, initial = dct['MaxScanSize'], help_text='<p><font size=2>This option sets the maximum amount of data to be scanned for each input file. Archives and other containers are recursively extracted and scanned up to this value.</font></p><br><br>')
    MaxFileSize = forms.CharField(label='MaxFileSize', max_length=100, initial = dct['MaxFileSize'], help_text="<p><font size=2>Files larger than this limit won't be scanned. Affects the input file itself as well as files contained inside it (when the input file is an archive, a document or some other kind of container).</font></p><br><br>")
    dct_updater,err = clamav.get_clamav_conf_file('freshclam')
    Checks = forms.CharField(label='Checks', max_length=100, initial = dct_updater['Checks'], help_text='<p><font size=2>Number of files to be scanned within an archive, a document, or any other container file.</font></p><br><br>')
    #upload_file = forms.FileField()


class QuarantineList(forms.Form):
    def __init__(self,  *args, **kwargs):
        super(QuarantineList, self).__init__(*args, **kwargs)
        virus_list = listdir('/opt/integralstor/integralstor_unicell/config/clamav/quarantine/')
        if virus_list == []:
            virus_list = 'Empty'
        else :
            for virus_file in virus_list:
                self.fields[virus_file] = forms.BooleanField(required=False)

