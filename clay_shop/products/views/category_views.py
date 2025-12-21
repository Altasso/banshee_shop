from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from products.models import Category
from products.services.category_crud import CategoryGet
from products.services.products_crud import ProductsService


# Create your views here.
class CategoryListView(ListView):
    model = Category
    template_name = ...
    context_object_name = "categories"

    def get_queryset(self):
        return CategoryGet.get_all_categories()


class CategoryDetailView(DetailView):
    model = Category
    template_name = ...
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Category, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = ProductsService.get_products_by_category(self.object.id)
        return context


