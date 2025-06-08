from rest_framework import serializers

from .models import Fcm, Notification, NotificationSetting, User


class RegisterSerizalizer(serializers.ModelSerializer):
    fcm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "name", "password", "phone_number", "fcm"]
        extra_kwargs = {"password": {"write_only": True}, "fcm": {"write_only": True}}

    def create(self, validated_data):
        fcm = validated_data.pop("fcm")
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        try:
            Fcm.objects.filter(token=fcm).delete()
        except Fcm.DoesNotExist:
            pass
        finally:
            Fcm.objects.create(user=user, token=fcm)
        return user


class AccountSerializer(serializers.ModelSerializer):
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
