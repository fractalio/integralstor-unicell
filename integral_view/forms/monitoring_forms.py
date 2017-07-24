from django import forms
import admin_forms

class AlertNotificationsForm(forms.Form):
    recipient_list = admin_forms.MultipleEmailField()
    def __init__(self, *args, **kwargs):
        reference_subsystem_types = None
        reference_severity_types = None
        reference_notification_types = None
        if kwargs and 'reference_subsystem_types' in kwargs:
            reference_subsystem_types = kwargs.pop('reference_subsystem_types')
        if kwargs and 'reference_severity_types' in kwargs:
            reference_severity_types = kwargs.pop('reference_severity_types')
        if kwargs and 'reference_notification_types' in kwargs:
            reference_notification_types = kwargs.pop('reference_notification_types')
        super(AlertNotificationsForm,
              self).__init__(*args, **kwargs)
        ch = []
        if reference_subsystem_types:
            for id, description in reference_subsystem_types.items():
                if id == -1:
                    continue
                ch.append((id, description))
        self.fields['subsystem_type_id'] = forms.ChoiceField(choices=ch)
        ch = []
        if reference_severity_types:
            for id, description in reference_severity_types.items():
                if id == -1:
                    continue
                ch.append((id, description))
        self.fields['severity_type_id'] = forms.ChoiceField(choices=ch)
        ch = []
        if reference_notification_types:
            for id, description in reference_notification_types.items():
                ch.append((id, description))
        self.fields['notification_type_id'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(AlertNotificationsForm, self).clean()
        #print 'form cd', cd
        if int(cd['notification_type_id']) == 1:
            if 'recipient_list' not in cd or (not cd['recipient_list']):
                self._errors["recipient_list"] = self.error_class(
                    ["The recipient list is required."])
        return cd

class AuditNotificationsForm(forms.Form):
    recipient_list = admin_forms.MultipleEmailField()
    def __init__(self, *args, **kwargs):
        reference_notification_types = None
        if kwargs and 'reference_notification_types' in kwargs:
            reference_notification_types = kwargs.pop('reference_notification_types')
        super(AuditNotificationsForm,
              self).__init__(*args, **kwargs)
        ch = []
        if reference_notification_types:
            for id, description in reference_notification_types.items():
                ch.append((id, description))
        self.fields['notification_type_id'] = forms.ChoiceField(choices=ch)

    def clean(self):
        cd = super(AuditNotificationsForm, self).clean()
        #print 'form cd', cd
        if int(cd['notification_type_id']) == 1:
            if 'recipient_list' not in cd or (not cd['recipient_list']):
                self._errors["recipient_list"] = self.error_class(
                    ["The recipient list is required."])
        return cd
# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
