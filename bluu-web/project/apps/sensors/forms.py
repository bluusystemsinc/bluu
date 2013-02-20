# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from .models import Sensor

class SensorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = Sensor


