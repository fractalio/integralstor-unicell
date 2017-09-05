from django import forms


class CommonPropertiesForm(forms.Form):

    name = forms.CharField()
    readonly = forms.BooleanField(required=False)
    compression = forms.BooleanField(required=False)
    dedup = forms.BooleanField(required=False)

    def clean(self):
        cd = super(CommonPropertiesForm, self).clean()
        if not cd['name'].isalnum():
            self._errors["name"] = self.error_class(
                ["The name cannot contain special characters."])
            del cd["name"]

        if 'name' in cd and cd['name'][0].isdigit():
            self._errors["name"] = self.error_class(
                ["The name cannot start with a number."])
            del cd["name"]

        if 'name' in cd and cd['name'].lower() in ['none']:
            self._errors["name"] = self.error_class(
                ["'None' is a reserved word, please try some other name"])
            del cd["name"]

        return cd


class BaseDatasetForm(CommonPropertiesForm):

    quota_size = forms.IntegerField()
    ch = [('G', 'GB'), ('M', 'MB')]
    quota_unit = forms.ChoiceField(choices=ch)


class BaseZvolForm(CommonPropertiesForm):

    pass


class CreateDatasetForm(BaseDatasetForm):

    pool = forms.CharField()


class AdvancedDatasetZvolPropertiesForm(forms.Form):
    name = forms.CharField()
    property_value = forms.CharField()

    def __init__(self, *args, **kwargs):
        if kwargs and 'modifiable_properties' in kwargs:
            modifiable_properties = kwargs.pop('modifiable_properties')
        super(AdvancedDatasetZvolPropertiesForm,
              self).__init__(*args, **kwargs)
        ch = []
        for property_name, property in modifiable_properties.items():
            ch.append((property_name, '%s(%s) - currently %s' %
                       (property['short_desc'], property_name, property['value'])))
        self.fields['property_name'] = forms.ChoiceField(choices=ch)


class CreateZvolForm(BaseZvolForm):

    thin_provisioned = forms.BooleanField(required=False)
    pool = forms.CharField()
    size = forms.DecimalField(decimal_places=1)
    ch = [('8K', '8K'), ('16K', '16K'), ('32K', '32K'), ('64K', '64K')]
    block_size = forms.ChoiceField(choices=ch)
    ch = [('GB', 'G'), ('MB', 'M')]
    unit = forms.ChoiceField(choices=ch)


class SlogForm(forms.Form):
    ramdisk_size = forms.IntegerField(required=False)
    pool = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        free_disks = None
        if kwargs and 'free_disks' in kwargs:
            free_disks = kwargs.pop('free_disks')
        super(SlogForm, self).__init__(*args, **kwargs)
        if free_disks:
            ch = [('ramdisk', 'RAM disk'), ('flash', 'Flash drive')]
            ch1 = []
            i = 1
            for disk in free_disks:
                ch1.append(
                    (disk['id'], 'Disk %d - %s flash drive' % (i, disk['capacity'])))
                i += 1
            self.fields['disk'] = forms.ChoiceField(choices=ch1)
        else:
            ch = [('ramdisk', 'RAM disk')]
        self.fields['slog'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(SlogForm, self).clean()
        if cd['slog'] == 'ramdisk':
            if 'ramdisk_size' not in cd or not cd['ramdisk_size']:
                self._errors["ramdisk_size"] = self.error_class(
                    ["Please enter a RAMDISK size for a RAMDISK write cache"])
        return cd


class L2arcForm(forms.Form):
    pool = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        free_disks = None
        if kwargs and 'free_disks' in kwargs:
            free_disks = kwargs.pop('free_disks')
        super(L2arcForm, self).__init__(*args, **kwargs)
        if free_disks:
            ch1 = []
            i = 1
            for disk in free_disks:
                ch1.append(
                    (disk['id'], 'Disk %d - %s flash drive' % (i, disk['capacity'])))
                i += 1
            self.fields['disk'] = forms.ChoiceField(choices=ch1)


class QuotaForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)
    ug_type = forms.CharField(widget=forms.HiddenInput)
    size = forms.IntegerField()
    ch = [('GB', 'G'), ('MB', 'M')]
    unit = forms.ChoiceField(choices=ch)

    def __init__(self, *args, **kwargs):
        if kwargs:
            user_group_list = kwargs.pop('user_group_list')
        super(QuotaForm, self).__init__(*args, **kwargs)
        ch = []
        if user_group_list:
            for ug in user_group_list:
                tup = (ug, ug)
                ch.append(tup)
        self.fields["ug_name"] = forms.ChoiceField(choices=ch)


class ImportPoolForm(forms.Form):
    def __init__(self, *args, **kwargs):
        pools = []
        if kwargs and ('exported_pools' and 'destroyed_pools' in kwargs):
            [pools.append(name) for name in kwargs.pop('exported_pools')]
            [pools.append(name) for name in kwargs.pop('destroyed_pools')]

        super(ImportPoolForm, self).__init__(*args, **kwargs)
        ch = []
        if pools:
            for pool in pools:
                tup = (str(pool), str(pool))
                ch.append(tup)

            self.fields['name'] = forms.ChoiceField(choices=ch, widget=forms.Select())


class CreatePoolForm(forms.Form):
    name = forms.CharField()
    num_disks = forms.IntegerField(widget=forms.HiddenInput, required=False)
    dedup = forms.BooleanField(required=False)

    ch = [('rotational', 'All rotating drives'), ('flash', 'All flash drives')]
    disk_type = forms.ChoiceField(choices=ch)

    def __init__(self, *args, **kwargs):
        pol = None
        if kwargs:
            pool_types_list = kwargs.pop('pool_types')
            num_free_disks = kwargs.pop('num_free_disks')
        super(CreatePoolForm, self).__init__(*args, **kwargs)
        if pool_types_list:
            for t in pool_types_list:
                if t[0] in ['raid5', 'raid6', 'raid10', 'raid50', 'raid60']:
                    self.fields['num_raid_disks'] = forms.IntegerField(
                        required=False)
                if t[0] in ['raid10', 'raid50', 'raid60']:
                    max_stripe_width = num_free_disks / 2
                    stripes = []
                    i = 2
                    #stripes.append((2, 2))
                    while i <= max_stripe_width:
                        stripes.append(('%d' % i, '%d' % i))
                        i += 1
                    self.fields['stripe_width'] = forms.ChoiceField(
                        choices=stripes, required=False)
            self.fields['pool_type'] = forms.ChoiceField(
                choices=pool_types_list)

    def clean(self):
        cd = super(CreatePoolForm, self).clean()
        num_disks = cd['num_disks']
        if cd['pool_type'] in ['raid5', 'raid6', 'raid50', 'raid60']:
            if ('num_raid_disks' not in cd) or (not cd['num_raid_disks']):
                self._errors["num_raid_disks"] = self.error_class(
                    ["The number of RAID disks is required for a RAID pool"])
            else:
                if cd['num_raid_disks'] > num_disks:
                    self._errors["num_raid_disks"] = self.error_class(
                        ["The number of RAID disks exceeds the available number of disks. Only %d disks available" % num_disks])
                if cd['pool_type'] in ['raid10', 'raid50', 'raid60']:
                    if ('stripe_width' not in cd) or (not cd['stripe_width']):
                        self._errors["stripe_width"] = self.error_class(
                            ["Stripe width is required for the specified type of pool"])
                    else:
                        stripe_width = int(cd['stripe_width'])
                        if cd['pool_type'] == 'raid10':
                            multiplier = 2
                        else:
                            multiplier = int(cd['num_raid_disks'])
                        if (stripe_width * multiplier) > num_disks:
                            self._errors["stripe_width"] = self.error_class(
                                ["The number of disks with the stripe width and RAID disks combination exceeds the number of available disks. Only %d disks available" % num_disks])
        if ('name' in cd) and (not cd['name'].isalnum()):
            self._errors["name"] = self.error_class(
                ["The pool name cannot contain special characters."])
            del cd["name"]

        if 'name' in cd and cd['name'][0].isdigit():
            self._errors["name"] = self.error_class(
                ["The pool name cannot start with a number."])
            del cd["name"]
        return cd


class AddSparesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        if kwargs:
            num_free_drives = kwargs.pop('num_free_drives')
        super(AddSparesForm, self).__init__(*args, **kwargs)
        i = 1
        l = []
        while i <= num_free_drives:
            l.append(('%d' % i, '%d' % i))
            i += 1
        self.fields['num_spares'] = forms.ChoiceField(choices=l)


class CreateSnapshotForm(forms.Form):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            dsl = kwargs.pop('datasets')
        super(CreateSnapshotForm, self).__init__(*args, **kwargs)
        ch = []
        if dsl:
            for i in dsl:
                tup = (i, i)
                ch.append(tup)
        self.fields['target'] = forms.ChoiceField(choices=ch)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name and name.lower().startswith(('rrr_', 'zrr_')):
            self._errors["name"] = self.error_class(
                ["Can't start with 'rrr_' or 'zrr_', please try some other name"])
        return name


class ViewSnapshotsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            dsl = kwargs.pop('datasets')
        super(ViewSnapshotsForm, self).__init__(*args, **kwargs)
        ch = []
        if dsl:
            ch.append((None, '--All targets--'))
            for i in dsl:
                tup = (i, i)
                ch.append(tup)
        self.fields['name'] = forms.ChoiceField(choices=ch)


class ScheduleSnapshotForm(forms.Form):
    frequent = forms.BooleanField(required=False)
    hourly = forms.BooleanField(required=False)
    daily = forms.BooleanField(required=False)
    weekly = forms.BooleanField(required=False)
    monthly = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        vl = None
        if kwargs:
            dsl = kwargs.pop('datasets')
        super(ScheduleSnapshotForm, self).__init__(*args, **kwargs)
        ch = []
        if dsl:
            for i in dsl:
                tup = (i, i)
                ch.append(tup)
        self.fields['target'] = forms.ChoiceField(choices=ch)


class RenameSnapshotForm(forms.Form):
    ds_name = forms.CharField(widget=forms.HiddenInput)
    snapshot_name = forms.CharField(widget=forms.HiddenInput)
    new_snapshot_name = forms.CharField()


    def clean_new_snapshot_name(self):
        new_snapshot_name = self.cleaned_data['new_snapshot_name']
        if new_snapshot_name and new_snapshot_name.lower().startswith(('rrr_', 'zrr_')):
            self._errors["new_snapshot_name"] = self.error_class(
                ["Can't start with 'rrr_' or 'zrr_', please try some other name"])
        return new_snapshot_name


class DeleteSnapshotsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        child_fs = None
        child_fs_ch = []
        if kwargs:
            if 'child_fs' in kwargs:
                child_fs = kwargs.pop('child_fs')
        super(DeleteSnapshotsForm, self).__init__(*args, **kwargs)
        if child_fs:
            for fs in child_fs:
                child_fs_ch.append((fs,fs))

        self.fields['filesystems'] = forms.MultipleChoiceField(
            widget=forms.widgets.CheckboxSelectMultiple,
            choices=child_fs_ch,
            required=True)

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
