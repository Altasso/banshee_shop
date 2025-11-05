from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
    UpdateView,
)

from .forms import UserAddressForm, UserCreateForm, UserProfileForm, UserUpdateForm
from .mixins import AdminRequiredMixin, OwnerOrAdminMixin
from .models import User, UserAddress, UserProfile
from .services.user_address_crud import UserAddressCrud
from .services.user_crud import CrudUser
from .services.user_profile_crud import UserProfileCrud


# Create your views here.
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = ...
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return CrudUser.get_all_users()


class UserDetailView(OwnerOrAdminMixin, DetailView):
    model = User
    template_name = "users/templates/profile"
    context_object_name = "user"

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get("pk"))
        if not user:
            raise Http404("Пользователь не найден")
        return user


class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = ...
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
    template_name = ...
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
    template_name = ...
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


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = ...
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
    template_name = ...
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddressCrud.get_user_address(self.request.user)


class UserAddressCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = ...
    success_url = reverse_lazy("address-list")
    success_message = "Адрес успешно добавлен"

    def form_valid(self, form):
        address = UserAddressCrud.create_address(self.request.user, form.cleaned_data)
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class UserAddressUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = ...
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
    template_name = ...
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
