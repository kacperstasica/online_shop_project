from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView

from .models import Category, Product
from cart.forms import CartAddProductForm
from .recommender import Recommender


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

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('id')
        instance = Product.objects.get(id=pk)
        return instance

    def get_context_data(self, **kwargs):
        r = Recommender()
        return {
            'cart_product_form': CartAddProductForm,
            'recommended_products': r.suggest_products_for([self.get_object(Product)], 4),
            **super().get_context_data(**kwargs)
        }
