# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions
from .models import Company


class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                    'name',
                    'street',
                    'city',
                    'state',
                    'zip_code',
                    'country',
                    'phone',
                    'email',
                    'contact_name',
            ),
            FormActions(
                layout.Submit('submit', _('Submit'), css_class="btn-primary")
            )
        )
        super(CompanyForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Company
        fields = ('name', 'street', 'city', 'state', 'zip_code', 'country',
                  'phone', 'email', 'contact_name')

