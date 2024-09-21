"""mutaengine_assignment_drf_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from user import views as user_views
from store import views as store_views
from payment import views as payment_views

router = DefaultRouter()
router.register(r'products', store_views.ProductViewSet, basename='product')
router.register(r'user-products', store_views.UserProductViewSet, basename='user-product')
router.register(r'orders', payment_views.CreateOrderViewSet, basename='order')
router.register(r'webhook', payment_views.PaymentWebhookViewSet, basename='webhook')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', user_views.SignupViewSet.as_view(), name='signup'),
    path("", include(router.urls)),
    path('auth/', user_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Get JWT token
    path('auth/refresh/', user_views.CustomTokenRefreshView.as_view(), name='token_refresh'), # Refresh JWT token
    path('password-reset-link/', user_views.password_reset_link, name='password_reset_link'),
    path('reset-password/<uidb64>/<token>/', user_views.reset_password, name='reset_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
