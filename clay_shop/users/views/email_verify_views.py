from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from users.services.email_verification_service import EmailVerificationService
from users.tasks import send_verification_email_task


class EmailVerifyView(View):
    def get(self, request, uidb64, token):
        success, message = EmailVerificationService.verify_email(uidb64, token)

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect("login")

class ResendVerificationEmailView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user

        if user.is_verified:
            messages.info(request, 'Ваш email уже подтвержден')
            return redirect('user-profile')

        verification_link = EmailVerificationService.generate_verification_link(user)

        send_verification_email_task.delay(
            user_email=user.email,
            user_name=user.first_name,
            verification_link=verification_link
        )

        messages.success(
            request, "✅ Письмо с подтверждением отправлено повторно. Проверьте почту!"
        )
        return redirect(request.META.get('HTTP_REFERER', 'user-profile'))
