from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView

from .models import Category, Product
from cart.forms import CartAddProductForm


class ProductListView(TemplateView):
    template_name = 'shop/product/list.html'

    def get_context_data(self, **kwargs):
        categories = Category.objects.all()
        category_slug = self.kwargs.get('category_slug', None)
        category = None
        products = Product.objects.filter(available=True)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category__slug=category_slug)
        return {
            'category': category,
            'products': products,
            'categories': categories,
            **super().get_context_data(**kwargs)
        }


class ProductDetailView(DetailView):
    template_name = 'shop/product/detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        return {
            'cart_product_form': CartAddProductForm,
            **super().get_context_data(**kwargs)
        }
