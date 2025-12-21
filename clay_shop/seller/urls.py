from django.urls import path

from seller.seller_views import (
    SellerDashboardView,
    SellerProductListView,
    SellerProductCreateView,
    SellerProductDetailView,
    SellerProductUpdateView,
    SellerProductToggleActiveView,
    SellerProductStockUpdateView,
    SellerReviewListView,
    SellerReviewVerifyView,
    SellerServiceListView,
    SellerServiceCreateView,
    SellerServiceUpdateView,
    SellerServiceToggleActiveView,
    SellerAnalyticsView,
)

urlpatterns = [
    # Главная панель
    path("", SellerDashboardView.as_view(), name="dashboard"),
    # Управление продуктами
    path("products/", SellerProductListView.as_view(), name="product-list"),
    path("products/create", SellerProductCreateView.as_view(), name="product-create"),
    path("products/<int:pk>", SellerProductDetailView.as_view(), name="product-detail"),
    path(
        "products/<int:pk>/edit",
        SellerProductUpdateView.as_view(),
        name="product-update",
    ),
    path(
        "products/<int:pk>/toggle-active/",
        SellerProductToggleActiveView.as_view(),
        name="product-toggle-active",
    ),
    path(
        "products/<int:pk>/update-stock/",
        SellerProductStockUpdateView.as_view(),
        name="product-update-stock",
    ),
    # Управление отзывами
    path("reviews/", SellerReviewListView.as_view(), name="review-list"),
    path(
        "reviews/<int:pk>/verify/",
        SellerReviewVerifyView.as_view(),
        name="review-verify",
    ),
    # Управление услугами
    path("services", SellerServiceListView.as_view(), name="service-list"),
    path("services/create", SellerServiceCreateView.as_view(), name="service-create"),
    path(
        "services/<int:pk>/edit",
        SellerServiceUpdateView.as_view(),
        name="service-update",
    ),
    path(
        "services/<int:pk>/toggle-active/",
        SellerServiceToggleActiveView.as_view(),
        name="service-toggle-active",
    ),
    # Аналитика
    path("analytics/", SellerAnalyticsView.as_view(), name="analytics"),
]
