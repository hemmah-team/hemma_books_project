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
        return self.rest


class UniversityInfo(models.Model):
    product = models.OneToOneField(
        "Product", on_delete=models.CASCADE, related_name="university_info"
    )

    name = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)
    year = models.IntegerField()

    def __str__(self):
        return self.name


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
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="product_buyer",
    )

    category = models.ManyToManyField(
        Category, related_name="products", null=True, blank=True
    )

    name = models.CharField(max_length=150)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="media")
    is_pending = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class AppVersion(models.Model):
    version = models.CharField(max_length=40)
    link = models.CharField(max_length=250)


class ProcessInfo(models.Model):
    method = models.CharField(max_length=15)
    price = models.IntegerField(null=True, blank=True)
    duration = models.CharField(null=True, blank=True, max_length=30)
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="process_info"
    )

    def __str__(self):
        return self.method
