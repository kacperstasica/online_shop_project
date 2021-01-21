import weasyprint
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View, DetailView

from cart.cart import Cart
from myshop import settings
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
