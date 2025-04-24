from django.urls import path

from .views import createNewProduct, deleteProduct, editProduct, listAllProducts

urlpatterns = [
    path("list/", listAllProducts),
    path("create/", createNewProduct),
    path("edit/<int:pk>/", editProduct),
    path("delete/<int:pk>/", deleteProduct),
]
