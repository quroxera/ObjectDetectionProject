from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_image_feed/', views.add_image_view, name='add_image_feed'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('process/<int:image_id>/', views.process_image_view, name='process_image'),
    path('delete/<int:image_id>/', views.delete_image_view, name='delete_image'),
]