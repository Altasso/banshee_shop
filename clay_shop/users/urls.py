from django.urls import path

from .views import (
    UserAddressCreateView,
    UserAddressDeleteView,
    UserAddressListView,
    UserAddressUpdateView,
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("users/create", UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/update", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete>", UserDeleteView.as_view(), name="user-delete"),
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
