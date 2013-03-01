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

from .models import Device

class DeviceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.bluusite = kwargs.pop('bluusite')

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                    layout.Field('name'),
                    layout.Field('serial'),
                    layout.Field('device_type'),
                    layout.Field('room'),
            ),
            FormActions(
                layout.Submit('submit', _('Submit'), css_class="btn-primary")
            )
        )

        super(DeviceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Device
        fields = ('name', 'serial', 'device_type', 'room')

    def save(self, commit=True):
        instance = super(DeviceForm, self).save(commit=False)
        if hasattr(self, 'bluusite') and self.bluusite is not None:
            instance.bluusite = self.bluusite
        instance.save()
        if commit:
            self.save_m2m()
        return instance


