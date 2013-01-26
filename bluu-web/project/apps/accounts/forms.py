# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db.models.base import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from registration.forms import RegistrationFormTermsOfService
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, HTML, Fieldset, Div, Field
from crispy_forms.bootstrap import FormActions
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm #SetPasswordForm
from django.shortcuts import redirect, render_to_response, get_object_or_404

#from accounts.models import UserProfile
#from mieszkanie.layout import BootstrappedSubmit
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import Company, Site, BluuUser

rev = lambda s: reverse(s)

# force emails to be uniqe
# User._meta.get_field_by_name('email')[0]._unique = True


class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
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
                Submit('submit', _('Submit'), css_class="btn-primary")
            )
        )
        super(CompanyForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Company
        fields = ('name', 'street', 'city', 'state', 'zip_code', 'country',
                  'phone', 'email', 'contact_name')


class SiteForm(ModelForm):


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        company = Field('company', required="required")
        company.attrs['ng-model'] = "site.company"
        first_name = Field('first_name', required="")
        first_name.attrs['ng-model'] = "site.first_name"
        middle_initial = Field('middle_initial')
        middle_initial.attrs['ng-model'] = "site.middle_initial"
        last_name = Field('last_name', required="")
        last_name.attrs['ng-model'] = "site.last_name"
        city = Field('city')
        city.attrs['ng-model'] = "site.city"
        state = Field('state')
        state.attrs['ng-model'] = "site.state"
        zip_code = Field('zip_code')
        zip_code.attrs['ng-model'] = "site.zip_code"
        country = Field('country')
        country.attrs['ng-model'] = "site.country"
        phone = Field('phone')
        phone.attrs['ng-model'] = "site.phone"
        email = Field('email', type='email')
        email.attrs['ng-model'] = "site.email"

        submit = Submit('submit', _('Submit'), css_class="btn-primary")
        submit.flat_attrs += 'ng-click="save(site)" ng-disabled="newsite.$invalid"'

        self.helper.layout = Layout(
            Div(
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
        model = Site
        fields = ('first_name', 'middle_initial', 'last_name', 
                  'city', 'state', 'zip_code', 'country', 'phone', 'email')


class BluuUserForm(ModelForm):
    username = forms.RegexField(regex=r'^\w+$',
            max_length=30,
            label=_('Username'),
            required=True,
            help_text=_('30 characters or fewer. Alphanumeric '
                        'characters only (letters, digits and underscores).'),
            error_message=_('This value must contain only letters, '
                            'numbers and underscores.'))
    email = forms.EmailField(required=False, label=_('Email'))
    first_name = forms.CharField(required=True, label=_('First name'))
    last_name = forms.CharField(required=True, label=_('Last name'))
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput,
                                required=False)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                required=False)

    def __init__(self, user, contract, *args, **kwargs):
        super(BluuUserForm, self).__init__(*args, **kwargs)
        self.user = user
        self.contract = contract

        if self.instance.pk:
            self.fields['password2'].help_text =\
            ("Leave both password fields blank if you don't want to change it")

        self.fields.keyOrder = ['username',
            'first_name', 'last_name', 'email',
            'password1', 'password2', 'cell', 'cell_text_email', 'is_active'
        ]

        if self.user.has_perm('accounts.manage_group_admins'):
            self.fields.keyOrder.append('groups')

    class Meta:
        model = BluuUser
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active',
                  'groups', 'cell', 'cell_text_email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                            ugettext("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(BluuUserForm, self).save(commit=False)

        # if user doesn't have manage_group_admins permission then
        # he can only add (edit) standard users
        # (neither TestCenter Admins nor Group Admins) to his entity
        if user.pk and \
                not self.user.has_perm('accounts.manage_dealers'):
            user.groups.clear()

        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            user.contract.add(self.contract)

        self.save_m2m = save_m2m

        if commit:
            user.save()
            self.save_m2m()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"))

dummy_trans = _("If you don't want to change your password leave these fields empty.")

attrs_dict = {'class': 'required'}
class RegistrationForm(RegistrationFormTermsOfService):
    first_name = forms.CharField(label=_("First name"), max_length=30)
    last_name = forms.CharField(label=_("Last name"), max_length=30)
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
            label=_(u'I have read and agree to the <a href="%(url)s">Terms of Service</a>') % {'url': settings.TOS_URL},
                             error_messages={'required': _("You must agree to the terms to register")})

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-RegistrationForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'registration_register'
        self.helper.form_style = 'inline'
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Fieldset(_('Register to be able to change your photo'),
                    'first_name',
                    'last_name',
                    'email',
                    'password1',
                    'password2',
                    'tos',
                    ),
        )
        self.fields.keyOrder = ('first_name', 'last_name', 'email', 'password1', 'password2', 'tos') # username is autogenerated so we remove it


    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError(_("This email address already exists."))
        except User.DoesNotExist:
            return email

class ProfileForm(ModelForm):
    email = forms.EmailField(label=_(u"E-mail"), help_text='')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        uni_fields = ['email']

        if self.instance.pk:  # profile and user already exists
            self.fields['email'].initial = self.instance.user.email
        #else:  # just create profile, don't overwrite email assigned to User
        #    del self.fields['email']
        #    uni_fields.remove('email')

        self.helper = FormHelper()
        self.helper.form_id = 'id-ProfileForm'
        self.helper.form_style = 'inline'
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Fieldset(_('Profile'),
                    *uni_fields
                    ),
                ButtonHolder(BootstrappedSubmit('submit', _('Submit')))
        )

    #class Meta:
    #    model = UserProfile
    #    exclude = ('user',)

    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        profile = super(ProfileForm, self).save(*args,**kwargs)
        if self.instance.pk:  # profile exists
            u = self.instance.user
            u.email = self.cleaned_data['email']
            u.save()
        return profile


#class AccountForm(SetPasswordForm):
class AccountForm(forms.ModelForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput, required=False)
    new_password1 = forms.CharField(label=_("Password"),
                                    widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label=_("Password confirmation"),
                                    widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        self.helper = FormHelper()
        self.helper.form_id = 'id-AccountForm'
        self.helper.form_style = 'inline'
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Fieldset(_(u'Your data'),
                    'first_name',
                    'last_name',),
                Fieldset(_(u'Password'),
                    HTML("""{% load i18n %}
                    <p class="info">{% trans "If you don't want to change your password leave these fields empty." %}</p>
                    """),
                    'old_password',
                    'new_password1',
                    'new_password2',),
        )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'old_password', 'new_password1',
                  'new_password2')

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 != password2:
            raise forms.ValidationError(\
                    _("The two password fields didn't match."))
        return password2

    def clean(self):
        if self.instance.pk and self.fields.has_key('old_password'):
            password1 = self.cleaned_data.get('new_password1')
            password2 = self.cleaned_data.get('new_password2')
            if password1 and password2 and password1 == password2:
                if not self.instance.check_password(\
                    self.cleaned_data.get('old_password', '')):
                    self._errors['old_password'] = self.error_class([_("Your old password was entered incorrectly. Please enter it again.")])
                    del self.cleaned_data['old_password']
        return self.cleaned_data

    def save(self, commit=True):
        form = super(AccountForm, self)
        user = form.save()
        password = self.cleaned_data["new_password1"]
        if password:
            user.set_password(password)
            user.save()
        return user


