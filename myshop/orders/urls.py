from django.urls import path

from .views import OrderCreate, AdminOrderDetailView

app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreate.as_view(), name='order_create'),
    path('admin/order/<int:pk>/', AdminOrderDetailView.as_view(), name='admin_order_detail'),
]
