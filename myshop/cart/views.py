from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, View

from coupons.forms import CouponApplyForm
from .cart import Cart
from .forms import CartAddProductForm
from shop.models import Product


class CartAdd(FormView):
    form_class = CartAddProductForm
    success_url = reverse_lazy('cart:cart_detail')
    http_method_names = ['post']

    def get_product(self):
        product_id = self.kwargs.get('product_id', None)
        return get_object_or_404(Product, id=product_id)

    def get_context_data(self, **kwargs):
        return {
            'product': self.get_product(),
            **super().get_context_data(**kwargs)
        }

    def form_valid(self, form):
        cd = form.cleaned_data
        cart = Cart(self.request)
        cart.add(product=self.get_product(),
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
        return super().form_valid(form)


class CartRemove(View):
    http_method_names = ['post']
    success_url = reverse_lazy('cart:cart_detail')

    def post(self, request, *args, **kwargs):
        cart = Cart(self.request)
        cart.remove(product=self.get_product())
        return redirect(self.success_url)

    def get_product(self):
        product_id = self.kwargs.get('product_id', None)
        return get_object_or_404(Product, id=product_id)


class CartDetail(View):

    def get(self, request):
        cart = Cart(self.request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                       'override': True})
        coupon_apply_form = CouponApplyForm()
        return render(request, 'cart/detail.html', {'cart': cart,
                                                    'coupon_apply_form': coupon_apply_form})
