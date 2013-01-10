from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Site, Company, BluuUser


class BluuUserAdmin(UserAdmin):
    pass

admin.site.register(Site)
admin.site.register(Company)
admin.site.register(BluuUser, BluuUserAdmin)
