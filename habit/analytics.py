"""
Utility functions for the Habit application.

This module contains various utility functions used across the Habit application.
These functions include conversion functions and other helper methods.
"""


from datetime import timedelta
from django.utils import timezone
from .models import TaskTracker


def due_today_tasks(user_id):
    """
    Retrieve tasks due today for a given user.

    Args:
        user_id (int): The ID of the user for whom tasks are to be retrieved.

    Returns:
        QuerySet: A queryset containing tasks due today for the user.

    """
    # Query tasks due today to be completed
    now = timezone.now()
    twenty_four_hours = now + timedelta(hours=24)
    due_today = TaskTracker.objects.filter(
        habit__user_id=user_id,
        due_date__range=(now, twenty_four_hours),
        task_status='In progress'
    )
    return due_today


def available_tasks(user_id):
    """
    Retrieve available tasks for a given user.

    Args:
        user_id (int): The ID of the user for whom tasks are to be retrieved.

    Returns:
        QuerySet: A queryset containing available tasks for the user.

    """
    now = timezone.now()
    # Query tasks that are available to be completed
    tasks = TaskTracker.objects.filter(
        habit__user_id=user_id,
        task_status='In progress',
        start_date__lte=now,
        due_date__gt=now
    )
    return tasks


def habit_by_period(habits):
    """
    Group habits by their periods.

    Args:
        habits (QuerySet): A queryset containing habits.

    Returns:
        tuple: A tuple containing three querysets:
               - daily_active_habits: Habits with 'daily' period.
               - weekly_active_habits: Habits with 'weekly' period.
               - monthly_active_habits: Habits with 'monthly' period.

    """
    daily_active_habits = habits.filter(period='daily')
    monthly_active_habits = habits.filter(period='monthly')
    weekly_active_habits = habits.filter(period='weekly')
    return (daily_active_habits, weekly_active_habits, monthly_active_habits)


def calculate_progress(habits):
    """
    Calculate progress percentage for each active habit.

    Args:
        habits (QuerySet): A queryset containing active habits.

    """
    # Calculate progress percentage for each active habit
    for habit in habits:
        if habit.num_of_tasks > 0:
            habit.progress_percentage = round(
                (habit.num_of_completed_tasks / habit.num_of_tasks) * 100, 2)
        else:
            habit.progress_percentage = 0.0
