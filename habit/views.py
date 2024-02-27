from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import HabitForm
from .models import Task
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user  # Assuming you're using user authentication
            habit.save()
            
            task_instance = Task(habit=habit)
            task_instance.create_due_dates(habit)
            task_instance.save()
            
            habit_name = form.cleaned_data.get('name')
            messages.success(request, f'{habit_name} Habit created')
            return redirect('habit-home')  # Redirect to the dashboard or habit list page
    else:
        form = HabitForm()

    return render(request, 'add_habit.html', {'form': form})


# Create your views here.
@login_required
def home_view(request):
    user_id = request.user.id
    now = datetime.now()
    twenty_four_hours_ago = now + timedelta(hours=24)
    seven_days_ago = now + timedelta(hours=168)
    thirty_days_ago = now + timedelta(hours=720)
    
    daily_tasks = Task.objects.filter(habit__user_id=user_id, period_col='daily', due_date__range=(now, twenty_four_hours_ago))
    weekly_tasks = Task.objects.filter(habit__user_id=user_id, period_col='weekly', due_date__range=(now, seven_days_ago))
    monthly_tasks = Task.objects.filter(habit__user_id=user_id, period_col='monthly', due_date__range=(now, thirty_days_ago))
    context = {
        'daily_tasks' : daily_tasks,
        'weekly_tasks' : weekly_tasks,
        'monthly_tasks' : monthly_tasks
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html', {'title': 'About'})



