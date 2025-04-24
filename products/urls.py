from django.urls import path

from .views import (
    approveProduct,
    buyProduct,
    createCategory,
    createNewProduct,
    deleteProduct,
    editProduct,
    listAllProducts,
)

urlpatterns = [
    path("list/", listAllProducts),
    path("create/", createNewProduct),
    path("edit/<int:pk>/", editProduct),
    path("delete/<int:pk>/", deleteProduct),
    path("buy/<int:pk>", buyProduct),
    ## ! FOR STAFF ONLY.
    path("approve/<int:pk>", approveProduct),
    path("create_category/", createCategory),
]
