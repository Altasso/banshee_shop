from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from products.models import Product, Review
from products.services.review_crud import ReviewService


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = ...
    fields = ["rating", "comment"]

    def form_valid(self, form):
        product_id = self.kwargs.get("product_id")

        try:
            review = ReviewService.create_review(
                product_id=product_id,
                user_id=self.request.user.id,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )

            if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Отзыв успешно создан",
                        "review_id": review.id,
                    }
                )
            return super().form_valid(form)
        except ValidationError as e:
            if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": str(e)}, status=400)
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "product-detail", kwargs={"pk": self.kwargs.get("product_id")}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get("product_id")
        context["product"] = get_object_or_404(Product, id=product_id)
        return context


class UserReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = ...
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        return ReviewService.get_user_reviews(self.request.user.id)
