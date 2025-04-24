from django.urls import path

from .views import (
    blockUserView,
    changeNumberView,
    changePasswordView,
    fetchProfileView,
    listAllUsersView,
    loginView,
    registerView,
)

urlpatterns = [
    path("register/", registerView),
    path("login/", loginView),
    path("change_number/", changeNumberView),
    path("change_password/", changePasswordView),
    path("my_profile/", fetchProfileView),
    path("list_users/", listAllUsersView),
    path("block/<int:pk>/", blockUserView),
]
