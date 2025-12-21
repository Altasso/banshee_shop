from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    ListView,
)

from products.forms.products_form import ProductForm, ProductImageFormSet, ServiceForm
from products.models import Product, Review, Service
from products.services.service_crud import ServiceCrud
from users.auth_mixins import OwnerOrAdminMixin

from products.services.analytics_service import AnalyticsService
from products.services.products_crud import ProductsService
from products.services.review_crud import ReviewService


class SellerDashboardView(OwnerOrAdminMixin, TemplateView):
    template_name = ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(AnalyticsService.get_dashboard_stats())

        context["recent_reviews"] = ReviewService.get_recent_reviews(limit=5)

        context["low_stock_products"] = ProductsService.get_low_stock_products(
            threshold=5
        )[:10]

        context["popular_products"] = ProductsService.get_popular_products(limit=5)

        return context


class SellerProductListView(OwnerOrAdminMixin, ListView):
    model = Product
    template_name = ...
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        return ProductsService.filter_products_for_seller(
            status=self.request.GET.get("status"),
            search=self.request.GET.get("search"),
            sort_by=self.request.GET.get("sort", "-created_at"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_by"] = self.request.GET.get("sort", "-created_at")
        return context


class SellerProductDetailView(OwnerOrAdminMixin, DetailView):
    model = Product
    template_name = ...
    context_object_name = "product"

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        return ProductsService.get_product_by_id_for_seller(product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_data = ProductsService.get_product_with_reviews(self.object.id)
        if product_data:
            context["avg_rating"] = product_data["avg_rating"]
            context["review_count"] = product_data["review_count"]

        context["reviews"] = ReviewService.get_product_reviews(self.object.id)

        context["images"] = self.object.images.all().order_by("order")

        return context


class SellerProductCreateView(OwnerOrAdminMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = ...
    success_url = reverse_lazy("seller:product-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["images_formset"] = ProductImageFormSet(self.request.POST)
        else:
            context["images_formset"] = ProductImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            product_data = form.cleaned_data

            self.object = form.save()

            image_formset.instance = self.object
            image_formset.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(context)


class SellerProductUpdateView(OwnerOrAdminMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = ...

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        return ProductsService.get_product_by_id_for_seller(product_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["image_formset"] = ProductImageFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["image_formset"] = ProductImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if image_formset.is_valid():
            product_data = form.cleaned_data
            ProductsService.update_product(self.object.id, product_data)

            image_formset.instance = self.object
            image_formset.save()

            return redirect("seller:product-detail", pk=self.object.pk)
        else:
            return self.render_to_response(context)


class SellerProductToggleActiveView(OwnerOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get("pk")

        is_active = ProductsService.toggle_product_active(product_id)

        if is_active is not None:
            return JsonResponse(
                {
                    "success": True,
                    "is_active": is_active,
                    "message": f"Продукт {'активирован' if is_active else 'деактивирован'}",
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Продукт не найден"}, status=404
            )


class SellerProductStockUpdateView(OwnerOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get("pk")
        action = request.POST.get("action")
        quantity = int(request.POST.get("quantity", 0))

        stock_quantity = ProductsService.update_stock(product_id, action, quantity)

        if stock_quantity is not None:
            return JsonResponse(
                {
                    "success": True,
                    "stock_quantity": stock_quantity,
                    "message": "Количество обновлено",
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Продукт не найден"}, status=404
            )


class SellerReviewListView(OwnerOrAdminMixin, ListView):
    model = Review
    template_name = ...
    context_object_name = "reviews"
    paginate_by = 20

    def get_queryset(self):
        status = self.request.GET.get("status")
        rating = self.request.GET.get("rating")

        verified_only = None
        if status == "pending":
            verified_only = False
        elif status == "verified":
            verified_only = True

        return ReviewService.get_all_reviews(
            verified_only=verified_only, rating_filter=int(rating) if rating else None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["rating_filter"] = self.request.GET.get("rating", "")
        return context


class SellerReviewVerifyView(OwnerOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        review_id = self.kwargs.get("pk")

        success = ReviewService.verify_review(review_id)

        return JsonResponse(
            {
                "success": success,
                "message": "Отзыв верифицирован" if success else "Ошибка верификации",
            }
        )


class SellerServiceListView(OwnerOrAdminMixin, ListView):
    model = Service
    template_name = ...
    context_object_name = "service"
    paginate_by = 20

    def get_queryset(self):
        return ServiceCrud.get_all_services()


class SellerServiceCreateView(OwnerOrAdminMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = ...
    success_url = reverse_lazy("seller:service-list")

    def form_valid(self, form):
        service_data = form.cleaned_data
        ServiceCrud.create_service(service_data)
        return redirect(self.success_url)


class SellerServiceUpdateView(OwnerOrAdminMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = ...
    success_url = reverse_lazy("seller:service-list")

    def get_object(self, queryset=None):
        service_id = self.kwargs.get("pk")
        return ServiceCrud.get_service_by_id(service_id)

    def form_valid(self, form):
        service_data = form.cleaned_data
        ServiceCrud.update_service(self.object.id, service_data)
        return redirect(self.success_url)


class SellerServiceToggleActiveView(OwnerOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        service_id = self.kwargs.get("pk")

        is_active = ServiceCrud.toggle_service_active(service_id)

        if is_active is not None:
            return JsonResponse(
                {
                    "success": True,
                    "is_active": is_active,
                    "message": f"Услуга {'активирована' if is_active else 'деактивирована'}",
                }
            )
        else:
            return JsonResponse(
                {"success": False, "error": "Услуга не найдена"}, status=404
            )


class SellerAnalyticsView(OwnerOrAdminMixin, TemplateView):
    template_name = ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["rating_distribution"] = ReviewService.get_rating_distribution()

        context["top_rated_products"] = AnalyticsService.get_top_rated_products(
            min_reviews=1, limit=10
        )

        context["needs_attention_pdoucts"] = (
            AnalyticsService.get_products_needing_attention(
                min_reviews=3, rating_threshold=3.5, limit=10
            )
        )

        period_days = int(self.request.GET.get("period", 30))
        context['period_days'] = period_days
        context.update(AnalyticsService.get_period_stats(days=period_days))

        context['category_distribution'] = AnalyticsService.get_category_distribution()

        return context