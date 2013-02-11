from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import BluuUser


class BluuUserChangeForm(UserChangeForm):

    class Meta:
        model = get_user_model()


class BluuUserCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class BluuUserAdmin(UserAdmin):
    form = BluuUserChangeForm
    add_form = BluuUserCreationForm
    fieldsets = (
        (None, {'fields': [('username', 'password'),]}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )

admin.site.register(BluuUser, BluuUserAdmin)
