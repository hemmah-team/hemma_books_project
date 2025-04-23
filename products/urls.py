from django.urls import path

from .views import createNewProduct, listAllProducts

urlpatterns = [path("list/", listAllProducts), path("create/", createNewProduct)]
