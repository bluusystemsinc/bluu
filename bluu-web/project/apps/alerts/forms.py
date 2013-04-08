# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions
from .models import UserAlert


class DurationForm(forms.Form):
    time = forms.IntegerField()
    unit = forms.ChoiceField(choices=UserAlert.UNITS)

    def __init__(self, device_type, alert, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        unit = layout.Field('unit', css_class="input-small", template='alerts/conf_unit_template.html')
        unit.attrs['ng-model'] = 'id_{}_unit'.format(alert.id)
        unit.attrs['ng-change'] = 'alert(\'change all enabled alerts for this alert type\');'
        durak = layout.Field('time', css_class="input-mili", maxlength="3", template='alerts/conf_time_template.html')
        durak.attrs['ng-model'] = 'id_{}_time'.format(alert.id)

        super(DurationForm, self).__init__(**kwargs)
        self.helper.layout = layout.Layout(durak, unit)

