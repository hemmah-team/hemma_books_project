from django.urls import path

from .views import (
    changeNumberView,
    changePasswordView,
    fetchProfileView,
    listAllUsersView,
    loginView,
    registerView,
    sendNotificationView,
    toggleUserView,
)

urlpatterns = [
    path("register/", registerView),
    path("login/", loginView),
    path("change_number/", changeNumberView),
    path("change_password/", changePasswordView),
    path("my_profile/", fetchProfileView),
    path("list_users/", listAllUsersView.as_view()),
    path("toggle_block/<int:pk>/", toggleUserView),
    path("send_notification/", sendNotificationView),
]
