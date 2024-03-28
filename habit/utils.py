"""
Utility functions for the Habit application.

This module contains various utility functions used across the Habit application.
These functions include conversion functions and other helper methods.
"""


from habit.models import TaskTracker
from django.db.models import Min


def convert_goal_to_days(value: str) -> int:
    """
    Convert a goal duration string to the corresponding number of days.

    Args:
        value (str): The goal duration string in the format '<number><unit>'.
                     Supported units: 'd' (days), 'w' (weeks), 'm' (months), 'y' (years).

    Returns:
        int: The number of days corresponding to the input duration.

    Raises:
        ValueError: If the input duration format is invalid.
    """

    if value == '3 days':
        num = 3
    elif value == '1 week':
        num = 7
    elif value == '1 month':
        num = 30
    elif value == '2 months':
        num = 60
    elif value == '3 months':
        num = 90
    elif value == '6 months':
        num = 180
    elif value == '1 year':
        num = 365
    else:
        raise ValueError("Invalid duration format")
    return num


def convert_period_to_days(value: str) -> int:
    """
    Convert a period string to the corresponding number of days.

    Args:
        value (str): The period string in the format '<unit>'.

    Returns:
        int: The number of days corresponding to the input period.

    Raises:
        ValueError: If the input period format is invalid.
    """
    if value == 'daily':
        num = 1
    elif value == 'weekly':
        num = 7
    elif value == 'monthly':
        num = 30
    elif value == 'annual':
        num = 365
    else:
        raise ValueError("Invalid duration format")
    return num






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
