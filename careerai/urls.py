from django.urls import path
from . import views
from .initial_data import create_initial_data

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('mentors/', views.mentors, name='mentors'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]