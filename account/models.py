from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        name,
        password,
        phone_number,
        fcm,
        is_verified,
        is_banned,
        is_staff=False,
        is_superuser=False,
    ) -> "User":
        if not email:
            raise ValueError("The Email Can't Be Empty.")
        if not name:
            raise ValueError("The Name Can't Be Empty.")

        if not phone_number:
            raise ValueError("The Phone Number Can't Be Empty.")

        if not password:
            raise ValueError("The Password Can't Be Empty.")

        user = self.model(email=email)
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
        email,
        name,
        password,
        phone_number,
        fcm,
        is_verified,
        is_banned,
    ) -> "User":
        user = self.create_user(
            email=email,
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
    email = models.EmailField(
        unique=True,
    )
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10, unique=True)
    fcm = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    username = None
    first_name = None
    last_name = None
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "phone_number",
        "name",
        "password",
        "fcm",
        "is_verified",
        "is_banned",
    ]

    def __str__(self):
        return self.email


class Otp(models.Model):
    code = models.CharField(max_length=5)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Notification(models.Model):
    title = models.CharField(max_length=30)
    message = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title
