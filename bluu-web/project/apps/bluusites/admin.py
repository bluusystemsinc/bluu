from django.contrib import admin
from django.contrib.contenttypes import generic

from grontextual.models import UserObjectGroup
from invitations.models import InvitationKey
from .models import BluuSite, BluuSiteAccess

class UOGInline(generic.GenericTabularInline):
    model = UserObjectGroup
    ct_fk_field = 'object_pk'

class BluuSiteAdmin(admin.ModelAdmin):
    inlines = [
        UOGInline,
    ]

class InvitationInline(generic.GenericTabularInline):
    model = InvitationKey

class BluuSiteAccessAdmin(admin.ModelAdmin):
    inlines = [
        InvitationInline,
    ]


admin.site.register(BluuSite, BluuSiteAdmin)
admin.site.register(BluuSiteAccess, BluuSiteAccessAdmin)
