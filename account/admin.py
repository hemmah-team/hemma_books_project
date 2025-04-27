from django.contrib import admin

from .models import Notification, Otp, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["phone_number"]


admin.site.register(User, UserAdmin)
admin.site.register(Otp)
admin.site.register(Notification)
