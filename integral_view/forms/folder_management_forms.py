from django import forms

from integralstor import config


class AddAcesForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)
    recursive = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            user_list = kwargs.pop("user_list")
            group_list = kwargs.pop("group_list")
        super(AddAcesForm, self).__init__(*args, **kwargs)
        ch = []
        if user_list:
            for user in user_list:
                tup = (user, user)
                ch.append(tup)
        self.fields["users"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
            attrs={'onclick': 'select_guest_ok();'}), choices=ch, required=False)

        ch = []
        if group_list:
            for gr in group_list:
                tup = (gr, gr)
                ch.append(tup)
        self.fields["groups"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(
            attrs={'onclick': 'select_guest_ok();'}), choices=ch, required=False)


class EditAcesForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)
    recursive = forms.BooleanField(required=False)
    ou_r = forms.BooleanField(required=False)
    ou_w = forms.BooleanField(required=False)
    ou_x = forms.BooleanField(required=False)

    og_r = forms.BooleanField(required=False)
    og_w = forms.BooleanField(required=False)
    og_x = forms.BooleanField(required=False)

    ot_r = forms.BooleanField(required=False)
    ot_w = forms.BooleanField(required=False)
    ot_x = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            user_list = kwargs.pop("user_list")
            group_list = kwargs.pop("group_list")
        super(EditAcesForm, self).__init__(*args, **kwargs)
        ch = []
        if user_list:
            for user in user_list:
                self.fields['user_%s_r' %
                            user[2]] = forms.BooleanField(required=False)
                self.fields["user_%s_w" %
                            user[2]] = forms.BooleanField(required=False)
                self.fields["user_%s_x" %
                            user[2]] = forms.BooleanField(required=False)
        if group_list:
            for group in group_list:
                self.fields["group_%s_r" %
                            group[2]] = forms.BooleanField(required=False)
                self.fields["group_%s_w" %
                            group[2]] = forms.BooleanField(required=False)
                self.fields["group_%s_x" %
                            group[2]] = forms.BooleanField(required=False)


class CreateDirForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)
    dir_name = forms.CharField()


class DirForm(forms.Form):
    path = forms.CharField(widget=forms.HiddenInput)


class ModifyStickyBitForm(DirForm):
    recursive = forms.BooleanField(required=False)
    sticky_bit_enabled = forms.BooleanField(required=False)


class DirManagerForm(DirForm):
    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(DirManagerForm, self).__init__(*args, **kwargs)
        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = (ds[0], ds[1])
                ch.append(tup)
        self.fields['dataset'] = forms.ChoiceField(
            widget=forms.Select, choices=ch)


class DirManagerForm1(DirForm):
    def __init__(self, *args, **kwargs):
        if kwargs:
            pool_list = kwargs.pop("pool_list")
        super(DirManagerForm1, self).__init__(*args, **kwargs)
        ch = []
        if pool_list:
            for p in pool_list:
                tup = (p, p)
                ch.append(tup)
        self.fields['pool'] = forms.ChoiceField(
            widget=forms.Select, choices=ch)


class ModifyOwnershipForm(DirForm):
    path = forms.CharField(widget=forms.HiddenInput)
    user_name = forms.CharField(widget=forms.HiddenInput)
    group_name = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            user_list = kwargs.pop("user_list")
            group_list = kwargs.pop("group_list")
        super(ModifyOwnershipForm, self).__init__(*args, **kwargs)
        owner_dict, err = config.get_default_file_dir_owner()
        if err:
            raise Exception(err)
        owner_uid, err = config.get_system_uid_gid(owner_dict['user'])
        if err:
            raise Exception(err)
        ch = []
        if group_list:
            for group in group_list:
                tup = (group['gid'], group['grpname'])
                ch.append(tup)
        ch.append((owner_uid, owner_dict['user']))
        self.fields['gid'] = forms.ChoiceField(
            widget=forms.Select, choices=ch, required=False)

        owner_gid, err = config.get_system_uid_gid(owner_dict['group'])
        if err:
            raise Exception(err)

        ch = []
        if user_list:
            for user in user_list:
                tup = (user['uid'], user['username'])
                ch.append(tup)
        ch.append((owner_gid, owner_dict['group']))
        self.fields['uid'] = forms.ChoiceField(
            widget=forms.Select, choices=ch, required=False)


class SetFileOwnerAndPermissionsForm(forms.Form):

    owner_read = forms.BooleanField(required=False)
    owner_write = forms.BooleanField(required=False)
    owner_execute = forms.BooleanField(required=False)
    group_read = forms.BooleanField(required=False)
    group_write = forms.BooleanField(required=False)
    group_execute = forms.BooleanField(required=False)
    other_read = forms.BooleanField(required=False)
    other_write = forms.BooleanField(required=False)
    other_execute = forms.BooleanField(required=False)
    set_owner = forms.BooleanField(required=False)
    set_group = forms.BooleanField(required=False)

    path = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        if kwargs:
            group_list = kwargs.pop("group_list")
            user_list = kwargs.pop("user_list")
        super(SetFileOwnerAndPermissionsForm, self).__init__(*args, **kwargs)

        ch = []
        if group_list:
            for group in group_list:
                tup = (group['gid'], group['grpname'])
                ch.append(tup)
        self.fields['gid'] = forms.ChoiceField(
            widget=forms.Select, choices=ch, required=False)

        ch = []
        if user_list:
            for user in user_list:
                tup = (user['uid'], user['username'])
                ch.append(tup)
        self.fields['uid'] = forms.ChoiceField(
            widget=forms.Select, choices=ch, required=False)


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
