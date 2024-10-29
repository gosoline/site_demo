from django.urls import path, include

from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('index/', views.index, name='首页'),
    path('data/', views.get_data, name='获取数据'),
    path('fault_statistics/', views.fault_statistics, name='故障统计'),
    path('vibration_analysis/', views.vibration_analysis, name='振动分析'),
]
