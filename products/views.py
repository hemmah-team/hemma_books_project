from django.http import QueryDict
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product
from .serializers import NewProductSerializer, ProductSerializer

FIELDS1 = ["name", "description", "image", "product_status"]
FIELDS2 = ["process_info", "address", "category", "university_info"]


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listAllProducts(request):
    products = Product.objects.filter(is_pending=False)
    ser = ProductSerializer(products, many=True)
    return Response(ser.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def editProduct(request, pk):
    data: QueryDict = request.data
    tmp = {}

    for key in FIELDS1:
        if data.get(key, None):
            tmp[key] = data[key]

    for key in FIELDS2:
        if data.get(key, None):
            tmp[key] = eval(data[key])

    tmp["seller"] = request.user.id

    product = Product.objects.get(pk=pk)
    if product.seller == request.user:
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
@permission_classes([IsAuthenticated])
def deleteProduct(request, pk):
    product = Product.objects.get(id=pk)
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
    return Response("deleted su")
