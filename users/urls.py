from django.urls import path
from .views import user_preferences_view
from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    #path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    #path('update_preferences/', update_preferences, name='update_preferences'),
    path('preferences/', user_preferences_view, name='user_preferences'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]