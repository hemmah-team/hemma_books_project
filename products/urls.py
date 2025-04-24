from django.urls import path

from .views import (
    buyProduct,
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
]
