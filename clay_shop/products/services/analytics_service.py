from datetime import timedelta
from typing import Any

from django.db.models import QuerySet, Avg, Count
from django.utils import timezone

from products.models import Product, Review
from products.services.products_crud import ProductsService
from products.services.review_crud import ReviewService


class AnalyticsService:
    @staticmethod
    def get_dashboard_stats() -> dict[str, Any]:
        return {
            "total_products": Product.objects.count(),
            "active_products": Product.objects.filter(is_active=True).count(),
            "out_of_stock": ProductsService.get_out_of_stock_count(),
            "low_stock": ProductsService.get_low_stock_products().count(),
            "total_reviews": ReviewService.get_total_reviews_count(),
            "pending_reviews": ReviewService.get_pending_reviews_count(),
            "avg_rating": ReviewService.get_average_rating(),
        }

    @staticmethod
    def get_top_rated_products(min_reviews: int = 1, limit: int = 10) -> QuerySet:
        return (
            Product.objects.annotate(
                avg_rating=Avg("review__rating"), review_count=Count("review")
            )
            .filter(review_count__gte=min_reviews)
            .order_by("-avg_rating")[:limit]
        )

    @staticmethod
    def get_products_needing_attention(
        min_reviews: int = 3, rating_threshold: float = 3.5, limit: int = 10
    ) -> QuerySet:
        return (
            Product.objects.annotate(
                avg_rating=Avg("review__rating"), review_count=Count("review")
            )
            .filter(review_count__gte=min_reviews, avg_rating__lt=rating_threshold)
            .order_by("-avg_rating")[:limit]
        )

    @staticmethod
    def get_period_stats(days: int = 30) -> dict[str, Any]:
        date_from = timezone.now() - timedelta(days=days)

        return {
            "new_reviews": Review.objects.filter(created_at__gte=date_from).count(),
            "new_products": Product.objects.filter(created_at__gte=date_from).count(),
        }

    @staticmethod
    def get_category_distribution() -> QuerySet:
        return (
            Product.objects.values("category_id__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )