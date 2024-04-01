"""
Utility functions for the Habit application.

This module contains various utility functions used across the Habit application.
These functions include conversion functions and other helper methods.
"""


from datetime import timedelta
from django.utils import timezone
from .models import TaskTracker, Habit, Streak
from functools import partial
from habit.models import TaskTracker, Achievement
from django.db.models import Min



def all_tracked_habits(user_id):
    return Habit.objects.filter(user_id=user_id,
                                completion_date__gte=timezone.now()
                                ).prefetch_related('streak')

                                
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


def longest_streak_for_habit(habit_id):
    return Habit.objects.filter(habit_id=habit_id).prefetch_related('streak')



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


def active_tasks(user_id):
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


def extract_first_failed_task(updated_task_ids):
    """
    Extracts the first failed task for each habit based on updated task IDs.

    Args:
        updated_task_ids (list): List of updated task IDs.

    Returns:
        list: List of first failed tasks for each habit.
    """
    # Annotate the minimum task number for each habit
    min_task_numbers = TaskTracker.objects.filter(
        id__in=updated_task_ids
        ).values('habit_id').annotate(min_task_number=Min('task_number'))

    # Fetch the first failed task for each habit using the annotated minimum task number
    first_failed_tasks = TaskTracker.objects.filter(
        id__in=updated_task_ids, 
        task_number__in=min_task_numbers.values('min_task_number')
        ).order_by('habit_id')

    return first_failed_tasks


def update_user_activity(user_id):
    # Update task status, and achievements
    updated_habit_tasks_ids = TaskTracker.update_task_statuses(user_id=user_id)
    updated_habit_ids, updated_task_ids = updated_habit_tasks_ids

    # Escape and quote task IDs for safe use
    # Define the SQL query with a placeholder for the parameter.
    # Using a window function to calculate the rank based on the task number.
    # This allows us to rank tasks within each habit, which is necessary to identify
    # The first failed task for each habit is used later to correctly identify
    # when the user breaks a Habit streak.
    first_failed_tasks = extract_first_failed_task(updated_task_ids)
    
    # Update achievements if failed task
    Achievement.update_achievements(first_failed_tasks)
    Streak.update_streak(updated_habit_ids)

