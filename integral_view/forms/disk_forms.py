from django import forms


class FormatDiskForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput, required=False)
    disk_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        if kwargs and 'fs_types' in kwargs:
            fs_type_list = kwargs.pop('fs_types')
            super(FormatDiskForm, self).__init__(*args, **kwargs)
            self.fields['fs_type'] = forms.ChoiceField(choices=fs_type_list)
        else:
            super(FormatDiskForm, self).__init__(*args, **kwargs)
            self.fields['fs_type'] = forms.CharField(required=False)

    def clean(self):
        cd = super(FormatDiskForm, self).clean()
        if 'fs_type' in cd:
            if cd['fs_type'] == '':
                raise forms.ValidationError('could not find file system type')
        if 'path' in cd:
            if cd['path'] == '':
                raise forms.ValidationError('could not find disk path')
        if 'disk_id' in cd:
            if cd['disk_id'] == '':
                raise forms.VAlidationError('could not find disk_id')
        return cd


class MountUnmountDiskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choiced = []
        if kwargs and 'partitions' in kwargs:
            partitions_list = kwargs.pop('partitions')
            for i in partitions_list:
                d = '/dev/' + i['name']
                choiced.append(d)
            super(MountUnmountDiskForm, self).__init__(*args, **kwargs)
            self.fields['partitions'] = forms.ChoiceField(choices=choiced)
        else:
            super(MountUnmountDiskForm, self).__init__(*args, **kwargs)
            self.fields['partition'] = forms.CharField(required=False)

    def clean(self):
        cd = super(MountUnmountDiskForm, self).clean()
        if 'partition' in cd:
            if cd['partition'] == '':
                raise forms.ValidationError(
                    'could not get partition to be mounted')
        return cd
