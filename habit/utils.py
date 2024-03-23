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
    if value.endswith('d'):
        num = int(value[:-1])
    if value.endswith('w'):
        num = int(value[:-1]) * 7
    if value.endswith('y'):
        num = int(value[:-1]) * 365
    if value.endswith('m'):
        months = int(value[:-1])
        if months == 1:
            num = 30
        if months == 2:
            num = 60
        if months == 3:
            num = 90
        if months == 6:
            num = 180
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
    if value.startswith('d'):
        value_num = 1
    if value.startswith('w'):
        value_num = 7
    if value.startswith('m'):
        value_num = 30
    if value.startswith('a'):
        value_num = 365
    else:
        raise ValueError("Invalid duration format")
    return value_num






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
        ).order_by('habit_id').prefetch_related('streak')

    return first_failed_tasks
