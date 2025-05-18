from django.urls import path

from .views import (
    changeNameView,
    changeNumberView,
    changePasswordOrResetView,
    checkEmailExistence,
    checkNewEmailExistence,
    fetchMyProducts,
    fetchNotificationsView,
    fetchProfileView,
    listAllUsersView,
    loginView,
    registerView,
    sendOtpView,
    sendPublicNotificationView,
    toggleIsFeaturedView,
    toggleUserBlockView,
    verifyOtpView,
)

urlpatterns = [
    path("register/", registerView),
    path("login/", loginView),
    path("check_phone_number/", checkEmailExistence),
    path("check_new_phone_number/", checkNewEmailExistence),
    path("change_name/", changeNameView),
    path("send_otp/", sendOtpView),
    path("verify_otp/", verifyOtpView),
    path("change_number/", changeNumberView),
    path("change_password/", changePasswordOrResetView),
    path("my_products/", fetchMyProducts),
    path("notifications/", fetchNotificationsView),
    path("profile/", fetchProfileView),
    ## ! FOR STAFF ONLY.
    path("send_notification/", sendPublicNotificationView),
    path("list_users/", listAllUsersView.as_view()),
    path("toggle_block/<int:pk>/", toggleUserBlockView),
    path("toggle_featured/<int:pk>/", toggleIsFeaturedView),
]
