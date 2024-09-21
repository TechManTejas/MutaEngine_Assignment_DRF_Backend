from django.contrib import admin
from .models import  Product, UserProduct

# Admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "cover_image")
    search_fields = ("name",)
    list_filter = ("price",)


# Admin for UserProduct
class UserProductAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "purchase_date", "invoice_no")
    search_fields = ("user__username", "product__name", "invoice_no")
    list_filter = ("purchase_date",)


# Register the models with their respective admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(UserProduct, UserProductAdmin)
