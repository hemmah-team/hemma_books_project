from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        name,
        password,
        phone_number,
        fcm,
        is_verified,
        is_banned,
        is_staff=False,
        is_superuser=False,
    ) -> "User":
        if not name:
            raise ValueError("The Name Can't Be Empty.")

        if not phone_number:
            raise ValueError("The Phone Number Can't Be Empty.")

        if not password:
            raise ValueError("The Password Can't Be Empty.")

        user = self.model(phone_number=phone_number)
        user.name = name
        user.phone_number = phone_number
        user.fcm = fcm
        user.is_active = is_verified
        user.is_banned = is_banned
        user.is_staff = is_staff
        user.is_superuser = is_superuser

        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        name,
        password,
        phone_number,
        fcm,
        is_verified,
        is_banned,
    ) -> "User":
        user = self.create_user(
            fcm=fcm,
            is_verified=is_verified,
            is_banned=is_banned,
            is_staff=True,
            is_superuser=True,
            name=name,
            password=password,
            phone_number=phone_number,
        )
        return user

    def update(self, **kwargs):
        return super().update(**kwargs)


class User(AbstractUser):
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10, unique=True)
    fcm = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    email = None
    username = None
    first_name = None
    last_name = None
    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = [
        "name",
        "password",
        "fcm",
        "is_verified",
        "is_banned",
    ]

    def __str__(self):
        return self.name


class Otp(models.Model):
    code = models.CharField(max_length=5)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.code
