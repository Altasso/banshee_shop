from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from products.models import Product, Service
from products.services.category_crud import CategoryGet
from products.services.products_crud import ProductsService
from products.services.review_crud import ReviewService
from products.services.service_crud import ServiceCrud


class ProductListView(ListView):
    model = Product
    template_name = ...
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = ProductsService.get_active_products()
        category_slug = self.request.GET.get("category")
        if category_slug:
            category = CategoryGet.get_category_by_slug(category_slug)
            if category:
                queryset = queryset.filter(category_id=category)

        search_query = self.request.GET.get("q")
        if search_query:
            queryset = ProductsService.search_products(search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = CategoryGet.get_all_categories()
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = ...
    context_object_name = "product"

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        return get_object_or_404(Product, id=product_id, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product_data = ProductsService.get_product_with_reviews(self.object.id)
        if product_data:
            context["avg_rating"] = product_data["avg_rating"]
            context["review_count"] = product_data["review_count"]

        context["reviews"] = ReviewService.get_product_reviews(
            self.object.id, verified_only=True
        )[:5]

        context["services"] = ServiceCrud.get_active_services()

        context["is_available"] = ProductsService.check_availability(self.object.id)

        return context


class ServiceListView(ListView):
    model = Service
    template_name = ...
    context_object_name = "services"

    def get_queryset(self):
        return ServiceCrud.get_active_services()


class ProductSearchView(ListView):
    model = Product
    template_name = ...
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if query:
            return ProductsService.search_products(query)
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
