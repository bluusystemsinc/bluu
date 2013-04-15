# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions
from .models import (Alert, UserAlertDevice, UserAlertConfig)


class DurationForm(forms.ModelForm):
    #duration = forms.IntegerField()
    #unit = forms.ChoiceField(choices=Alert.UNITS)

    def __init__(self, device_type, alert, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        unit = layout.Field('unit', css_class="input-small unit", template='alerts/conf_unit_template.html')
        durak = layout.Field('duration', css_class="input-mili duration", maxlength="3", template='alerts/conf_duration_template.html')

        super(DurationForm, self).__init__(**kwargs)
        self.helper.layout = layout.Layout(durak, unit)

    class Meta:
        model = UserAlertConfig
        fields = ('duration', 'unit')


class NotificationForm(forms.ModelForm):
    #duration = forms.IntegerField()
    #unit = forms.ChoiceField(choices=Alert.UNITS)

    def __init__(self, device_type, alert, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        text = layout.Field('text_notification') #, css_class="input-small unit", template='alerts/conf_unit_template.html')
        email = layout.Field('email_notification') #, css_class="input-mili duration", maxlength="3", template='alerts/conf_duration_template.html')

        super(NotificationForm, self).__init__(**kwargs)
        self.helper.layout = layout.Layout(text, email)

    class Meta:
        model = UserAlertConfig
        fields = ('text_notification', 'email_notification')

