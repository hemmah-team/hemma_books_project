from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import User
from permissions import BanPermission, VerificationPermission
from products.models import Product
from products.serializers import ProfileProductSerializer

from .serializers import AccountSerializer, RegisterSerizalizer


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
        return Response(serializer.errors)


@api_view(["POST"])
def loginView(request):
    try:
        phone = request.data["phone_number"]
        password = request.data["password"]
    except:
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
                {"details": "Credentials Are Invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_active is False:
            return Response(
                {
                    "detail": "You Need To Verify The OTP At First.",
                },
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
        return Response({"name": user.name, "token": str(token)})
    except:
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
    serializer2 = ProfileProductSerializer(products, many=True)
    tmp["products"] = serializer2.data

    return Response(tmp)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def changeNumberView(request):
    new_phone_number = request.data["phone_number"]
    user = User.objects.filter(id=request.user.id)
    user.update(phone_number=new_phone_number)

    return Response(AccountSerializer(User.objects.get(id=request.user.id)).data)


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
