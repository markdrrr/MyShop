from collections import OrderedDict
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import *
from ..models import *


class Pagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_zise'
    max_page_size = 10


class OrdersAPIView(ListCreateAPIView, RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    pagination_class = Pagination
    queryset = Order.objects.all()


class OrderDetailApiView(RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class CategoryAPIView(ListCreateAPIView, RetrieveUpdateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = Pagination
    queryset = Product.objects.all()
    filter_backends = [SearchFilter]
    search_fields = [f.name for f in Product._meta.get_fields()]


class ProductDetailApiView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'id'


class CostumersListApiView(ListAPIView):
    serializer_class = CostumerSerializer
    queryset = Customer.objects.all()
