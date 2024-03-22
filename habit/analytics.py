from django.utils import timezone
from datetime import timedelta
from .models import TaskTracker




def due_today_tasks(user_id):
    # Query tasks due today to be completed
    
    now = timezone.now()
    twenty_four_hours = now + timedelta(hours=24)
    due_today_tasks = TaskTracker.objects.filter(
        habit__user_id=user_id, 
        due_date__range=(now, twenty_four_hours), 
        task_status='In progress'
    )
    return due_today_tasks

def available_tasks(user_id):
    
    now = timezone.now()
    # Query tasks that are available to be completed
    available_tasks = TaskTracker.objects.filter(
        habit__user_id=user_id,
        task_status='In progress',
        start_date__lte=now,
        due_date__gt=now
    )
    return available_tasks

def habit_by_period(habits):
        daily_active_habits = habits.filter(period='daily')
        monthly_active_habits = habits.filter(period='monthly')
        weekly_active_habits = habits.filter(period='weekly')
        return (daily_active_habits, weekly_active_habits, monthly_active_habits)


def calculate_progress(habits):
    # Calculate progress percentage for each active habit
    for habit in habits:
        if habit.num_of_tasks > 0:
            habit.progress_percentage = round((habit.num_of_completed_tasks / habit.num_of_tasks) * 100, 2)
        else:
            habit.progress_percentage = 0.0