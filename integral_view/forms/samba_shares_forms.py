from django import forms
import common_forms
from integralstor import networking
from integral_view.forms import folder_management_forms


class AuthADSettingsForm(forms.Form):
    security = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(widget=forms.PasswordInput())
    realm = forms.CharField()
    workgroup = forms.CharField()
    password_server = forms.CharField()
    password_server_ip = forms.CharField()
    netbios_name = forms.CharField()

    def clean(self):
        cd = super(AuthADSettingsForm, self).clean()
        if 'password_server_ip' in cd:
            valid, err = networking.validate_ip(cd['password_server_ip'])
            if err:
                raise Exception(err)
            if not valid:
                del cd["password_server_ip"]
                self._errors["password_server_ip"] = self.error_class(
                    ["Please specify a valid IP address"])
        return cd


class AuthUsersSettingsForm(forms.Form):
    security = forms.CharField(widget=forms.HiddenInput)
    workgroup = forms.CharField()
    netbios_name = forms.CharField()


class CreateShareForm(folder_management_forms.DirForm):
    share_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    name = forms.CharField()
    comment = forms.CharField(required=False)
    browseable = forms.BooleanField(required=False, initial=True)
    read_only = forms.BooleanField(required=False)
    new_folder = forms.CharField(required=False)
    ch = [('all', 'All hosts'), ('restricted', 'Specified hosts')]
    hosts_allow_choice = forms.ChoiceField(choices=ch)
    ch = [('none', 'None'), ('restricted', 'Specified hosts')]
    hosts_deny_choice = forms.ChoiceField(choices=ch)
    hosts_allow = common_forms.MultipleServerField(required=False)
    hosts_deny = common_forms.MultipleServerField(required=False)

    def __init__(self, *args, **kwargs):
        if kwargs:
            dataset_list = kwargs.pop("dataset_list")
        super(CreateShareForm, self).__init__(*args, **kwargs)

        ch = []
        if dataset_list:
            for ds in dataset_list:
                tup = (ds[0], ds[1])
                ch.append(tup)
        self.fields['dataset'] = forms.ChoiceField(
            widget=forms.Select, choices=ch)

    def clean(self):
        cd = super(CreateShareForm, self).clean()
        if cd['hosts_allow_choice'] == 'restricted' and (('hosts_allow' not in cd) or (not cd['hosts_allow'])):
            self._errors['hosts_allow'] = self.error_class(
                ["Please specify a valid set of IP addresses or hostnames"])
        if cd['hosts_deny_choice'] == 'restricted' and (('hosts_deny' not in cd) or (not cd['hosts_deny'])):
            self._errors["hosts_deny"] = self.error_class(
                ["Please specify a valid set of IP addresses or hostnames"])
        return cd


class AddShareAcesForm(folder_management_forms.AddAcesForm):
    share_index = forms.IntegerField(widget=forms.HiddenInput)
    share_name = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AddShareAcesForm, self).__init__(*args, **kwargs)


class EditShareAcesForm(folder_management_forms.EditAcesForm):
    share_index = forms.IntegerField(widget=forms.HiddenInput)
    share_name = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(EditShareAcesForm, self).__init__(*args, **kwargs)


class EditShareForm(forms.Form):
    share_id = forms.IntegerField(widget=forms.HiddenInput)
    name = forms.CharField()
    path = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    browseable = forms.BooleanField(required=False)
    read_only = forms.BooleanField(required=False)
    ch = [('all', 'All hosts'), ('restricted', 'Specified hosts')]
    hosts_allow_choice = forms.ChoiceField(choices=ch)
    ch = [('none', 'None'), ('restricted', 'Specified hosts')]
    hosts_deny_choice = forms.ChoiceField(choices=ch)
    hosts_allow = common_forms.MultipleServerField(required=False)
    hosts_deny = common_forms.MultipleServerField(required=False)

    def clean(self):
        cd = super(EditShareForm, self).clean()
        if cd['hosts_allow_choice'] == 'restricted' and (('hosts_allow' not in cd) or (not cd['hosts_allow'])):
            self._errors['hosts_allow'] = self.error_class(
                ["Please specify a valid set of IP addresses or hostnames"])
        if cd['hosts_deny_choice'] == 'restricted' and (('hosts_deny' not in cd) or (not cd['hosts_deny'])):
            self._errors["hosts_deny"] = self.error_class(
                ["Please specify a valid set of IP addresses or hostnames"])
        return cd

    '''
  def __init__(self, *args, **kwargs):
    if kwargs:
      user_list = kwargs.pop("user_list")
      group_list = kwargs.pop("group_list")
    super(EditShareForm, self).__init__(*args, **kwargs)
    ch = []
    if user_list:
      for user in user_list:
        tup = (user, user)
        ch.append(tup)   
    self.fields["users"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )

    ch = []
    if group_list:
      for gr in group_list:
        tup = (gr, gr)
        ch.append(tup)   
    self.fields["groups"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'onclick':'select_guest_ok();'}), choices=ch,required=False )

  def clean(self):
    cd = super(EditShareForm, self).clean()
    go = cd['guest_ok']
    us = cd['users']
    gr = cd['users']
    if go:
      if us:
        self._errors["users"] = self.error_class(["This field cannot be set when guest ok is selected"])
        del cd["users"]
      if gr:
        self._errors["groups"] = self.error_class(["This field cannot be set when guest ok is selected"])
        del cd["groups"]
    else:
      if (not us) and (not gr):
        self._errors["guest_ok"] = self.error_class(["This field cannot be left unselected if no users or groups are selected"])
    return cd
  '''


# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
