import datetime
import random

from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from permissions import BanPermission, VerificationPermission
from products.models import Product
from products.serializers import ProfileProductSerializer

from .models import Notification, Otp, User
from .serializers import (
    AccountSerializer,
    AccountStaffSerializer,
    NotificationSerializer,
    RegisterSerizalizer,
)


@api_view(["POST"])
def resetPasswordView(request):
    phone_number = request.data["phone_number"]
    try:
        user = User.objects.get(phone_number=phone_number)
        return sendOtp(user)

    except User.DoesNotExist:
        return Response(
            {"detail": "This Phone Number Is Not Registered."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view()
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def sendOtpView(request):
    user = request.user
    return sendOtp(user)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def verifyOtpView(request):
    try:
        user = request.user
        print(f"user is {user}")
    except:
        user = User.objects.get(phone_number=request.data["phone_number"])

    request_type = request.data["type"]
    code = request.data["code"]
    try:
        otp_object = Otp.objects.get(user=user)
        is_same = otp_object.code == code
        if is_same:
            user_ob = User.objects.get(id=user.id)
            res = {}
            ## here either reset password or verify account
            if request_type == "verify":
                user_ob.is_verified = True
                res["message"] = "The Account Has Been Verified Successfully."
            if request_type == "reset":
                user_ob.set_password(request.data["new_password"])
                res["message"] = "You Have Reset The Password Successfully."

            user_ob.save()
            otp_object.delete()
            return Response(res)

        else:
            return Response(
                {"detail": "The OTP Code Is Wrong."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except Otp.DoesNotExist:
        return Response(
            {"detail": "Send An OTP First."}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
def registerView(request):
    serializer = RegisterSerizalizer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        tmp = serializer.data

        tmp["token"] = token.key

        return Response(tmp)
    else:
        return Response(
            {
                "detail": "This Phone Number Already Exists.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def loginView(request):
    try:
        phone = request.data["phone_number"]
        password = request.data["password"]
    except KeyError:
        return Response(
            {
                "detail": "All Fields Must Be Entered.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = User.objects.get(phone_number=phone)
        isCorrect = user.check_password(password)
        if not isCorrect:
            return Response(
                {"detail": "Credentials Are Invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_banned is True:
            return Response(
                {
                    "detail": "Your Account Is Banned.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token = Token.objects.get(user=user)
        return Response(
            {"name": user.name, "token": str(token), "is_verified": user.is_verified}
        )
    except User.DoesNotExist:
        return Response(
            {
                "detail": "Credentials Are Invalid.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchProfileView(request):
    tmp = {}
    user = request.user
    serializer1 = AccountSerializer(user)
    tmp["profile"] = serializer1.data
    products = Product.objects.filter(Q(seller=user) | Q(buyer=user))
    serializer2 = ProfileProductSerializer(
        products,
        many=True,
    )
    tmp["products"] = serializer2.data

    return Response(tmp)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def changeNumberView(request):
    new_phone_number = request.data["phone_number"]
    password = request.data["password"]
    user = User.objects.get(id=request.user.id)
    if user.check_password(password):
        user.phone_number = new_phone_number
        user.save()

        return Response(AccountSerializer(User.objects.get(id=request.user.id)).data)
    else:
        return Response(
            {"detail": "The Password Is Incorrect."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def changePasswordView(request):
    old_password = request.data["old_password"]
    new_password = request.data["new_password"]

    user = User.objects.get(id=request.user.id)

    if old_password == new_password:
        return Response(
            {"detail": "The New Password Can't Be The Same As The Old One."},
            status=status.HTTP_403_FORBIDDEN,
        )
    if user.check_password(old_password):
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password Is Changed Successfully."})
    else:
        return Response(
            {"detail": "The Old Password Is Incorrect."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchNotificationsView(request):
    user = request.user
    notifications = Notification.objects.filter(Q(user=None) | Q(user=user)).order_by(
        "-id"
    )
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


## ! Only Staff Users.


class listAllUsersView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAdminUser,
    ]
    queryset = User.objects.filter(is_verified=True, is_staff=False)

    serializer_class = AccountStaffSerializer


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggleUserBlockView(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.is_banned = not user.is_banned
        user.save()
        if user.is_banned:
            return Response({"detail": "User Has Been Banned Successfully."})
        else:
            return Response({"detail": "User Has Been Unbanned Successfully."})
    except User.DoesNotExist:
        return Response(
            {"detail": "User Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def sendPublicNotificationView(request):
    ## TODO: SEND TOPIC NOTIFICATION
    pass


def sendOtp(user):
    try:
        otp = Otp.objects.get(user=user)

        otp_date = datetime.datetime(
            year=otp.created_at.year,
            month=otp.created_at.month,
            day=otp.created_at.day,
            hour=otp.created_at.hour + 3,
            minute=otp.created_at.minute,
            second=otp.created_at.second,
        )
        time_delta = datetime.datetime.now() - otp_date
        if time_delta.total_seconds() > 120:
            otp.delete()
            random_otp = str(random.randint(0, 99999)).zfill(5)
            Otp.objects.create(code=random_otp, user=user)
            ## ! send actual otp here
            return Response({"message": "Sent OTP Successfully."})
        else:
            return Response(
                {
                    "detail": "You Have To Wait 2 Minutes Before Sending Another OTP.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
    except Otp.DoesNotExist:
        random_otp = str(random.randint(0, 99999)).zfill(5)
        Otp.objects.create(code=random_otp, user=user)
        return Response({"detail": "Sent OTP Successfully."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggleIsFeaturedView(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.is_featured = not product.is_featured
        product.save()
        if product.is_featured:
            return Response(
                {"detail": "Product Has Been Added To Featured Successfully."}
            )
        else:
            return Response(
                {"detail": "Product Has Been Removed From Featured Successfully."}
            )
    except Product.DoesNotExist:
        return Response(
            {"detail": "Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
        )
