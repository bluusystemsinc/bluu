# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import Http404
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
        company = layout.Field('company', required="required")
        #company.attrs['ng-model'] = "site.company"
        first_name = layout.Field('first_name', required="required")
        #first_name.attrs['ng-model'] = "site.first_name"
        middle_initial = layout.Field('middle_initial')
        #middle_initial.attrs['ng-model'] = "site.middle_initial"
        last_name = layout.Field('last_name', required="required")
        #last_name.attrs['ng-model'] = "site.last_name"
        street = layout.Field('street')
        #street.attrs['ng-model'] = "site.street"
        city = layout.Field('city')
        #city.attrs['ng-model'] = "site.city"
        state = layout.Field('state')
        #state.attrs['ng-model'] = "site.state"
        zip_code = layout.Field('zip_code')
        #zip_code.attrs['ng-model'] = "site.zip_code"
        country = layout.Field('country')
        #country.attrs['ng-model'] = "site.country"
        phone = layout.Field('phone')
        #phone.attrs['ng-model'] = "site.phone"
        email = layout.Field('email', type='email')
        #email.attrs['ng-model'] = "site.email"

        submit = Submit('submit', _('Submit'), css_class="btn-primary")
        submit.flat_attrs += 'ng-click="save(site)" ng-disabled="newsite.$invalid"'

        self.helper.layout = layout.Layout(
            layout.Div(
                    company,
                    first_name,
                    middle_initial,
                    last_name,
                    street,
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
        self.user = kwargs.pop('user', None)
        super(SiteForm, self).__init__(*args, **kwargs)

        # If this form is called in a context where company is to be chosen
        # from user assigned companies then there should be a current user
        # instance passed to the form.
        if self.user is not None:
            companies = self.user.get_companies()
            company_count = companies.count()
            if company_count == 1:
                # If there is only one company assigned to a user then there is
                # no need to force him to select this company in the form.
                self.company = companies[0]
                # remove company from crispy forms layout
                self.helper.layout[0].pop(0)
                # remove company from fields
                del self.fields['company']
            else:
                # Else allow user to choose one company from assigned companies
                self.fields['company'].choices = [('', '---')] +\
                        [(company.pk, company.name) for company in companies]

    class Meta:
        model = BluuSite
        fields = ('company', 'first_name', 'middle_initial', 'last_name',
                  'street', 'city', 'state', 'zip_code', 'country', 'phone',
                  'email')

    def save(self, commit=True):
        instance = super(SiteForm, self).save(commit=False)
        if hasattr(self, 'company') and self.company is not None:
            instance.company = self.company
        instance.save()
        if commit:
            self.save_m2m()
        return instance
