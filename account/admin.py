from django.contrib import admin

from .models import Fcm, Notification, NotificationSetting, Otp, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "name"]


admin.site.register(User, UserAdmin)
admin.site.register(Otp)
admin.site.register(Fcm)
admin.site.register(Notification)
admin.site.register(NotificationSetting)
