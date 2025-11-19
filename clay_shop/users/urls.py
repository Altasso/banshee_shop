from django.urls import path

from users.views.address_views import (
    UserAddressCreateView,
    UserAddressDeleteView,
    UserAddressListView,
    UserAddressUpdateView,
)
from users.views.api_views import AddressAutocompleteView
from users.views.auth_views import (
    AuthLoginView,
    AuthLogoutView,
    ChangePasswordView,
    UserRegistrationView,
)
from users.views.email_verify_views import EmailVerifyView, ResendVerificationEmailView
from users.views.profile_views import UserProfileUpdateView, UserProfileView
from users.views.user_views import (
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)

urlpatterns = [
    # Аутентификация
    path("login/", AuthLoginView.as_view(), name="login"),
    path("logout/", AuthLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="user-create"),
    path(
        "change_password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    # Профиль пользователя
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/edit/", UserProfileUpdateView.as_view(), name="user-profile-edit"),
    # Управление пользователями (для админов)
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/update", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete>", UserDeleteView.as_view(), name="user-delete"),
    # Адреса доставки
    path("addresses/", UserAddressListView.as_view(), name="address-list"),
    path("addresses/create/", UserAddressCreateView.as_view(), name="address-create"),
    path(
        "addresses/<int:pk>/update/",
        UserAddressUpdateView.as_view(),
        name="address-update",
    ),
    path(
        "addresses/<int:pk>/delete/",
        UserAddressDeleteView.as_view(),
        name="address-delete",
    ),
    # Верификация email
    path(
        "email-verify/<uidb64>/<token>/", EmailVerifyView.as_view(), name="email-verify"
    ),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification",
    ),
    # API
    path(
        "api/address-autocomplete/",
        AddressAutocompleteView.as_view(),
        name="address-autocomplete",
    ),
]
