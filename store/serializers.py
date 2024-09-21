from rest_framework import serializers
from .models import Product, UserProduct


# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "detailed_description",
            "price",
            "cover_image"
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
