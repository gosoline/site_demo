from django.urls import path, include

from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.test, name='test'),
    path('data/', views.get_data, name='get_data')
]
