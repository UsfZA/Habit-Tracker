"""Habit_Tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from Users import views as user_views
from habit import views as habit_views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('Login', auth_views.LoginView.as_view(template_name='Users/login.html'), name='login'),
    path('Register/', user_views.register, name='register'),
    path('Profile/', user_views.profile, name='profile'),
    path('Logout', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),

    path('', habit_views.HabitView.as_view(), name='habit-home'),

    path('Add-Habit/', habit_views.HabitManagerView.add_habit, name='habit_creation'),
    path('delete-habit/<int:habit_id>/', habit_views.HabitManagerView.delete_habit, name='habit_deletion'),
    path('Habit-Manager/', habit_views.HabitManagerView.active_habits, name = 'active_habits'),
    path('Habit-Infos/<int:habit_id>/', habit_views.HabitManagerView.habit_detail, name='habit_detail'),

    path('Habits-Analysis/', habit_views.HabitAnalysis.as_view(), name = 'HabitsAnalysis'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)