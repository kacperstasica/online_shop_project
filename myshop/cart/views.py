from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import FormView, View, DeleteView, TemplateView

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


# class CartRemove(TemplateView):
#     template_name = 'cart/detail.html'
#     # form_class = CartAddProductForm
#     http_method_names = ['post']
#     success_url = reverse_lazy('cart:cart_detail')
#
#     def get_product(self):
#         product_id = self.kwargs.get('product_id', None)
#         return get_object_or_404(Product, id=product_id)
#
#     def form_valid(self, form):
#         cart = Cart(self.request)
#         cart.remove(product=self.get_product())
#         return super().form_valid(form)

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                   'override': True})
    return render(request, 'cart/detail.html', {'cart': cart})
