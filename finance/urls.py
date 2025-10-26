from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload'),
    path('result/<int:file_id>/', views.result, name='result'),
    path('tax/', views.tax_calculator, name='tax'),
    path('set_goal/', views.set_goal, name='set_goal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]