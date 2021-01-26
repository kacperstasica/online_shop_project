import braintree
from django.shortcuts import render, get_object_or_404, redirect

# instantiate Braintree payment gateway
from django.views.generic.base import View, TemplateView

from myshop import settings
from orders.models import Order
from payment.tasks import payment_completed

gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


class PaymentProcessView(View):

    def get(self, request):
        # generate token
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        client_token = gateway.client_token.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})

    def post(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        nonce = request.POST.get('payment_method_nonce', None)
        # create and submit transaction
        result = gateway.transaction.sale({
            'amount':  f'{order.get_total_cost():.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # mark order as paid
            order.paid = True
            # store the transaction id
            order.braintree_id = result.transaction.id
            order.save()
            # launch asynchronous task
            payment_completed.delay(order.id)
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')


class PaymentDoneView(TemplateView):
    template_name = 'payment/done.html'


class PaymentCanceledView(TemplateView):
    template_name = 'payment/canceled.html'
