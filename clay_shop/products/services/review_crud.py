from typing import Dict

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet, Avg, Count

from products.models import Review


class ReviewService:
    @staticmethod
    def get_product_reviews(product_id: int, verified_only: bool = False) -> QuerySet:
        filters = {"product_id": product_id}
        if verified_only:
            filters["is_verified"] = True

        return (
            Review.objects.filter(**filters)
            .select_related("user_id")
            .order_by("-create_at")
        )

    @staticmethod
    def get_all_reviews(
        verified_only: bool | None = None, rating_filter: int | None = None
    ) -> QuerySet:
        queryset = Review.objects.select_related("product_id", "user_id").order_by(
            "-created_at"
        )

        if verified_only is not None:
            if verified_only:
                queryset = queryset.filter(is_verified=True)
            else:
                queryset = queryset.filter(is_verified=False)
        if rating_filter:
            queryset = queryset.filter(rating=rating_filter)

        return queryset

    @staticmethod
    def get_pending_reviews_count() -> int:
        return Review.objects.filter(is_verified=False).count()

    @staticmethod
    def get_total_reviews_count() -> int:
        return Review.objects.count()

    @staticmethod
    def get_average_rating() -> float:
        result = Review.objects.aggregate(Avg("rating"))
        return result["rating__avg"] or 0

    @staticmethod
    def get_recent_reviews(limit: int = 5) -> QuerySet:
        return Review.objects.select_related("product_id", "user_id").order_by(
            "-create_at"
        )[:limit]

    @staticmethod
    def get_rating_distribution() -> Dict[int, int]:
        rating_stats = (
            Review.objects.values("rating")
            .annotate(count=Count("rating"))
            .order_by("rating")
        )

        return {item["rating"]: item["count"] for item in rating_stats}

    @staticmethod
    @transaction.atomic
    def create_review(
        product_id: int, user_id: int, rating: int, comment: str
    ) -> Review:
        if not 1 <= rating <= 5:
            raise ValidationError("Рейтинг должен быть от 1 до 5")

        if Review.objects.filter(product_id=product_id, user_id=user_id).exists():
            raise ValidationError("Вы уже оставили отзыв на этот продукт")

        review = Review.objects.create(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            is_verified=False,
        )
        return review

    @staticmethod
    def verify_review(review_id: int) -> bool:
        try:
            review = Review.objects.get(id=review_id)
            review.is_verified = True
            review.save()
            return True
        except Review.DoesNotExist:
            return False

    @staticmethod
    def get_user_reviews(user_id: int) -> QuerySet:
        return (
            Review.objects.filter(user_id=user_id)
            .select_related("product_id")
            .order_by("-create_at")
        )
