
from django import forms

from integralstor import networking


class MultipleServerField(forms.CharField):

    def _is_valid_server(self, server):
        server = server.strip()
        ok, err = networking.validate_ip_or_hostname(server)
        if err:
            raise Exception('Error validating server : %s' % err)
        return ok

    def clean(self, value):
        super(MultipleServerField, self).validate(value)
        '''
        if not value:
            raise forms.ValidationError(
                "Enter atleast one IP address or hostname")
        '''
        if not value:
            return None
        if ',' in value:
            servers = value.lower().split(',')
        else:
            servers = value.lower().split(' ')
        for server in servers:
            if not self._is_valid_server(server):
                raise forms.ValidationError(
                    "%s is not a valid address" % server)

        return value.lower()


class ConfigureNTPForm(forms.Form):

    server_list = MultipleServerField()


class AddNodesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if kwargs:
            pml = kwargs.pop('pending_minions_list')
        super(AddNodesForm, self).__init__(*args, **kwargs)
        ch = []
        for minion in pml:
            tup = (minion, minion)
            ch.append(tup)
        self.fields["nodes"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=ch)


class FileUploadForm(forms.Form):
    file_field = forms.FileField()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
