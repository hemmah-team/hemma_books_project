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
def sendOtpView(request):
    ## new phone number
    phone_number = request.data.get("phone_number", None)

    if phone_number is not None:
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            ## get from headers
            token = Token.objects.get(key=request.headers["Authorization"][6:])
            user = token.user

    else:
        return Response(
            {"detail": "يجب إرسال رقم الهاتف."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        otp = Otp.objects.get(user=user)
        otp_date = datetime.datetime(
            year=otp.created_at.year,
            month=otp.created_at.month,
            day=otp.created_at.day,
            hour=otp.created_at.hour,
            minute=otp.created_at.minute,
            second=otp.created_at.second,
        )

        time_delta = datetime.datetime.now() - otp_date
        if time_delta.total_seconds() > 120:
            otp.delete()
            random_otp = str(random.randint(0, 99999)).zfill(5)
            Otp.objects.create(code=random_otp, user=user)
            ## ! send actual otp here
            ## !!!!!!!!!!  send always to new phone number
            ##### !!!!!!!!!!! to this (phone_number)
            return Response({"detail": "تم إرسال رمز التحقق بنجاح."})
        else:
            return Response(
                {
                    "detail": "يجب عليك أن تنتظر دقيقتين قبل إرسال رمز تحقق آخر.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
    except Otp.DoesNotExist:
        random_otp = str(random.randint(0, 99999)).zfill(5)
        Otp.objects.create(code=random_otp, user=user)
        return Response({"detail": "تم إرسال رمز التحقق بنجاح."})


@api_view(["POST"])
def checkEmailExistence(request):
    try:
        email = request.data["email"]
        user = User.objects.get(email=email)
        if user:
            return Response()
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def changeNameView(request):
    name = request.data["name"]
    email = request.data["email"]
    password = request.data["password"]

    try:
        user = User.objects.get(
            email=email,
        )

        if user.check_password(password):
            user.name = name
            user.save()
            return Response({"detail": "تم تغيير الاسم بنجاح."})
        else:
            return Response(
                {"detail": "كلمة المرور خاطئة."}, status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {"detail": "رقم الهاتف غير مسجل مسبقاً."},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def checkNewEmailExistence(request):
    new_email = request.data["new_email"]
    old_email = request.data["old_email"]
    password = request.data["password"]

    try:
        user = User.objects.get(email=old_email)
        if user.check_password(password):
            try:
                user = User.objects.get(email=new_email)
                return Response(
                    {"detail": "الإيميل مستخدم مسبقاً."},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            except User.DoesNotExist:
                return Response()
        else:
            return Response(
                {"detail": "كلمة المرور خاطئة."}, status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {"detail": "الإيميل غير موجود."}, status=status.HTTP_403_FORBIDDEN
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def verifyOtpView(request):
    request_type = request.data["type"]
    code = request.data["code"]
    email = request.data["email"]
    # if request.auth is not None & request_type == "change_number":
    #     print("dsjsdosdksjdsdjsd")
    #     pass
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = Token.objects.get(key=request.headers["Authorization"][6:]).user

    try:
        otp_object = Otp.objects.get(user=user)
        is_same = otp_object.code == code
        if is_same:
            user_ob = User.objects.get(id=user.id)
            res = {}
            ## here either reset password or verify account
            if request_type == "verify":
                user_ob.is_verified = True
                res["detail"] = "تم تفعيل هذا الحساب بنجاح."
                user_ob.save()
                otp_object.delete()
            if request_type == "reset":
                res["detail"] = "رمز التحقق صحيح."

            if request_type == "change_number":
                user_ob.email = email
                res["detail"] = "تم تغيير الإيميل بنجاح."
                user_ob.save()
                otp_object.delete()

            return Response(res)

        else:
            return Response(
                {"detail": "رمز التحقق خاطئ."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except Otp.DoesNotExist:
        return Response(
            {"detail": "أرسل رمز التحقق أولاً."}, status=status.HTTP_401_UNAUTHORIZED
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
                "detail": "هذا الإيميل مسجّل مسبقاً.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def loginView(request):
    try:
        email = request.data["email"]
        password = request.data["password"]
    except KeyError:
        return Response(
            {
                "detail": "يجب إدخال جميع البيانات.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = User.objects.get(email=email)
        isCorrect = user.check_password(password)
        if not isCorrect:
            return Response(
                {"detail": "البيانات خاطئة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_banned is True:
            return Response(
                {
                    "detail": "حسابك محظور.",
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
                "detail": "البيانات خاطئة.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchMyProducts(request):
    products = Product.objects.filter(Q(seller=request.user) | Q(buyer=request.user))
    serializer = ProfileProductSerializer(
        products,
        many=True,
    )

    return Response(serializer.data)


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchProfileView(request):
    user = request.user
    serializer1 = AccountSerializer(user)

    return Response(serializer1.data)


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
            {"detail": "كلمة المرور خاطئة."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def changePasswordOrResetView(request):
    ## ! only for change password
    old_password = request.data.get("old_password", None)
    ## ! only for resetting password
    code = request.data.get("code", None)
    ## ! common for both cases
    new_password = request.data["new_password"]
    email = request.data["email"]
    try:
        user = User.objects.get(email=email)

        ## changing password
        if old_password is not None:
            if old_password == new_password:
                return Response(
                    {"detail": "لا يمكن أن إدخال نفس كلمة المرور مرتين."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"detail": "تم تغيير كلمة المرور بنجاح."})
            else:
                return Response(
                    {"detail": "كلمة المرور القديمة خاطئة."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        ## resetting password
        elif code is not None:
            ## check if code is correct first
            try:
                otp = Otp.objects.get(code=code, user=user)
                otp.delete()
                user.set_password(new_password)
                user.save()
                return Response({"detail": "تم إعادة تعيين كلمة المرور بنجاح."})
            except Otp.DoesNotExist:
                return Response(
                    {
                        "detail": "رمز التحقق خاطئ.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

    except User.DoesNotExist:
        return Response(
            {"detail": "الإيميل غير مسجل مسبقاً"}, status=status.HTTP_403_FORBIDDEN
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
            return Response({"detail": "تم حظر المستخدم بنجاح."})
        else:
            return Response({"detail": "تم فك الحظر عن المستخدم بنجاح."})
    except User.DoesNotExist:
        return Response(
            {"detail": "المستخدم غير موجود."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def sendPublicNotificationView(request):
    ## TODO: SEND TOPIC NOTIFICATION
    pass


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggleIsFeaturedView(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.is_featured = not product.is_featured
        product.save()
        if product.is_featured:
            return Response({"detail": "تم إضافة المنتج إلى القائمة المميزة بنجاح."})
        else:
            return Response({"detail": "تم إزالة المنتج عن القائمة المميزة بنجاح."})
    except Product.DoesNotExist:
        return Response(
            {"detail": "هذا المنتج غير موجود."}, status=status.HTTP_404_NOT_FOUND
        )
