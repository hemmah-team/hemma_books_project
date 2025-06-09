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

### !!!!!!!!!!! START OF FIXED SERIALIZERS


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


### !!!!!!!!!!! END OF FIXED SERIALIZERS


### ?? USED FOR HOME, FAVOURITE, FILTER
class BasicProductSerializer(serializers.ModelSerializer):
    address = ExplicitAddressSerializer()
    process_info = ProcessInfoSerializer()
    category = CategorySerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "image",
            "category",
            "address",
            "process_info",
            "is_featured",
        ]


### ?? USED FOR PRODUCT SCREEN
class MiddleProductSerializer(serializers.ModelSerializer):
    address = ExplicitAddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer()
    category = CategorySerializer(many=True)
    product_status = ProductStatusSerializer()

    class Meta:
        model = Product
        exclude = ["seller", "buyer", "got_at"]


### ?? USED FOR BUY (RETURN DATA), PRODUCT SCREEN
class WholeProductSerializer(serializers.ModelSerializer):
    address = ExplicitAddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer()
    category = CategorySerializer(many=True)
    product_status = ProductStatusSerializer()
    seller = AccountSerializer()
    buyer = AccountSerializer()

    class Meta:
        model = Product
        fields = "__all__"


class UpdateProfileProductSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    process_info = ProcessInfoSerializer()
    university_info = UniversityInfoSerializer(allow_null=True)
    product_status = ProductStatusSerializer(read_only=True)
    seller = AccountSerializer()
    buyer = AccountSerializer()
    image = Base64ImageField()

    class Meta:
        model = Product
        fields = [
            "product_status",
            "address",
            "id",
            "name",
            "description",
            "image",
            "category",
            "created_at",
            "updated_at",
            "product_status",
            "process_info",
            "university_info",
            "is_featured",
            "pages",
            "seller",
            "buyer",
            "is_pending",
        ]
        extra_kwargs = {
            "is_pending": {"read_only": True},
        }

    def update(self, instance, validated_data):
        process_info_data = validated_data.pop("process_info", None)
        university_info_data = validated_data.pop("university_info", "None")
        address_data = validated_data.pop("address", None)
        category = validated_data.pop("category", None)

        instance.pages = validated_data.get("pages", instance.pages)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.image = validated_data.get("image", instance.image)
        instance.product_status = validated_data.get(
            "product_status", instance.product_status
        )
        if category is not None:
            instance.category.set(category)

        if process_info_data:
            ProcessInfo.objects.filter(product=instance.id).update(**process_info_data)

        if university_info_data is not None:
            if university_info_data != "None":
                try:
                    t = UniversityInfo.objects.get(product=instance)
                    t.name = university_info_data["name"]
                    t.faculty = university_info_data["faculty"]
                    t.year = university_info_data["year"]
                    t.save()
                except:
                    mod = UniversityInfo(product=instance, **university_info_data)
                    mod.save()

        try:
            if university_info_data is None:
                ob = UniversityInfo.objects.get(product=instance.id)
                ob.delete()

        except:
            pass
        if address_data:
            Address.objects.filter(product=instance.id).update(**address_data)

        instance.save()
        return instance


class NewProductSerializer(serializers.ModelSerializer):
    university_info = UniversityInfoSerializer(required=False, allow_null=True)
    process_info = ProcessInfoSerializer(required=True)
    address = AddressSerializer(required=True)
    image = Base64ImageField(required=True)

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
        extra_kwargs = {
            "seller": {"write_only": True},
        }

    def create(self, validated_data):
        university_info_data = validated_data.pop(
            "university_info",
            None,
        )

        process_info_data = validated_data.pop("process_info")
        address_data = validated_data.pop("address")
        category_ids = validated_data.pop("category")
        product = Product.objects.create(**validated_data)

        product.category.add(*category_ids)
        if university_info_data is not None:
            UniversityInfo.objects.create(product=product, **university_info_data)
        ProcessInfo.objects.create(product=product, **process_info_data)
        Address.objects.create(
            product=product,
            city=address_data["city"],
            rest=address_data["rest"],
        )

        return product
