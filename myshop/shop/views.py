from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView

from .models import Category, Product


class ProductListView(TemplateView):
    template_name = 'shop/product/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug', None)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category__slug=category_slug)
        else:
            category = None
            products = Product.objects.filter(available=True)
        categories = Category.objects.all()

        context.update({
            'category': category,
            'products': products,
            'categories': categories,
        })
        return context


class ProductDetailView(DetailView):
    template_name = 'shop/product/detail.html'
    model = Product
    # pk_url_kwarg = 'id'
