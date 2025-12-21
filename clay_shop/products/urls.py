from django.urls import path

from products.views.category_views import CategoryDetailView, CategoryListView
from products.views.product_views import (
    ProductDetailView,
    ProductSearchView,
    ServiceListView,
)
from products.views.review_views import ReviewCreateView, UserReviewListView

app_name = "products"

urlpatterns = [
    # Категории
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    # Продукты
    path("", ProductDetailView.as_view(), name="product-list"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("search/", ProductSearchView.as_view(), name="product-search"),
    # Отзывы
    path(
        "product/<int:product_id>/review/",
        ReviewCreateView.as_view(),
        name="review-create",
    ),
    path("my-reviews/", UserReviewListView.as_view(), name="user-reviews"),
    # Услуги
    path("services/", ServiceListView.as_view(), name="service-list"),
]
