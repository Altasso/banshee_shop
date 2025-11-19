from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class VerifiedEmailRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_verified
    def handle_no_permission(self):
        messages.warning(
            self.request,
            "⚠️ Для оформления заказа необходимо подтвердить email. "
            "Проверьте почту и перейдите по ссылке из письма."
        )
        return redirect('cart')
