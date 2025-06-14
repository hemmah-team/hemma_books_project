from django.db import models

from account.models import User


class City(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    rest = models.CharField(max_length=150)
    product = models.OneToOneField(
        "Product", on_delete=models.CASCADE, related_name="address"
    )

    def __str__(self):
        return self.rest + " - " + str(self.product.id)


class UniversityInfo(models.Model):
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name="university_info",
    )

    name = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)
    year = models.IntegerField()

    def __str__(self):
        return self.name + " - " + str(self.product.id)


class ProductStatus(models.Model):
    status = models.CharField(max_length=30)

    def __str__(self):
        return self.status


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_status = models.ForeignKey(ProductStatus, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_buyer",
    )

    category = models.ManyToManyField(
        Category,
        related_name="products",
    )

    name = models.CharField(max_length=150)
    description = models.CharField(max_length=200)
    pages = models.IntegerField()
    image = models.ImageField(upload_to="media", name="")
    is_pending = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    got_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id) + " - " + self.name


class AppVersion(models.Model):
    version = models.CharField(max_length=40)
    link = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.version


class ProcessInfo(models.Model):
    method = models.CharField(max_length=15)
    price = models.IntegerField(null=True, blank=True)
    duration = models.CharField(null=True, blank=True, max_length=30)
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="process_info"
    )

    def __str__(self):
        return self.method + " - " + str(self.product.id)
