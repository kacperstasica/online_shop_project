from django.urls import path

from payment.views import PaymentProcessView, PaymentDoneView, PaymentCanceledView

app_name = 'payment'


urlpatterns = [
    path('process/', PaymentProcessView.as_view(), name='process'),
    path('done/', PaymentDoneView.as_view(), name='done'),
    path('cancelled/', PaymentCanceledView.as_view(), name='canceled'),
]