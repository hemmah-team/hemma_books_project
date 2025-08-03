from django.urls import path

from .views import (
    ListAllProducts,
    ListStaffPendingProducts,
    ListStaffProducts,
    approveProduct,
    createCategory,
    createNewProduct,
    deleteProduct,
    editProduct,
    fetchFavourites,
    fetchSingleProduct,
    filterView,
    getInitital,
)

urlpatterns = [
    path("get_initial/", getInitital),
    path("<int:pk>/", fetchSingleProduct),
    path("list/", ListAllProducts),
    path("list_favourites/", fetchFavourites),
    path("create/", createNewProduct),
    path("edit/<int:pk>/", editProduct),
    path("delete/<int:pk>/", deleteProduct),
    path("filter/", filterView),
    ## ! FOR STAFF ONLY.
    path("approve/<int:pk>/", approveProduct),
    path("create_category/", createCategory),
    path("list_products_staff/", ListStaffProducts.as_view()),
    path("list_pending_products/", ListStaffPendingProducts.as_view()),
]
