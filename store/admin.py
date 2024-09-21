from django.contrib import admin
from .models import ProductImage, Product, UserProduct


# Admin for ProductImage
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
    )
    search_fields = ("id",)


# Admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "cover_image")
    search_fields = ("name",)
    list_filter = ("price",)
    filter_horizontal = ("images",)


# Admin for UserProduct
class UserProductAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "purchase_date", "invoice_no")
    search_fields = ("user__username", "product__name", "invoice_no")
    list_filter = ("purchase_date",)


# Register the models with their respective admin classes
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(UserProduct, UserProductAdmin)
