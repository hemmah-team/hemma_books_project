from django.urls import path

from .views import (
    FetchSingleProduct,
    ListAllProducts,
    ListStaffPendingProducts,
    ListStaffProducts,
    approveProduct,
    buyProduct,
    createCategory,
    createNewProduct,
    deleteProduct,
    editProduct,
    filterView,
    getSettings,
)

urlpatterns = [
    path("list_settings/", getSettings),
    path("<int:pk>/", FetchSingleProduct.as_view()),
    path("list/", ListAllProducts.as_view()),
    path("create/", createNewProduct),
    path("edit/<int:pk>/", editProduct),
    path("delete/<int:pk>/", deleteProduct),
    path("buy/<int:pk>/", buyProduct),
    path("filter/", filterView),
    ## ! FOR STAFF ONLY.
    path("approve/<int:pk>/", approveProduct),
    path("create_category/", createCategory),
    path("list_products_staff/", ListStaffProducts.as_view()),
    path("list_pending_products/", ListStaffPendingProducts.as_view()),
]
