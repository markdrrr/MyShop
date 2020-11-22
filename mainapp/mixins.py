from django.views.generic import View
from .models import *


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
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
        self.cart = cart
        self.categories = Category.objects.all()
        return super().dispatch(request, *args, **kwargs)



# class CartMixin(View):
#
#     def dispatch(self, request, *args, **kwargs):
#         print('11111111111111111', request)
#         if request.user.is_authenticated:
#             print('TRUE !!!!!!!!!!')
#             customer = Customer.objects.filter(user=request.user).first()
#             if not customer:
#                 customer = Customer.objects.create(
#                     user=request.user
#                 )
#             cart = Cart.objects.filter(owner=customer, in_order=False).first()
#             if not cart:
#                 cart = Cart.objects.create(owner=customer)
#         else:
#             print('else !!!!!!!!!!')
#             cart = Cart.objects.filter(for_anonymous_user=True).first()
#             if not cart:
#                 cart = Cart.objects.create(for_anonymous_user=True)
#         self.cart = cart
#         print(cart)
#         return super().dispatch(request, *args, **kwargs)

