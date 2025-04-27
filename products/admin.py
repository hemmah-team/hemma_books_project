from django.contrib import admin

# from .models import City
from .models import (
    Address,
    AppVersion,
    Category,
    City,
    ProcessInfo,
    Product,
    ProductStatus,
    UniversityInfo,
)

# Register your models here.
admin.site.register(City)
admin.site.register(Address)

admin.site.register(ProcessInfo)
admin.site.register(UniversityInfo)
admin.site.register(ProductStatus)
admin.site.register(Product)
admin.site.register(AppVersion)
admin.site.register(Category)
