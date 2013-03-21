from django.contrib import admin
from django.contrib.contenttypes import generic

from grontextual.models import UserObjectGroup
from invitations.models import InvitationKey
from .models import Company, CompanyAccess

class UOGInline(generic.GenericTabularInline):
    model = UserObjectGroup
    ct_fk_field = 'object_pk'

class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        UOGInline,
    ]


class InvitationInline(generic.GenericTabularInline):
    model = InvitationKey

class CompanyAccessAdmin(admin.ModelAdmin):
    inlines = [
        InvitationInline,
    ]


admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyAccess, CompanyAccessAdmin)
