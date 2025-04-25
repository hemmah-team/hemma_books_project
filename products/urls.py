from django.urls import path

from .views import (
    ListAllProducts,
    ListStaffProducts,
    approveProduct,
    buyProduct,
    createCategory,
    createNewProduct,
    deleteProduct,
    editProduct,
)

urlpatterns = [
    path("list/", ListAllProducts.as_view()),
    path("create/", createNewProduct),
    path("edit/<int:pk>/", editProduct),
    path("delete/<int:pk>/", deleteProduct),
    path("buy/<int:pk>", buyProduct),
    ## ! FOR STAFF ONLY.
    path("approve/<int:pk>", approveProduct),
    path("create_category/", createCategory),
    path("list_products_staff/", ListStaffProducts.as_view()),
]
