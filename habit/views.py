from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import HabitForm
from .models import Task, Habit, Streak
from .utils import calculate_progress
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from Users.utils import update_profile
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone
from django.contrib.auth.models import User


@login_required
def home_view(request):
    """
    View function to display the user's home page with tasks due today and available tasks.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response.
    """
    # update task status, current streak, longest streak
    user_id = request.user.id
    updated_habit_ids = Task.update_task_statuses(user_id=user_id)
    Streak.update_streak(updated_habit_ids)

    user_full_name = ""
    try:
        user = User.objects.get(id=user_id)
        user_full_name = user.get_full_name()
    except User.DoesNotExist:
        pass


    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        habit_id = request.POST.get('habit_id')
        task_status = request.POST.get('task_status')

        try:
            task = Task.objects.get(id=task_id)
            task.task_status = 'Completed'
            task.save()

            if task and task_status == 'Completed':
                habit = Habit.objects.get(id=habit_id)
                streak = Streak.objects.get(habit_id=habit_id)
                streak.current_streak += 1
                streak.num_of_completed_tasks += 1
                habit.num_of_completed_tasks += 1

                habit.save()
                streak.save()

                messages.success(request, f'Task marked as done')

                return redirect('habit-home')
            
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'})

    now = timezone.now()
    twenty_four_hours = now + timedelta(hours=24)

    # Query tasks due today
    due_today_tasks = Task.objects.filter(
        habit__user_id=user_id, 
        due_date__range=(now, twenty_four_hours), 
        task_status='In progress'
        )
    
    # Query tasks that are available to start
    available_tasks = Task.objects.filter(
        habit__user_id=user_id,
        task_status='In progress',
        start_date__lte=now,
        due_date__gt=now
        )   

    context = {
        'daily_tasks' : due_today_tasks,
        'weekly_tasks' : available_tasks,
        'user_full_name' : user_full_name.split()[0].capitalize()
    }
    
    return render(request, 'home.html', context)


@login_required
def add_habit(request):
    """
    View function to handle adding a new habit.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response.
    """
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
            habit.user = request.user
            habit.save()
            
            # Create tasks with their due and start dates for the habit
            Task.create_due_dates(habit)
            Streak.initiate_streak(habit)
            
            # Update user's profile
            update_profile(request.user)
            
            habit_name = form.cleaned_data.get('name')
            messages.success(request, f'{habit_name} Habit created')
            return redirect('habit-home')
    else:
        form = HabitForm()

    return render(request, 'add_habit.html', {'form': form})


@login_required
def active_habits(request):
    """
    View function to display active habits for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response.
    """
    user_id = request.user.id
    all_active_habits = Habit.objects.filter(user_id=user_id, completion_date__gte=timezone.now()).prefetch_related('streak')
    daily_active_habits = all_active_habits.filter(period='daily')
    monthly_active_habits = all_active_habits.filter(period='monthly')
    weekly_active_habits = all_active_habits.filter(period='weekly')

    # Calculate progress percentage for each active habit
    calculate_progress(all_active_habits)
    calculate_progress(daily_active_habits)
    calculate_progress(monthly_active_habits)
    calculate_progress(weekly_active_habits)

    context = {
        'active_habits': all_active_habits,
        'monthly_active_habits': monthly_active_habits,
        'weekly_active_habits': weekly_active_habits,
        'daily_active_habits': daily_active_habits,
    }
    return render(request, 'active_habits.html', context)


def habit_detail(request , habit_id):
    habit = Habit.objects.get(pk=habit_id)
    tasks = Task.objects.filter(habit_id=habit_id)
    streak = Streak.objects.get(habit_id=habit_id)

    context = {
        'habit' : habit,
        'tasks' : tasks,
        'streak' : streak
    }

    return render(request, 'habit_details.html', context)

def about(request):
    """
    View function to display the About page.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response.
    """
    return render(request, 'about.html', {'title': 'About'})

