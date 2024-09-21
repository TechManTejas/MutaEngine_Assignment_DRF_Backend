from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'product', 'completed', 'created_at')
    list_filter = ('completed', 'created_at')  # Allows filtering by completion status and creation date
    search_fields = ('order_id', 'user__username', 'product__name')  # Enables search by order ID, username, or product name
    actions = ['delete_expired_orders_action']

    def delete_expired_orders_action(self, request, queryset):
        # Custom admin action to delete expired orders
        Order.delete_expired_orders()
        self.message_user(request, "Expired orders have been deleted successfully.")

    delete_expired_orders_action.short_description = 'Delete expired orders'

# Register the Order model and the OrderAdmin class with the admin site
admin.site.register(Order, OrderAdmin)
