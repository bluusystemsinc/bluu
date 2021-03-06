# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from bluusites.models import Room
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
        self.fields['room'].queryset = Room.objects.filter(bluusite=self.bluusite)

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


    def clean(self):
        cleaned_data = self.cleaned_data
        serial = cleaned_data.get("serial")

        if self.instance:
            count = Device.objects.exclude(pk=self.instance.pk).\
                                    filter(serial=serial,
                                           bluusite=self.bluusite).count()
        else:
            count = Device.objects.filter(serial=serial,
                                    bluusite=self.bluusite).count()
        if count > 0:
           del cleaned_data["serial"]
           raise forms.ValidationError("Device with such serial already exists in this site.")
        return cleaned_data
