from django.contrib import admin
from django.urls import path

from seller import views

urlpatterns = [
    path('seller/', views.dashboard_view),
]
