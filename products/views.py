from django.db.models import Q
from django.http import QueryDict
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from permissions import BanPermission, VerificationPermission

from .models import Category, City, Product, ProductStatus
from .serializers import (
    CategorySerializer,
    CitySerializer,
    ExplicitProductSerializer,
    NewProductSerializer,
    ProductStatusSerializer,
    ProfileProductSerializer,
    UpdateProfileProductSerializer,
)

# FIELDS1 = ["name", "description", "product_status"]
FIELDS1 = ["name", "description", "image", "product_status", "pages"]

FIELDS2 = ["process_info", "address", "category", "university_info"]


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def ListAllProducts(request):
    querysetFeatured = Product.objects.filter(
        is_pending=False, buyer=None, is_featured=True
    ).order_by(
        "-created_at",
    )[:10]
    querysetFree = Product.objects.filter(
        is_pending=False, buyer=None, process_info__method="donate"
    ).order_by(
        "-created_at",
    )[:10]

    querysetPaid = Product.objects.filter(
        is_pending=False, buyer=None, process_info__method="sell"
    ).order_by(
        "-created_at",
    )[:10]

    querysetLend = Product.objects.filter(
        is_pending=False, buyer=None, process_info__method="lend"
    ).order_by(
        "-created_at",
    )[:10]
    ser1 = ExplicitProductSerializer(querysetFeatured, many=True)
    ser2 = ExplicitProductSerializer(querysetFree, many=True)
    ser3 = ExplicitProductSerializer(querysetPaid, many=True)
    ser4 = ExplicitProductSerializer(querysetLend, many=True)

    return Response(
        {"featured": ser1.data, "free": ser2.data, "paid": ser3.data, "lend": ser4.data}
    )


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def fetchSingleProduct(request, pk):
    product = Product.objects.get(id=pk)
    same_user = product.seller.email == request.user.email
    if (product.buyer is not None) & (same_user is False):
        return Response(
            {"detail": "عذراً هذا المنتج غير متوفر."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = ExplicitProductSerializer(product)
    return Response(serializer.data)


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
        # tmp[key] = eval(data[key])
        try:
            tmp[key] = data[key]
        except KeyError:
            pass

    serializer = NewProductSerializer(data=tmp)

    if serializer.is_valid():
        obj = serializer.save()
        ser = ProfileProductSerializer(obj)

        return Response(ser.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        try:
            tmp[key] = data[key]

        except KeyError:
            pass

    product = Product.objects.get(pk=pk)
    if product.seller == request.user or request.user.is_staff:
        if product.buyer is not None:
            return Response(
                {
                    "detail": "لا يمكنك تعديل هذا المنتج.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UpdateProfileProductSerializer(product, data=tmp, partial=True)
        if serializer.is_valid():
            obj = serializer.save()

            ser = ProfileProductSerializer(obj)
            return Response(ser.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {
                "detail": "لا تملك الصلاحيات الكافية لتعديل هذا المنتج.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def deleteProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response(
            {"detail": "هذا المنتج غير متوفر."}, status=status.HTTP_404_NOT_FOUND
        )
    if not request.user.is_staff:
        if product.seller.id != request.user.id:
            return Response(
                {
                    "detail": "لا تملك الصلاحيات الكافية لإزالة هذا المنتج.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if product.buyer is not None:
            return Response(
                {
                    "detail": "لا يمكنك حذف هذا المنتج.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    product.delete()
    return Response({"detail": "تم حذف هذا المنتج بنجاح."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, BanPermission, VerificationPermission])
def buyProduct(request, pk):
    product = Product.objects.get(id=pk)
    if product.buyer is not None:
        return Response(
            {
                "detail": "تم شراء هذا المنتج مسبقاً.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if product.seller == request.user:
        return Response(
            {
                "detail": "لا يمكنك شراء منتجك.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if product.is_pending:
        return Response(
            {
                "detail": "المنتج ما زال في قائمة الانتظار.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    product.buyer = request.user
    product.save()

    ## TODO: SEND FCM NOTIFICATION

    return Response({"detail": "تم شراء المنتج بنجاح."})


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, VerificationPermission, BanPermission])
def getSettings(request):
    product_status_objects = ProductStatus.objects.all()
    product_status = ProductStatusSerializer(product_status_objects, many=True).data
    city_objects = City.objects.all()
    city = CitySerializer(city_objects, many=True).data
    category_objects = Category.objects.all()
    category = CategorySerializer(category_objects, many=True).data
    return Response(
        {"categories": category, "cities": city, "product_status": product_status}
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, VerificationPermission, BanPermission])
def filterView(request):
    data = request.data
    name = data.get("name", None)
    sub_name = data.get("sub_name", None)

    pages = data.get("pages", None)
    order_by = data.get("order_by", "-created_at")

    ## ! perhaps this is a useless filter
    description = data.get("description", None)
    category = data.get("category", None)
    is_featured = data.get("is_featured", None)

    ## * Address Info
    city = data.get("city", None)
    rest_address = data.get("rest_address", None)

    ## * University Info
    university_name = data.get("university_name", None)
    faculty = data.get("faculty", None)
    year = data.get("year", None)

    ## * Product Status
    product_status = data.get("product_status", None)

    ## * Process Info
    method = data.get("method", None)
    min_price = data.get("min_price", None)
    max_price = data.get("max_price", None)

    duration = data.get("duration", None)
    filters = Q(is_pending=False, buyer=None)
    if is_featured:
        filters &= Q(is_featured=is_featured)
    if name:
        filters &= Q(name__icontains=name)
    if description:
        filters &= Q(description__icontains=description)
    if pages:
        filters &= Q(pages=pages)
    if rest_address:
        filters &= Q(address__rest__icontains=rest_address)

    if university_name:
        filters &= Q(university_info__name__icontains=university_name)
    if year:
        filters &= Q(university_info__year=year)
    if faculty:
        filters &= Q(university_info__faculty__icontains=faculty)

    if duration:
        filters &= Q(process_info__duration__icontains=duration)
    if min_price is not None:
        filters &= Q(process_info__price__gte=min_price)
    if max_price is not None:
        filters &= Q(process_info__price__lte=max_price)
    if city is not None:
        filters &= Q(address__city=city)

    if sub_name is not None:
        filters &= Q(name__icontains=sub_name)

    products = Product.objects.filter(filters) if filters else Product.objects.none()

    if category:
        for cat in category:
            products = products.filter(category=cat)

    filters = Q()
    if method:
        for met in method:
            filters |= Q(process_info__method=met)
        products = products.filter(filters) if filters else Product.objects.none()
        filters = Q()

    if product_status:
        for stat in product_status:
            filters |= Q(product_status=stat)

        products = products.filter(filters) if filters else Product.objects.none()

    if order_by == "d_price":
        order_by = "-process_info__price"
    if order_by == "a_price":
        order_by = "process_info__price"
    if order_by == "a_created_at":
        order_by = "created_at"
    if order_by == "d_created_at":
        order_by = "-created_at"
    if order_by == "d_name":
        order_by = "-name"
    if order_by == "a_name":
        order_by = "name"

    products = products.order_by(order_by)

    paginator = PageNumberPagination()

    results = paginator.paginate_queryset(
        products,
        request,
    )
    res = paginator.get_paginated_response(
        ExplicitProductSerializer(results, many=True).data,
    )
    return res


## ! Only Staff Users.


@api_view()
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def approveProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        if not product.is_pending:
            return Response(
                {"detail": "تم قبول هذا المنتج مسبقاً."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.is_pending = False
        product.save()

        ## TODO: SEND FCM NOTIFICATION

        return Response({"detail": "تم قبول المنتج بنجاح."})

    except Product.DoesNotExist:
        return Response(
            {"detail": "هذا المنتج غير موجود."}, status=status.HTTP_404_NOT_FOUND
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
    queryset = Product.objects.filter(
        is_pending=False,
    ).order_by("-created_at")
    serializer_class = ProfileProductSerializer
    pagination_class = PageNumberPagination


class ListStaffPendingProducts(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        BanPermission,
        VerificationPermission,
        IsAdminUser,
    ]
    queryset = Product.objects.filter(
        is_pending=True,
    ).order_by("-created_at")
    pagination_class = PageNumberPagination

    serializer_class = ProfileProductSerializer
