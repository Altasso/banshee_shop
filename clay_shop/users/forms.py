from django import forms

from .models import User, UserAddress, UserProfile


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "is_verified"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Новый пароль (оставьте пустым, если не хотите менять)",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role", "is_verified"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "date_of_birth", "preferred_delivery_method"]
        widgets = {
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 (999) 999-99-99"}
            ),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "preferred_delivery_method": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "phone": "Телефон",
            "date_of_birth": "Дата рождения",
            "preferred_delivery_method": "Предпочитаемый способ доставки",
        }


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ["title", "address", "is_default"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Дом, Работа, и т.д."}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Полный адрес доставки",
                }
            ),
            "is_default": forms.CheckboxInput(attrs={"class": "forms-check-input"}),
        }
        label = {
            "title": "Название",
            "address": "Адрес",
            "is_default": "Использовать по умолчанию",
        }
