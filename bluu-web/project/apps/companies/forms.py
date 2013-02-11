# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from accounts.forms import BluuUserForm
from .models import Company, CompanyAccess


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


class CompanyBluuUserForm(BluuUserForm):
    def __init__(self, user, company, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.company = kwargs.pop('company')
        super(CompanyBluuUserForm, self).__init__(*args, **kwargs)


class CompanyInvitationForm(forms.ModelForm):
    #email = forms.EmailField()
    #group = forms.ChoiceField()

    class Meta:
        model = CompanyAccess
        fields = ('email', 'group')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        self.request = kwargs.pop('request', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                    layout.Field('email', placeholder='e-mail'),
                    layout.Field('group')
            ),
            FormActions(
                layout.Submit('submit', _('Submit'), css_class="btn-primary")
            )
        )
        super(CompanyInvitationForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = [('', '---')] + [(group.pk, group.name) for group in Group.objects.filter(name__in=settings.COMPANY_GROUPS)]
        self.fields['group'].label = ''
        self.fields['group'].widget.attrs['ng-model'] = 'company_access.group'
        self.fields['email'].label = ''
        self.fields['email'].widget.attrs['ng-model'] = 'company_access.email'
        self.fields['email'].widget.attrs['placeholder'] = 'e-mail'

    def clean(self):
        cleaned_data = super(CompanyInvitationForm, self).clean()
        email = cleaned_data.get("email")
        group = cleaned_data.get("group")
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            user = None

        if not self.instance.pk:
            if user and \
                CompanyAccess.objects.filter(company=self.company, user=user).exists():
                raise forms.ValidationError(_('User with the same e-mail has already been granted access.'))
            elif email and \
                    CompanyAccess.objects.filter(company=self.company, email=email).exists():
                raise forms.ValidationError(_('User with the same e-mail has already been granted access.'))
        # Always return the full collection of cleaned data.
        return cleaned_data

#class CompanyInvitationForm_old(forms.Form):
#    email = forms.EmailField()
#    group = forms.ChoiceField()
#
#    def __init__(self, *args, **kwargs):
#        self.helper = FormHelper()
#        self.helper.form_tag = False
#        self.helper.layout = layout.Layout(
#            layout.Div(
#                    layout.Field('email', placeholder='e-mail'),
#                    layout.Field('group')
#            ),
#            FormActions(
#                layout.Submit('submit', _('Submit'), css_class="btn-primary")
#            )
#        )
#        super(CompanyInvitationForm, self).__init__(*args, **kwargs)
#        self.fields['group'].choices = [('', '---')] + [(group.pk, group.name) for group in Group.objects.filter(name__in=["Dealer", "Technician"])]
#        self.fields['group'].label = ''
#        self.fields['group'].widget.attrs['ng-model'] = 'company_access.group'
#        self.fields['email'].label = ''
#        self.fields['email'].widget.attrs['ng-model'] = 'company_access.email'


