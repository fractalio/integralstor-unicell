from django import forms


class RenameVolumeForm(forms.Form):

    current_name = forms.CharField(widget=forms.HiddenInput)
    path = forms.CharField(widget=forms.HiddenInput)
    new_name = forms.CharField()

class CreateVolumeForm(forms.Form):

    name = forms.CharField()
    path = forms.CharField()
    dataset = forms.CharField(required=True)
    new_folder = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(CreateVolumeForm, self).__init__(*args, **kwargs)

        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = (ds['mountpoint'], ds['name'])
                ch.append(tup)
        self.fields["dataset"] = forms.ChoiceField(choices=ch)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
