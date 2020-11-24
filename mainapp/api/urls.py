from django.urls import path
from .api_views import *

urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='categories'),
    path('costumers/', CostumersListApiView.as_view(), name='costumers'),
    path('orders/', OrdersAPIView.as_view(), name='products'),
    path('order/<str:pk>', OrderDetailApiView.as_view(), name='products'),
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('products/<str:id>', ProductDetailApiView.as_view(), name='product_detail'),
    ]