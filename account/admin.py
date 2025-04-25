from django.contrib import admin

from .models import Otp, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["phone_number"]


admin.site.register(User, UserAdmin)
admin.site.register(Otp)
