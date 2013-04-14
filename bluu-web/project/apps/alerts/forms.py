# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions
from .models import (Alert, UserAlertDevice)


class DurationForm(forms.Form):
    duration = forms.IntegerField()
    unit = forms.ChoiceField(choices=Alert.UNITS)

    def __init__(self, device_type, alert, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        unit = layout.Field('unit', css_class="input-small unit", template='alerts/conf_unit_template.html')
        durak = layout.Field('duration', css_class="input-mili duration", maxlength="3", template='alerts/conf_duration_template.html')

        super(DurationForm, self).__init__(**kwargs)
        self.helper.layout = layout.Layout(durak, unit)

