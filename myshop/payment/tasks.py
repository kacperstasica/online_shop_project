from io import BytesIO

import weasyprint
from celery import task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from myshop import settings
from orders.models import Order


@task
def payment_completed(order_id):
    """Task to send e-mail notification
    when payment is complete"""
    order = Order.objects.get(id=order_id)

    # create invoice mail
    subject = f'My Shop Invoice no. {order.id}'
    message = 'Please find attached invoice for your recent purchase'
    email = EmailMessage(subject,
                         message,
                         'admin@myshop.com',
                         [order.email])
    # generate PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out,
                                           stylesheets=stylesheets)
    # attach PDF file
    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')
    # send email
    email.send()
