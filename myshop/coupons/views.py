from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from coupons.forms import CouponApplyForm
from coupons.models import Coupon


class CouponApplyView(FormView):
    form_class = CouponApplyForm
    success_url = reverse_lazy('cart:cart_detail')
    http_method_names = ['post']

    def form_valid(self, form):
        now = timezone.now()
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        active=True)
            self.request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            self.request.session['coupon_id'] = None
        return redirect('cart:cart_detail')
