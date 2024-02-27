from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import HabitForm
from .models import Task
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from Users.utils import update_profile


@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            if not form.is_goal_achievable():
                messages.error(request, "The frequency results in a goal that is not achievable. Choose a longer goal.")
                return render(request, 'add_habit.html', {'form': form})
            
            if not form.is_valid_habit_name(request.user):
                messages.error(request, "You already used that name for another habit")
                return render(request, 'add_habit.html', {'form': form})
            
            habit = form.save(commit=False)
            habit.user = request.user  # Assuming you're using user authentication
            habit.save()
            
            task_instance = Task(habit=habit)
            task_instance.create_due_dates(habit)
            task_instance.save()

            update_profile(request.user)
            
            habit_name = form.cleaned_data.get('name')
            messages.success(request, f'{habit_name} Habit created')
            return redirect('habit-home')  # Redirect to the dashboard or habit list page
    else:
        form = HabitForm()

    return render(request, 'add_habit.html', {'form': form})
    Users.profile(request)


# Create your views here.
@login_required
def home_view(request):
    user_id = request.user.id
    now = datetime.now()
    twenty_four_hours_ago = now + timedelta(hours=24)
    seven_days_ago = now + timedelta(hours=168)
    thirty_days_ago = now + timedelta(hours=720)
    
    daily_tasks = Task.objects.filter(habit__user_id=user_id, due_date__range=(now, twenty_four_hours_ago))
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



