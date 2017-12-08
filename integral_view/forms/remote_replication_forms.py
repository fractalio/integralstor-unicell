from django import forms


class ZFSMode(forms.Form):
    target_pool = forms.CharField()

    def clean_target_pool(self):
        target_pool = self.cleaned_data['target_pool']
        if target_pool and (target_pool.find('\'') >= 0 or target_pool.find('\"') >= 0):
            self._errors["target_pool"] = self.error_class(
                ["Pool name cannot contain single or double quotes."])

        if target_pool and target_pool.isdigit():
            self._errors["target_pool"] = self.error_class(
                ["Pool name cannot start with a number."])

        return target_pool


class RsyncMode(forms.Form):
    local_path = forms.CharField()
    remote_path = forms.CharField()
    rsync_type = forms.ChoiceField(choices=[('push', 'local host to remote host(push)'), (
        'pull', 'remote host to local host(pull)'), ('local', 'within the local host')])
    is_between_integralstor = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'checked': 'checked'}), required=False)
    # is_between_integralstor = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        switches = None
        initial = None
        switch_ch = []
        if kwargs:
            if 'switches' in kwargs:
                switches = kwargs.pop('switches')
            if 'initial' in kwargs:
                initial = kwargs.pop('initial')
        super(RsyncMode, self).__init__(*args, **kwargs)
        if switches:
            for switch, val in switches.items():
                switch_ch.append(
                    ({switch: switches[switch]}, val['description']))
                if val['is_arg'] == True:
                    self.fields['%s_arg' %
                                val['id']] = forms.CharField(required=False)

        self.fields['switches'] = forms.MultipleChoiceField(
            widget=forms.widgets.CheckboxSelectMultiple,
            choices=switch_ch,
            required=False)


class CreateRemoteReplication(ZFSMode, RsyncMode):
    target_ip = forms.GenericIPAddressField(protocol='IPv4')
    is_one_shot = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        modes = []
        select_mode = None
        datasets = None
        initial = None
        if kwargs:
            if 'modes' in kwargs:
                modes = kwargs.pop('modes')
            if 'select_mode' in kwargs:
                select_mode = str(kwargs.pop('select_mode'))
            if 'datasets' in kwargs:
                datasets = kwargs.pop('datasets')
            if 'initial' in kwargs:
                initial = kwargs.pop('initial')
        super(CreateRemoteReplication, self).__init__(*args, **kwargs)
        ch = []
        if modes:
            for mode in modes:
                tup = (mode, mode)
                ch.append(tup)
        else:
            ch.append((None, 'None'))
        self.fields['modes'] = forms.ChoiceField(choices=ch)

        if select_mode:
            self.fields['select_mode'] = forms.CharField(
                initial=str(select_mode))

        if select_mode and select_mode == 'zfs':
            self.fields['local_path'] = forms.CharField(required=False)
            self.fields['remote_path'] = forms.CharField(required=False)
            self.fields['rsync_type'] = forms.ChoiceField(required=False)
            self.fields['switches'] = forms.MultipleChoiceField(required=False)

        src_ds_ch = []
        if datasets:
            for dataset in datasets:
                tup = (dataset, dataset)
                src_ds_ch.append(tup)
        else:
            src_ds_ch.append((None, 'None'))
        self.fields['source_dataset'] = forms.ChoiceField(choices=src_ds_ch)

        if select_mode and select_mode == 'rsync':
            self.fields['target_pool'] = forms.CharField(
                required=False, initial=None)
            if datasets:
                self.fields['local_path'] = forms.CharField(
                    initial='/%s' % datasets[0])
            else:
                self.fields['local_path'] = forms.CharField(
                    initial='')

    def clean_target_ip(self):
        target_ip = str(self.cleaned_data['target_ip'])
        rsync_type = str(self.cleaned_data['rsync_type'])
        # if target_ip and rsync_type:
        # if target_ip == '0.0.0.0':
        if target_ip == '0.0.0.0' and rsync_type != 'local':
            self._errors["target_ip"] = self.error_class(
                ["Please provide a valid IP"])

        return target_ip
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
