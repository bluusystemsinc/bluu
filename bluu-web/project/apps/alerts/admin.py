from django.contrib import admin

from .models import (Alert, UserAlertConfig, UserAlertDevice, UserAlertRoom)


admin.site.register(Alert)
admin.site.register(UserAlertConfig)
admin.site.register(UserAlertDevice)
admin.site.register(UserAlertRoom)
