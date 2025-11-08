from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    LoginForm,
    UserAddressForm,
    UserCreateForm,
    UserProfileForm,
    UserUpdateForm,
    UserRegistrationForm,
)
from .mixins import AdminRequiredMixin, OwnerOrAdminMixin
from .models import User, UserAddress, UserProfile
from .services.auth_service import AuthService
from .services.user_address_crud import UserAddressCrud
from .services.user_crud import CrudUser
from .services.user_profile_crud import UserProfileCrud


# Create your views here.
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return CrudUser.get_all_users()


class UserDetailView(OwnerOrAdminMixin, DetailView):
    model = User
    template_name = "user_detail.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get("pk"))
        if not user:
            raise Http404("Пользователь не найден")
        return user


class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "user_form.html"
    success_url = reverse_lazy("user-list")
    success_message = "Пользователь %(email)s успешно создан"

    def form_valid(self, form):
        try:
            user = CrudUser.create_user(form.cleaned_data)
            self.object = user
            messages.success(self.request, self.success_message % {"email": user.email})
            return redirect(self.success_url)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class UserUpdateView(OwnerOrAdminMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "user_form.html"
    success_message = "Пользователь успешно обновлен"

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get("pk"))
        if not user:
            raise Http404("Пользователь не найден")
        return user

    def get_success_url(self):
        return reverse_lazy("user-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            user = CrudUser.update_user(self.object.id, form.cleaned_data)
            if not user:
                messages.error(self.request, "Ошибка при обновлении пользователя")
                return self.form_invalid(form)
            self.object = user
            messages.success(self.request, self.success_message)
            return redirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "user_confirm_delete.html"
    success_url = reverse_lazy("user-list")

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get("pk"))
        if not user:
            raise Http404("Пользователь не найден")
        return user

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success = CrudUser.delete_user(self.object.id)
        if success:
            messages.success(
                request, f"Пользователь {self.object.email} успешно удален"
            )
        else:
            messages.error(request, "Ошибка при удалении пользователя")
        return redirect(self.success_url)


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "user_profile.html"
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
    template_name = "user_profile_form.html"
    success_message = "Профиль успешно обновлен"

    def get_object(self, queryset=None):
        return UserProfileCrud.get_or_create_profile(self.request.user)

    def get_success_url(self):
        return reverse_lazy("user-profile")

    def form_valid(self, form):
        profile = UserProfileCrud.update_profile(self.request.user, form.cleaned_data)
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())


class UserAddressListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = UserAddress
    template_name = "address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddressCrud.get_user_address(self.request.user)


class UserAddressCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "address_form.html"
    success_url = reverse_lazy("address-list")
    success_message = "Адрес успешно добавлен"

    def form_valid(self, form):
        address = UserAddressCrud.create_address(self.request.user, form.cleaned_data)
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class UserAddressUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "address_form.html"
    success_url = reverse_lazy("address-list")
    success_message = "Адрес успешно обновлен"

    def get_object(self, queryset=None):
        address = UserAddressCrud.get_address_by_id(self.kwargs.get("pk"))
        if not address:
            raise Http404("Адрес не найден")

        if not UserAddressCrud.validate_address_owner(address, self.request.user):
            raise PermissionDenied

        return address

    def form_valid(self, form):
        address = UserAddressCrud.update_address(self.object.id, form.cleaned_data)
        if not address:
            messages.error(self.request, "Ошибка при обновлении адреса")
            return self.form_invalid(form)

        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class UserAddressDeleteView(LoginRequiredMixin, DeleteView):
    model = UserAddress
    template_name = "address_confirm_delete.html"
    success_url = reverse_lazy("address-list")

    def get_object(self, queryset=None):
        address = UserAddressCrud.get_address_by_id(self.kwargs.get("pk"))
        if not address:
            raise Http404("Адрес не найден")

        if not UserAddressCrud.validate_address_owner(address, self.request.user):
            raise PermissionDenied

        return address

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success = UserAddressCrud.delete_address(self.object.id)

        if success:
            messages.success(request, "Адрес успешно удален")
        else:
            messages.error(request, "Ошибка при удалении адреса")

        return redirect(self.success_url)


class AuthLoginView(LoginView):
    template_name = "login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("user-profile")

    def form_valid(self, form):
        email = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        success, message, user = AuthService.login_user(self.request, email, password)

        if success:
            messages.success(self.request, message)
            AuthService.assign_role_group(user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Проверьте правильность введенных данных")
        return super().form_invalid(form)


class AuthLogoutView(LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Вы успешно вышли из системы")
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("user-profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password1"])
        user.save()

        UserProfileCrud.get_or_create_profile(user)

        AuthService.assign_role_group(user)

        messages.success(
            self.request,
            f"Добро пожаловать, {user.username}! Ващ аккаунт успешно создан. Теперь вы можете войти",
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме")
        return super().form_invalid(form)