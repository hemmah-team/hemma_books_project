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
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from firebase_messaging import sendPublicMessage
from permissions import BanPermission, VerificationPermission
from products.models import Product
from products.serializers import WholeProductSerializer

from .models import Fcm, Notification, NotificationSetting, Otp, User
from .serializers import (
    ALLOWED_EMAIL_DOMAINS,
    AccountSerializer,
    AccountStaffSerializer,
    NotificationSerializer,
    NotificationSettingSerializer,
    RegisterSerizalizer,
)


@api_view(["POST"])
def sendOtpView(request):
    ## new phone number
    email = request.data.get("email", None)

    if email is not None:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            ## get from headers
            token = Token.objects.get(key=request.headers["Authorization"][6:])
            user = token.user

    else:
        return Response(
            {"detail": "يرجى إدخال البريد الإلكتروني."},
            status=status.HTTP_400_BAD_REQUEST,
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
            return Response(
                {"detail": "تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح."}
            )
        else:
            return Response(
                {
                    "detail": "يرجى الانتظار دقيقتين قبل طلب رمز تحقق جديد.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
    except Otp.DoesNotExist:
        random_otp = str(random.randint(0, 99999)).zfill(5)
        Otp.objects.create(code=random_otp, user=user)
        return Response({"detail": "تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح."})


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
                {"detail": "كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except User.DoesNotExist:
        return Response(
            {"detail": "البريد الإلكتروني غير مسجّل لدينا."},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["POST"])
def changeNumberView(request):
    phone_number = request.data["phone_number"]
    email = request.data["email"]
    password = request.data["password"]

    try:
        user = User.objects.get(
            email=email,
        )
        if user.check_password(password):
            try:
                User.objects.get(phone_number=phone_number)
                return Response(
                    {"detail": "رقم الهاتف مُستخدم بالفعل."},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            except User.DoesNotExist:
                user.phone_number = phone_number
                user.save()
                return Response({"detail": "تم تحديث رقم الهاتف بنجاح."})
        else:
            return Response(
                {"detail": "كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except User.DoesNotExist:
        return Response(
            {"detail": "البريد الإلكتروني غير مسجّل لدينا."},
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
                    {"detail": "هذا البريد الإلكتروني مستخدم بالفعل."},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            except User.DoesNotExist:
                return Response()
        else:
            return Response(
                {"detail": "كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except User.DoesNotExist:
        return Response(
            {"detail": "لم يتم العثور على البريد الإلكتروني."},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def changeNotificationSettings(request):
    private = request.data["private"]
    public = request.data["public"]

    user = request.user
    try:
        NotificationSetting.objects.filter(user=user).update(
            private=private, public=public
        )

        return Response(
            {"detail": "تم تحديث إعدادات الإشعارات بنجاح."},
        )
    except:
        return Response(
            {"detail": "حدث خطأ أثناء تحديث الإعدادات."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def verifyOtpView(request):
    request_type = request.data["type"]
    code = request.data["code"]
    email = request.data["email"]
    fcm = request.data.get("fcm", None)

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

                res["detail"] = "تم تفعيل حسابك بنجاح."
                user_ob.save()

                NotificationSetting.objects.create(user=user)

                otp_object.delete()

                if fcm is not None:
                    ## here make fcm token
                    try:
                        Fcm.objects.filter(token=fcm).delete()
                    except Fcm.DoesNotExist:
                        pass
                    finally:
                        Fcm.objects.create(user=user, token=fcm)
            if request_type == "reset":
                res["detail"] = "تم التحقق من الرمز بنجاح."

            if request_type == "change_email":
                if email.split("@")[-1].lower() not in ALLOWED_EMAIL_DOMAINS:
                    return Response(
                        {"detail": "نوع البريد الإلكتروني غير مسموح به."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user_ob.email = email
                res["detail"] = "تم تحديث البريد الإلكتروني بنجاح."
                user_ob.save()
                otp_object.delete()

            return Response(res)

        else:
            return Response(
                {"detail": "رمز التحقق غير صحيح."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except Otp.DoesNotExist:
        return Response(
            {"detail": "يرجى طلب رمز تحقق أولاً."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def registerView(request):
    try:
        serializer = RegisterSerizalizer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            tmp = serializer.data

            tmp["token"] = token.key

            return Response(tmp)
        else:
            email_error = serializer.errors.get("email")
            phone_number_error = serializer.errors.get("phone_number")
            if email_error is not None:
                return Response(
                    {"detail": "هذا البريد الإلكتروني مسجّل بالفعل."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif phone_number_error is not None:
                return Response(
                    {"detail": "رقم الهاتف هذا مسجّل بالفعل."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
    except:
        return Response(
            {
                "detail": "البيانات المدخلة مسجلة مسبقاً.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def deleteAccount(request):
    user = request.user
    password = request.data["password"]
    if user.check_password(password):
        Product.objects.filter(seller=user, is_pending=True).delete()
        Product.objects.filter(seller=user, buyer=None).delete()

        user.delete()
        return Response({"detail": "تم حذف الحساب بنجاح."})
    return Response(
        {"detail": "كلمة المرور غير صحيحة."}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def loginView(request):
    try:
        email = request.data["email"]
        password = request.data["password"]
        fcm = request.data["fcm"]

    except KeyError:
        return Response(
            {
                "detail": "يرجى إدخال جميع البيانات المطلوبة.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = User.objects.get(email=email)
        isCorrect = user.check_password(password)
        if not isCorrect:
            return Response(
                {"detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_banned is True:
            return Response(
                {
                    "detail": "تم حظر حسابك. يرجى التواصل مع فريق الدعم.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token = Token.objects.get(user=user)
        ## change fcm
        ### !!!! COMMENT THIS WILL HANDLE TO VERIFICATION PART
        try:
            Fcm.objects.filter(token=fcm).delete()
        except Fcm.DoesNotExist:
            pass
        finally:
            Fcm.objects.create(user=user, token=fcm)
        try:
            notification_settings = NotificationSetting.objects.get(user=user)
            notification = NotificationSettingSerializer(notification_settings).data
        except NotificationSetting.DoesNotExist:
            pass
        return Response(
            {
                "name": user.name,
                "token": str(token),
                "is_verified": user.is_verified,
                "phone_number": user.phone_number,
                "notification_settings": notification,
            }
        )
    except User.DoesNotExist:
        return Response(
            {
                "detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchMyProducts(request):
    products = Product.objects.filter(
        Q(seller=request.user) | Q(buyer=request.user)
    ).order_by(
        "-created_at",
    )
    serializer = WholeProductSerializer(
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
@permission_classes([IsAuthenticated, VerificationPermission])
def logoutUser(request):
    user = request.user
    fcm = request.data.get("fcm")
    if fcm is None:
        return Response(
            {
                "detail": "حدث خطأ ما.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    else:
        try:
            ob = Fcm.objects.filter(token=fcm, user=user)
            ob.delete()
        except Exception:
            pass
        finally:
            return Response({"detail": "تم تسجيل الخروج بنجاح."})


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
                    {"detail": "لا يمكن استخدام نفس كلمة المرور القديمة."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"detail": "تم تحديث كلمة المرور بنجاح."})
            else:
                return Response(
                    {"detail": "كلمة المرور الحالية غير صحيحة."},
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
                        "detail": "رمز التحقق غير صحيح.",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

    except User.DoesNotExist:
        return Response(
            {"detail": "البريد الإلكتروني غير مسجّل لدينا."},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchNotificationsView(request):
    user = request.user
    notifications = (
        Notification.objects.filter(Q(user=None) | Q(user=user))
        .filter(created_at__gte=user.date_joined)
        .order_by("-created_at")
    )
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
## !!!!! Only Staff Users.                                                                                                     !!!!!
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, VerificationPermission, BanPermission])
def listAllUsersView(request):
    data = request.data
    filters = Q(is_verified=True, is_staff=False)
    name = data.get("name", None)
    if name is not None:
        filters &= Q(name__icontains=name)

    users = User.objects.filter(filters).order_by("-date_joined")

    paginator = PageNumberPagination()
    page_size_query = request.query_params.get("page_size", None)
    if page_size_query:
        paginator.page_size = page_size_query

    results = paginator.paginate_queryset(
        users,
        request,
    )
    res = paginator.get_paginated_response(
        AccountStaffSerializer(results, many=True).data,
    )
    return res


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
            return Response({"detail": "تم إلغاء حظر المستخدم بنجاح."})
    except User.DoesNotExist:
        return Response(
            {"detail": "لم يتم العثور على المستخدم."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def sendPublicNotificationView(request):
    ## TODO: SEND TOPIC NOTIFICATION
    title = request.data["title"]
    message = request.data["message"]
    sendPublicMessage(title=title, message=message)
    return Response({"detail": "تم إرسال الإشعار بنجاح."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggleIsFeaturedView(request, pk):
    try:
        product = Product.objects.get(id=pk)
        product.is_featured = not product.is_featured
        product.save()
        if product.is_featured:
            return Response({"detail": "تمت إضافة المنتج إلى القائمة المميزة بنجاح."})
        else:
            return Response({"detail": "تمت إزالة المنتج من القائمة المميزة بنجاح."})
    except Product.DoesNotExist:
        return Response(
            {"detail": "لم يتم العثور على هذا المنتج."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def loginAdminView(request):
    email = request.data["email"]
    password = request.data["password"]

    try:
        user = User.objects.get(email=email, is_staff=True)
        isCorrect = user.check_password(password)
        if not isCorrect:
            return Response(
                {"detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = Token.objects.get(user=user)

        return Response(
            {
                "name": user.name,
                "token": str(token),
                "phone_number": user.phone_number,
            }
        )
    except User.DoesNotExist:
        return Response(
            {
                "detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
