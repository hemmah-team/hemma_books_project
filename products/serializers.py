from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from account.serializers import AccountSerializer

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
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"
        extra_kwargs = {"name": {"read_only": True}}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["id", "product"]


class ExplicitAddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Address
        exclude = ["id", "product"]


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
            "address",
            "process_info",
            "university_info",
            "is_featured",
            "pages",
        ]

    def update(self, instance, validated_data):
        process_info_data = validated_data.pop("process_info", None)
        university_info_data = validated_data.pop("university_info", None)
        address_data = validated_data.pop("address", None)
        instance.pages = validated_data.get("pages", instance.pages)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.product_status = validated_data.get(
            "product_status", instance.product_status
        )

        if process_info_data:
            ProcessInfo.objects.filter(product=instance.id).update(**process_info_data)

        if university_info_data:
            UniversityInfo.objects.filter(product=instance.id).update(
                **university_info_data
            )

        if address_data:
            Address.objects.filter(product=instance.id).update(**address_data)

        return instance


class ExplicitProductSerializer(serializers.ModelSerializer):
    address = ExplicitAddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer()
    category = CategorySerializer(many=True)
    product_status = ProductStatusSerializer()

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
            "address",
            "process_info",
            "university_info",
            "is_featured",
            "pages",
        ]


class ProfileProductSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer()
    seller = AccountSerializer()
    buyer = AccountSerializer()

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
            "is_pending",
            "process_info",
            "university_info",
            "seller",
            "buyer",
            "pages",
        ]


class NewProductSerializer(serializers.ModelSerializer):
    university_info = UniversityInfoSerializer(
        required=True,
    )
    process_info = ProcessInfoSerializer(required=True)
    address = AddressSerializer(required=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "product_status",
            "seller",
            "category",
            "process_info",
            "name",
            "description",
            "image",
            "created_at",
            "updated_at",
            "university_info",
            "address",
            "pages",
        ]
        extra_kwargs = {"seller": {"write_only": True}}

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        university_info_data = validated_data.pop("university_info")
        process_info_data = validated_data.pop("process_info")
        address_data = validated_data.pop("address")
        category_ids = validated_data.pop("category")
        product = Product.objects.create(**validated_data)

        product.category.add(*category_ids)

        UniversityInfo.objects.create(product=product, **university_info_data)
        ProcessInfo.objects.create(product=product, **process_info_data)
        Address.objects.create(
            product=product,
            city=address_data["city"],
            rest=address_data["rest"],
        )

        return product
