from django.urls import path

from .views import (
    AuthLoginView,
    AuthLogoutView,
    UserAddressCreateView,
    UserAddressDeleteView,
    UserAddressListView,
    UserAddressUpdateView,
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserProfileUpdateView,
    UserProfileView,
    UserUpdateView, UserRegistrationView,
)

urlpatterns = [
    # Аутентификация
    path("login/", AuthLoginView.as_view(), name="login"),
    path("logout/", AuthLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="user-create"),
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
]
