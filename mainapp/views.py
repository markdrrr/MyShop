from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, View
from .forms import OrderForm
from .mixins import *
from .models import *
from django.db import models, transaction
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .utils import recalc_cart


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = get_categories_for_left_sidebar()
        products = []
        ct_models = ContentType.objects.filter(model__in=('notebook', 'smartphone'))
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'base.html', context)

# class BaseView(View):
#
#     def get(self, request, *args, **kwargs):
#         # customer = Customer.objects.get(user=request.user)
#         # cart = Cart.objects.get(owner=customer)
#         categories = get_categories_for_left_sidebar()
#         products = []
#         ct_models = ContentType.objects.filter(model__in=('notebook', 'smartphone'))
#         for ct_model in ct_models:
#             model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
#             products.extend(model_products)
#         # отфильтровываем в нужном порядке
#         # products = sorted(
#         #                 products, key=lambda x: x.__class__._meta.model_name.startswith('notebook'), reverse=True
#         #             )
#         context = {
#             'categories': categories,
#             'products': products,
#             # 'cart': cart
#         }
#         return render(request, 'base.html', context)
# def test_view(request):
#     categories = get_categories_for_left_sidebar()
#     return render(request, 'base.html', {'categories': categories})


def product_detail_view(request, ct_model, slug):

    CT_MODEL_CLASS = {
        'notebook': Notebook,
        'smartphone': Smartphone
    }
    model = CT_MODEL_CLASS[f'{ct_model}']
    product = get_object_or_404(model, slug=slug)
    categories = get_categories_for_left_sidebar()
    context = {'product': product, 'categories': categories, 'ct_model': ct_model}
    # достаем карзину
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(
                user=request.user
            )
        cart = Cart.objects.filter(owner=customer, in_order=False).first()
        if not cart:
            cart = Cart.objects.create(owner=customer)
    else:
        cart = Cart.objects.filter(for_anonymous_user=True).first()
        if not cart:
            cart = Cart.objects.create(for_anonymous_user=True)
    context["cart"] = cart
    return render(request, 'product_detail.html', context)


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['category_products'] = model.objects.all()
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        # cart_product.delete()
        # recalc_cart(self.cart)
        # messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeCountView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        count = int(request.POST.get('count'))
        cart_product.count = count
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = get_categories_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = None
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            recalc_cart(self.cart)
            new_order.cart = self.cart
            new_order.save()
            if new_order.customer:
                customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')