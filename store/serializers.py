from rest_framework import serializers
from .models import ProductImage, Product, UserProduct


# Serializer for ProductImage
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "detailed_description",
            "price",
            "cover_image",
            "images",
        ]


# Serializer for UserProduct
class UserProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = UserProduct
        fields = [
            "id",
            "user",
            "product",
            "purchase_date",
            "payment_details",
            "invoice_no",
        ]
