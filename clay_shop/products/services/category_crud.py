from django.db.models import QuerySet

from products.models import Category


class CategoryGet:
    @staticmethod
    def get_all_categories() -> QuerySet:
        return Category.objects.all()

    @staticmethod
    def get_category_by_slug(slug: str) -> Category | None:
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def get_category_with_products(slug: int) -> Category | None:
        try:
            return Category.objects.prefetch_related("products").get(slug=slug)
        except Category.DoesNotExist:
            return None

