from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
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

from .forms import UserCreateForm, UserUpdateForm
from .models import User
from .services.crud import CrudUser


# Create your views here.
class UserListView(ListView):
    model = User
    template_name = ...
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return CrudUser.get_all_users()


class UserDetailView(DetailView):
    model = User
    template_name = "users/templates/profile"
    context_object_name = "user"

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get("pk"))
        if not user:
            raise Http404("Пользователь не найден")
        return user


class UserCreateView(SuccessMessageMixin, CreateView):
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


class UserUpdateView(UpdateView):
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

class UserDeleteView(DeleteView):
    model = User
    template_name = ...
    success_url = reverse_lazy('user-list')

    def get_object(self, queryset=None):
        user = CrudUser.get_user_by_id(self.kwargs.get('pk'))
        if not user:
            raise Http404("Пользователь не найден")
        return user

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success = CrudUser.delete_user(self.object.id)
        if success:
            messages.success(request, f"Пользователь {self.object.email} успешно удален")
        else:
            messages.error(request, "Ошибка при удалении пользователя")
        return redirect(self.success_url)
