"""
Utility functions for the Habit application.

This module contains various utility functions used across the Habit application.
These functions include conversion functions and other helper methods.
"""


from datetime import timedelta
from django.utils import timezone
from .models import TaskTracker, Habit, Streak
from functools import partial





def all_tracked_habits(user_id):
    return Habit.objects.all().prefetch_related('streak')


def habits_by_period(period):
    # Function to filter habits by period
    return partial(filter_habits_by_period, period)


def filter_habits_by_period(period, habits):
    # Function to filter habits by period
    return habits.filter(period=period)


def longest_streak_over_all_habits():
    """
    Retrieve habit_id of the habit with the longest streak from Streak table.

    Args:
        None.

    Returns:
        Habit_id

    """
    return Habit.objects.filter(id=Streak.objects.order_by('-longest_streak').first().habit_id).prefetch_related('streak')


def longest_current_streak_over_all_habits():
    """
    Retrieve habit_id of the habit with the longest streak from Streak table.

    Args:
        None.

    Returns:
        Habit_id

    """
    return Habit.objects.filter(id=Streak.objects.order_by('-current_streak').first().habit_id).prefetch_related('streak')



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
