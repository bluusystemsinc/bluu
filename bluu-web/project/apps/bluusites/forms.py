# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions
from .models import BluuSite

class SiteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        #company = Field('company', required="required")
        #company.attrs['ng-model'] = "site.company"
        first_name = layout.Field('first_name', required="required")
        first_name.attrs['ng-model'] = "site.first_name"
        middle_initial = layout.Field('middle_initial')
        middle_initial.attrs['ng-model'] = "site.middle_initial"
        last_name = layout.Field('last_name', required="required")
        last_name.attrs['ng-model'] = "site.last_name"
        city = layout.Field('city')
        city.attrs['ng-model'] = "site.city"
        state = layout.Field('state')
        state.attrs['ng-model'] = "site.state"
        zip_code = layout.Field('zip_code')
        zip_code.attrs['ng-model'] = "site.zip_code"
        country = layout.Field('country')
        country.attrs['ng-model'] = "site.country"
        phone = layout.Field('phone')
        phone.attrs['ng-model'] = "site.phone"
        email = layout.Field('email', type='email')
        email.attrs['ng-model'] = "site.email"

        submit = Submit('submit', _('Submit'), css_class="btn-primary")
        submit.flat_attrs += 'ng-click="save(site)" ng-disabled="newsite.$invalid"'

        self.helper.layout = layout.Layout(
            layout.Div(
                    first_name,
                    middle_initial,
                    last_name,
                    city,
                    state,
                    zip_code,
                    country,
                    phone,
                    email,
            ),
            FormActions(
               submit 
            )
        )
        super(SiteForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'type':'email'})
        #self.fields['email'].required = True

        """self.user = kwargs.pop('user')
        try:
            self.company = kwargs.pop('company')
        except KeyError:
            pass
        if not self.user.has_perm('accounts.manage_site'):
            self.fields['company'].queryset = self.user.companies.get(pk=self.company.pk)
        else:
            self.fields['company'].queryset = Company.objects.get(pk=self.company.pk)
        # user with 'manage_site' permission can assign site to any company
        if not self.user.has_perm('accounts.manage_site'):
            self.fields['company'].queryset = self.user.companies.all()
        """

    class Meta:
        model = BluuSite
        fields = ('first_name', 'middle_initial', 'last_name', 
                  'city', 'state', 'zip_code', 'country', 'phone', 'email')

