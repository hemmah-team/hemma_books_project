from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Notification, NotificationSetting, User

ALLOWED_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "protonmail.com",
    "aol.com",
    "mail.com",
    "zoho.com",
    "yandex.com",
]


def validate_email_domain(value):
    domain = value.split("@")[-1].lower()
    if domain not in ALLOWED_EMAIL_DOMAINS:
        raise ValidationError(
            f"Email domain must be one of: {', '.join(ALLOWED_EMAIL_DOMAINS)}"
        )
    return value


class RegisterSerizalizer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_email_domain])

    class Meta:
        model = User
        fields = ["email", "name", "password", "phone_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_email_domain])

    class Meta:
        model = User
        fields = ["id", "name", "phone_number", "email"]


class AccountStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "phone_number", "is_banned", "email"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ["user"]


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        exclude = ["user", "id"]
