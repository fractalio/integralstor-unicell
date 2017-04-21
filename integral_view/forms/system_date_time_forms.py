from django import forms
import pytz
import datetime


class DateTimeForm(forms.Form):
    system_time = forms.CharField(required=False)
    system_date = forms.CharField(required=False)
    system_timezone = forms.ChoiceField(choices = [(item, item + ' ' + datetime.datetime.now(pytz.timezone(item)).strftime('%Z (GMT%z)')) for item in pytz.common_timezones], required=False)

    def clean(self):
        cd = super(DateTimeForm, self).clean()
        if ('system_time' not in cd or cd['system_time'] == '') and ('system_date' not in cd or cd['system_date'] == '') and ('system_timezone' not in cd or cd['system_timezone'] == '') :
            raise forms.ValidationError(
                "Atleast date, time or timezone should be present")
        else:
            if 'system_date' in cd:
                if cd['system_date'] == '':
                    cd['system_date'] = None
            if 'system_time' in cd:
                if cd['system_time'] == '':
                    cd['system_time'] = None
            if 'system_timezone' in cd:
                if cd['system_timezone'] == '':
                    cd['system_timezone'] = None
            return cd
