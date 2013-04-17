# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms import layout

from .models import (UserAlertDevice, UserAlertConfig)


class DurationForm(forms.ModelForm):

    def __init__(self, **kwargs):
        super(DurationForm, self).__init__(**kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        unit = layout.Field('unit', css_class="alert_config input-small unit", template='alerts/conf_unit_template.html')
        durak = layout.Field('duration', css_class="alert_config input-mili duration", maxlength="3", template='alerts/conf_duration_template.html')


        self.fields['unit'].choices = self.fields['unit'].choices[1:]
        self.helper.layout = layout.Layout(durak, unit)

    class Meta:
        model = UserAlertConfig
        fields = ('duration', 'unit')


class NotificationForm(forms.ModelForm):

    def __init__(self, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        text = layout.Field('text_notification', css_class="alert_config text_input", template='alerts/conf_checkbox_template.html')
        email = layout.Field('email_notification', css_class="alert_config email_input", template='alerts/conf_checkbox_template.html')

        super(NotificationForm, self).__init__(**kwargs)
        self.fields['text_notification'].label = 'text'
        self.fields['email_notification'].label = 'email'
        self.helper.layout = layout.Layout(text, email)

    class Meta:
        model = UserAlertConfig
        fields = ('text_notification', 'email_notification')


class AlertDeviceForm(forms.ModelForm):

    def __init__(self, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        #text = layout.Field('text_notification', css_class="alert_config text_input", template='alerts/conf_checkbox_template.html')
        #email = layout.Field('email_notification', css_class="alert_config email_input", template='alerts/conf_checkbox_template.html')

        super(AlertDeviceForm, self).__init__(**kwargs)
        #self.fields['text_notification'].label = 'text'
        #self.fields['email_notification'].label = 'email'
        self.helper.layout = layout.Layout('device')

    class Meta:
        model = UserAlertDevice
        fields = ('device',)

