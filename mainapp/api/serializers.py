from rest_framework import routers, serializers, viewsets
from ..models import *


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects)
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)

    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CostumerSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    class Meta:
        model = Customer
        fields = '__all__'