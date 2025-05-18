from django.contrib import admin

from .models import Notification, Otp, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "phone_number", "name"]


admin.site.register(User, UserAdmin)
admin.site.register(Otp)
admin.site.register(Notification)
