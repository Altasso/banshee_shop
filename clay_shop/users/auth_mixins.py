from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin_role

    def handle_no_permission(self):
        messages.error(self.request, "Доступ только для админов")
        return super().handle_no_permission()


class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_seller or self.request.user.is_admin_role

    def handle_no_permission(self):
        messages.error(self.request, "Доступ только для продавцов")
        return super().handle_no_permission()


class OwnerOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.id == obj.id or self.request.user.is_admin_role

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этому ресурсу")
        return super().handle_no_permission()
