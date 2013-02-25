from django.contrib import admin
from .models import InvitationKey

class InvitationKeyAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'from_user', 'date_invited', 'key_expired')

class InvitationUserAdmin(admin.ModelAdmin):
    list_display = ('inviter',)

admin.site.register(InvitationKey, InvitationKeyAdmin)
