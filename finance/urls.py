from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload'),
    path('result/<int:file_id>/', views.result, name='result'),
    path('tax/', views.tax_calculator, name='tax'),
]