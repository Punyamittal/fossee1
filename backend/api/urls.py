"""
API URL routing.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('upload/', views.upload_csv),
    path('datasets/', views.dataset_list),
    path('datasets/<int:pk>/', views.dataset_detail),
    path('datasets/<int:pk>/summary/', views.dataset_summary),
    path('datasets/<int:pk>/equipment/', views.EquipmentList.as_view()),
    path('datasets/<int:pk>/generate-pdf/', views.generate_pdf),
    path('auth/login/', views.login),
    path('auth/register/', views.register),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
]
