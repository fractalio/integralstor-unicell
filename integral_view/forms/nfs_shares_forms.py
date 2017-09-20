from django import forms


class ShareForm(forms.Form):

    path = forms.CharField()
    clients = forms.CharField()
    readonly = forms.BooleanField(required=False)
    root_squash = forms.BooleanField(required=False)
    all_squash = forms.BooleanField(required=False)
    force_map_anonid = forms.BooleanField(required=False)

    def clean(self):
        cd = super(ShareForm, self).clean()
        if len(cd['path'].split()) > 1:
            self._errors["path"] = self.error_class(
                ["The export path cannot contain whitespaces"])
        return cd


class CreateShareForm(ShareForm):

    dataset = forms.CharField(required=True)
    new_folder = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(CreateShareForm, self).__init__(*args, **kwargs)

        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = (ds['mountpoint'], ds['name'])
                ch.append(tup)
        self.fields["dataset"] = forms.ChoiceField(choices=ch)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
