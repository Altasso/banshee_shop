from django.views.generic import DetailView, ListView

from .models import Product


# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = 'templates/catalog'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.object.filter(is_active=True).order_by('-created_at')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'templates/product_detail'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
