from django.urls import path

from .views import (
    changeNumberView,
    changePasswordView,
    fetchNotificationsView,
    fetchProfileView,
    listAllUsersView,
    loginView,
    registerView,
    resetPasswordView,
    sendOtpView,
    sendPublicNotificationView,
    toggleIsFeaturedView,
    toggleUserBlockView,
    verifyOtpView,
)

urlpatterns = [
    path("register/", registerView),
    path("reset_password/", resetPasswordView),
    path("send_otp/", sendOtpView),
    path("verify_otp/", verifyOtpView),
    path("login/", loginView),
    path("change_number/", changeNumberView),
    path("change_password/", changePasswordView),
    path("my_profile/", fetchProfileView),
    path("list_users/", listAllUsersView.as_view()),
    path("toggle_block/<int:pk>/", toggleUserBlockView),
    path("toggle_featured/<int:pk>/", toggleIsFeaturedView),
    path("send_notification/", sendPublicNotificationView),
    path("notifications/", fetchNotificationsView),
]
