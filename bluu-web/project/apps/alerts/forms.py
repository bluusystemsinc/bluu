# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions


class DurationForm(forms.Form):
    SECONDS = 's'
    MINUTES = 'm'
    HOURS = 'h'
    DAYS = 'd'
    UNITS = (
        (SECONDS, _('seconds')),
        (MINUTES, _('minutes')),
        (HOURS, _('hours')),
        (DAYS, _('days')),
    )
    time = forms.IntegerField()
    unit = forms.ChoiceField(choices=UNITS)

    def __init__(self, device_type, alert, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        super(DurationForm, self).__init__(**kwargs)
        self.helper.layout = layout.Layout(
            layout.Field('time', css_class="input-mili", maxlength="3", template='alerts/conf_time_template.html'),
            layout.Field('unit', css_class="input-small", template='alerts/conf_unit_template.html'),
        )

