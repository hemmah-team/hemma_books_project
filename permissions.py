from rest_framework.permissions import BasePermission


class VerificationPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_verified

    message = "You Are Not Verified."


class BanPermission(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_banned

    message = "You Are Banned."
