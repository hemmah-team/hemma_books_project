from rest_framework import serializers

from .models import User


class RegisterSerizalizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "name",
            "password",
            "phone_number",
            "fcm",
        ]
        extra_kwargs = {"password": {"write_only": True}, "fcm": {"write_only": True}}
