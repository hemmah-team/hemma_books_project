from django.http import QueryDict
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from permissions import BanPermission, VerificationPermission

from .models import Product
from .serializers import (
    CategorySerializer,
    NewProductSerializer,
    ProductSerializer,
    ProfileProductSerializer,
)

FIELDS1 = ["name", "description", "image", "product_status"]
FIELDS2 = ["process_info", "address", "category", "university_info"]


class ListAllProducts(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, BanPermission, VerificationPermission]
    queryset = Product.objects.filter(is_pending=False, buyer=None)

    serializer_class = ProfileProductSerializer


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def createNewProduct(request):
    data: QueryDict = request.data
    tmp = {}

    tmp["seller"] = request.user.id

    for key in FIELDS1:
        tmp[key] = data[key]

    for key in FIELDS2:
        tmp[key] = eval(data[key])

    serializer = NewProductSerializer(data=tmp)

    if serializer.is_valid():
        serializer.save()
        data = serializer.data

        return Response(data)
    else:
        return Response(serializer.errors)


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication])
@permission_classes(
    [
        IsAuthenticated,
        BanPermission,
        VerificationPermission,
    ]
)
def editProduct(request, pk):
    data: QueryDict = request.data
    tmp = {}

    for key in FIELDS1:
        if data.get(key, None):
            tmp[key] = data[key]

    for key in FIELDS2:
        if data.get(key, None):
            tmp[key] = eval(data[key])

    product = Product.objects.get(pk=pk)
    if product.seller == request.user or request.user.is_staff:
        if product.buyer is not None:
            return Response(
                {
                    "detail": "You Can't Edit This Product.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProductSerializer(product, data=tmp, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    else:
        return Response(
            {
                "detail": "You Don't Have The Permission To Edit This Product.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def deleteProduct(request, pk):
    product = Product.objects.get(id=pk)
    if not request.user.is_staff:
        if product.seller.id != request.user.id:
            return Response(
                {
                    "detail": "You Don't Have The Permission To Delete This Product.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if product.buyer is not None:
            return Response(
                {
                    "detail": "You Can't Delete This Product.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    product.delete()
    return Response({"detail": "Product Has Been Deleted Successfully."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def buyProduct(request, pk):
    product = Product.objects.get(id=pk)
    if product.buyer is not None:
        return Response(
            {
                "detail": "This Product Has Already Been Bought.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if product.seller == request.user:
        return Response(
            {
                "detail": "You Can't Buy Your Own Product.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if product.is_pending:
        return Response(
            {
                "detail": "The Product Is Still In Pending.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    product.buyer = request.user
    product.save()

    ## TODO: SEND FCM NOTIFICATION

    return Response({"detail": "Bought Successfully."})


## ! Only Staff Users.


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def approveProduct(request, pk):
    try:
        product = Product.objects.filter(id=pk)
        product.update(is_pending=False)

        ## TODO: SEND FCM NOTIFICATION

        return Response({"detail": "Approved Successfully."})

    except Product.DoesNotExist:
        return Response(
            {"detail": "The Product Does Not Exist."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def createCategory(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


class ListStaffProducts(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        BanPermission,
        VerificationPermission,
        IsAdminUser,
    ]
    queryset = Product.objects.all()

    serializer_class = ProfileProductSerializer
