from rest_framework import serializers

from .models import (
    Address,
    Category,
    City,
    ProcessInfo,
    Product,
    ProductStatus,
    UniversityInfo,
)


class UniversityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityInfo
        exclude = ["id", "product"]


class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        exclude = [
            "id",
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Address
        exclude = [
            "id",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProcessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessInfo
        exclude = ["id", "product"]


class ProductSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer()

    category = CategorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "image",
            "product_status",
            "category",
            "created_at",
            "updated_at",
            "product_status",
            "category",
            "address",
            "process_info",
            "university_info",
        ]


class NewProductSerializer(serializers.ModelSerializer):
    university_info = UniversityInfoSerializer(
        required=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "product_status",
            "seller",
            "category",
            "name",
            "description",
            "image",
            "created_at",
            "updated_at",
            "university_info",
        ]
        extra_kwargs = {"seller": {"write_only": True}}

    def create(self, validated_data):
        university_info_data = validated_data.pop("university_info")
        product = Product.objects.create(**validated_data)
        UniversityInfo.objects.create(product=product, **university_info_data)
        return product
