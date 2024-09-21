from rest_framework import viewsets
from .models import Product, UserProduct
from .serializers import ProductSerializer, UserProductSerializer

# Read-only ViewSet for Product
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UserProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProduct.objects.all()
    serializer_class = UserProductSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)