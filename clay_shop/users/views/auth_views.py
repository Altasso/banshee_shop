from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms.auth_forms import ChangePasswordForm, LoginForm, UserRegistrationForm
from users.models import User
from users.services.auth_service import AuthService
from users.services.email_verification_service import EmailVerificationService
from users.tasks import send_verification_email_task


class AuthLoginView(LoginView):
    form_class = LoginForm
    template_name = "auth_templates/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url

        user = self.request.user
        if user.is_admin_role:
            return reverse_lazy("user-list")
        elif user.is_seller:
            return reverse_lazy("user-profile")  # TODO: seller dashboard
        else:
            return reverse_lazy("user-profile")

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(
            self.request, f"Добро пожаловать, {self.request.user.first_name}!"
        )

        if self.request.headers.get("HX-Request"):
            from django.http import HttpResponse

            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        response = super().form_invalid(form)

        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))

        return response


class AuthLogoutView(LogoutView):
    next_page = "login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Вы успешно вышли из системы")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if request.headers.get("HX-Request"):
            from django.http import HttpResponse

            redirect_response = HttpResponse()
            redirect_response["HX-Redirect"] = self.get_success_url()
            return redirect_response
        return response


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "auth_templates/register.html"
    success_url = reverse_lazy("login")
    success_message = "Регистрация успешна! Проверьте email для подтверждения"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("user-profile")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_verified = False
        user.save()

        AuthService.assign_role_group(user)

        verification_link = EmailVerificationService.generate_verification_link(user)

        send_verification_email_task.delay(
            user_email=user.email,
            user_name=user.first_name,
            verification_link=verification_link,
        )

        messages.success(
            self.request, "Регистрация успешна! Проверьте email для подтверждения"
        )
        if self.request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = str(self.success_url)
            return response

        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))

        return super().form_invalid(form)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    form_class = ChangePasswordForm
    template_name = "auth_templates/change_password.html"
    success_url = reverse_lazy("user-profile")
    success_message = 'Пароль успешно изменен'
