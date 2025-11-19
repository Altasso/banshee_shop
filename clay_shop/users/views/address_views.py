from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from users.forms.user_forms import UserAddressForm
from users.models import UserAddress
from users.services.user_address_crud import UserAddressCrud


class UserAddressListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = UserAddress
    template_name = "address_templates/address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return UserAddressCrud.get_user_address(self.request.user)


class UserAddressCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "address_templates/address_form.html"
    success_url = reverse_lazy("address-list")
    success_message = "Адрес успешно добавлен"

    def form_valid(self, form):
        address = UserAddressCrud.create_address(self.request.user, form.cleaned_data)
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class UserAddressUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserAddress
    form_class = UserAddressForm
    template_name = "address_templates/address_form.html"
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
    template_name = "address_templates/address_confirm_delete.html"
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


