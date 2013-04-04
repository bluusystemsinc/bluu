from django.contrib import admin

from .models import (Alert, UserAlert)


admin.site.register(Alert)
admin.site.register(UserAlert)
