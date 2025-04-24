from django.urls import path

from .views import (
    changeNumberView,
    changePasswordView,
    fetchProfileView,
    loginView,
    registerView,
)

urlpatterns = [
    path("register/", registerView),
    path("login/", loginView),
    path("change_number/", changeNumberView),
    path("change_password/", changePasswordView),
    path("my_profile/", fetchProfileView),
]
