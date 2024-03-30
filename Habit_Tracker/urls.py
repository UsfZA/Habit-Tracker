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




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='Users/login.html'), name='login'),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('logout', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),

    path('home/', habit_views.HabitView.habit_home, name='habit-home'),
    path('about/', habit_views.HabitView.about, name='habit-about'),

    path('addHabit/', habit_views.HabitManager.add_habit, name='habit-creation'),
    path('drophabit/<int:habit_id>/', habit_views.HabitManagerView.delete_habit, name='habit-deletion'),
    path('ActiveHabits/', habit_views.HabitManager.active_habits, name = 'active_habits'),
    path('habit/<int:habit_id>/', habit_views.HabitManagerView.habit_detail, name='habit_detail'),

    path('HabitsAnalysis/', habit_views.AnalyticView.habit_analysis_view, name = 'HabitsAnalysis'),

]
