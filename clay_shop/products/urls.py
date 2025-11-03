from django.urls import path

from .views import ProductDetailView, ProductListView

app_name = "products"

urlpatterns = [
    path('', ProductDetailView.as_view(), name="product"),
    path('<slug:slug>/', ProductDetailView.as_view(), name="detail")
]
