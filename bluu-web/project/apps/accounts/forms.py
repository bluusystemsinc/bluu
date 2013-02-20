# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _, ugettext
from django.core.urlresolvers import reverse

from registration.forms import RegistrationFormTermsOfService
from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.bootstrap import FormActions

from django.contrib.auth.forms import AuthenticationForm
from accounts.models import BluuUser

rev = lambda s: reverse(s)


class BluuUserForm(ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    email = forms.EmailField(required=False, label=_('Email'))
    first_name = forms.CharField(required=True, label=_('First name'))
    last_name = forms.CharField(required=True, label=_('Last name'))
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput,
                                required=False)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."),
                                required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(
            layout.Div(
                    'username',
                    'first_name',
                    'last_name',
                    'groups',
                    'email',
                    'password1',
                    'password2',
                    'cell',
                    'cell_text_email',
                    'is_active',
            ),
            FormActions(
                layout.Submit('submit', _('Submit'), css_class="btn-primary")
            )
        )
        super(BluuUserForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['password2'].help_text =\
            ("Leave both password fields blank if you don't want to change it")
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

        self.fields.keyOrder = ['username',
            'first_name', 'last_name', 'groups', 'email',
            'password1', 'password2', 'cell', 'cell_text_email', 'is_active'
        ]

        #if self.user.has_perm('accounts.manage_group_admins'):
        #    self.fields.keyOrder.append('groups')

    class Meta:
        model = BluuUser
        fields = ('username', 'first_name', 'last_name', 'groups', 'email', 'is_active',
                  'groups', 'cell', 'cell_text_email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                ugettext("Passwords don't match"))
        return password2

    def save(self, commit=True):
        user = super(BluuUserForm, self).save(commit=False)

        # if user doesn't have manage_group_admins permission then
        # he can only add (edit) standard users
        #if user.pk and \
        #        not self.user.has_perm('accounts.manage_dealers'):
        #    user.groups.clear()

        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        # Prepare a 'save_m2m' method for the form,
        #old_save_m2m = self.save_m2m
        #def save_m2m():
        #    old_save_m2m()
        #self.save_m2m = save_m2m

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
        self.helper.layout = layout.Layout(
                layout.Fieldset(_('Register to be able to change your photo'),
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
            user = BluuUser.objects.get(email=email)
            raise forms.ValidationError(_("This email address already exists."))
        except BluuUser.DoesNotExist:
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
        self.helper.layout = layout.Layout(
                layout.Fieldset(_('Profile'),
                    *uni_fields
                    ),
                layout.ButtonHolder(layout.Submit('submit', _('Submit')))
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
        self.helper.layout = layout.Layout(
                layout.Fieldset(_(u'Your data'),
                    'first_name',
                    'last_name',),
                layout.Fieldset(_(u'Password'),
                    layout.HTML("""{% load i18n %}
                    <p class="info">{% trans "If you don't want to change your password leave these fields empty." %}</p>
                    """),
                    'old_password',
                    'new_password1',
                    'new_password2',),
        )

    class Meta:
        model = BluuUser
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


