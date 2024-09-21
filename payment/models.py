from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from store.models import Product

class Order(models.Model):
    order_id = models.CharField(max_length=255, unique=True)
    completed = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    # Content of order
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"Order {self.order_id}"
    
    @staticmethod
    def delete_expired_orders():
        expiration_time = timezone.now() - timedelta(minutes=12)
        expired_orders = Order.objects.filter(completed=False, created_at__lt=expiration_time)
        expired_orders.delete()  