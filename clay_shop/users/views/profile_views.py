from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from users.forms.user_forms import UserProfileForm
from users.models import UserProfile
from users.services.user_profile_crud import UserProfileCrud


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile_templates/user_profile.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile = UserProfileCrud.get_or_create_profile(self.request.user)

        context["profile"] = profile

        context["status"] = {
            "orders_count": 0,  # TODO: Добавить подсчет заказов
            "reviews_count": 0,  # TODO: Добавить подсчет отзывов
            "total_spent": 0,  # TODO: Добавить подсчет потраченных средств
            "bonus_points": 0,  # TODO: Добавить систему бонусов
        }

        context["recent_orders"] = []  # TODO: Добавить последние заказы

        context["recent_reviews"] = []  # TODO: Добавить последние отзывы

        return context


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profile_templates/user_profile_form.html"
    success_message = "Профиль успешно обновлен"

    def get_object(self, queryset=None):
        return UserProfileCrud.get_or_create_profile(self.request.user)

    def get_success_url(self):
        return reverse_lazy("user-profile")

    def form_valid(self, form):
        profile = UserProfileCrud.update_profile(self.request.user, form.cleaned_data)
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())


