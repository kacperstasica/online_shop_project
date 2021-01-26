import weasyprint
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import View, DetailView, CreateView

from cart.cart import Cart
from myshop import settings
from orders.forms import OrderCreateForm
from orders.models import OrderItem, Order
from .tasks import order_created


class OrderCreate(CreateView):
    form_class = OrderCreateForm
    template_name = 'orders/order/create.html'

    def get_context_data(self, **kwargs):
        return {'cart': Cart(self.request), **super().get_context_data(**kwargs)}

    def form_valid(self, form):
        cart = Cart(self.request)
        # create Order object, but avoid saving it to database with commit=False
        order = form.save(commit=False)
        if cart.coupon:
            order.coupon = cart.coupon
            order.discount = cart.coupon.discount
        order.save()
        for item in cart:
            OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        # launch asynchronous task
        order_created.delay(order.id)
        # set the order in session
        self.request.session['order_id'] = order.id
        return redirect(reverse('payment:process'))


class AdminOrderDetailView(PermissionRequiredMixin, DetailView):
    model = Order
    permission_required = ['is_staff']
    template_name = 'orders/admin/orders/order/order_detail.html'


class AdminOrderPdfView(PermissionRequiredMixin, View):
    permission_required = ['is_staff']

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        html = render_to_string('orders/order/pdf.html',
                                {'order': order})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=order_{order_id}.pdf'
        weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT + 'css/pdf.css'
        )])
        return response
