from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, DetailView

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem, Order
from .tasks import order_created


class OrderCreate(View):

    def get(self, request):
        cart = Cart(self.request)
        form = OrderCreateForm(request.POST)
        return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

    def post(self, request):
        cart = Cart(self.request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # set the order in session
            request.session['order_id'] = order.id

            return redirect(reverse('payment:process'))


class AdminOrderDetailView(PermissionRequiredMixin, DetailView):
    model = Order
    permission_required = ['is_staff']
    template_name = 'orders/admin/orders/order/order_detail.html'
