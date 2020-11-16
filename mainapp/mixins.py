from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import *


class CategoryDetailMixin(SingleObjectMixin):

    CATEGORY_SLUG2PRODUCT_MODEL = {
        'notebook': Notebook,
        'smartsphone': Smartphone
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_categories_for_left_sidebar()
        return context


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        print('11111111111111111', request)
        if request.user.is_authenticated:
            print('TRUE !!!!!!!!!!')
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            print('else !!!!!!!!!!')
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        print(cart)
        return super().dispatch(request, *args, **kwargs)

