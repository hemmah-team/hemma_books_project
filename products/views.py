from django.http import QueryDict
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

    tmp["name"] = data["name"]
    tmp["description"] = data["description"]
    tmp["image"] = data["image"]
    tmp["seller"] = request.user.id
    tmp["product_status"] = data["product_status"]
    tmp["process_info"] = eval(data["process_info"])
    tmp["address"] = eval(data["address"])
    tmp["category"] = eval(data["category"])
    tmp["university_info"] = eval(data["university_info"])

    serializer = NewProductSerializer(data=tmp)

    if serializer.is_valid():
        serializer.save()
        data = serializer.data

        return Response(data)
    else:
        return Response(serializer.errors)
