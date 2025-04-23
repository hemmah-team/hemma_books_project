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

from .serializers import RegisterSerizalizer


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
                "message": "All Fields Must Be Entered.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = User.objects.get(phone_number=phone, password=password)
        if user.is_active is False:
            return Response(
                {
                    "message": "You Need To Verify The OTP At First.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if user.is_banned is True:
            return Response(
                {
                    "message": "Your Account Is Banned.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token = Token.objects.get(user=user)
        return Response({"name": user.name, "token": str(token)})
    except:
        return Response(
            {
                "message": "Credentials Are Invalid.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def changeNumberView(request):
    new_phone_number = request.data["phone_number"]
    user = User.objects.update(phone_number=request.user.phone_number)
    # user.update(phone_number=new_phone_number)

    return Response(str(new_phone_number))
