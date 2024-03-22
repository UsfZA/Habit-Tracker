"""
Utility functions for the Habit application.

This module contains various utility functions used across the Habit application.
These functions include conversion functions and other helper methods.
"""


from django.db import connection
from habit.models import TaskTracker

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



def escape_and_quote(ids):
    """
    Escape and quote task IDs for safe use in the raw SQL query.

    This function ensures that the IDs are properly formatted and protected
    against SQL injection attacks by escaping special characters and quoting
    the IDs as necessary before using them in the SQL query.

    Args:
        ids (iterable): An iterable containing the task IDs to be escaped and quoted.

    Returns:
        str: A string containing the properly escaped and quoted task IDs, 
        suitable for use in a SQL query.
    """
    updated_tasks_id_str = ','.join(map(str, ids))
    escaped_updated_tasks_id_str = connection.ops.quote_name(updated_tasks_id_str)
    return escaped_updated_tasks_id_str


def extract_first_failed_task(updated_task_ids):
    """
    Extracts the first failed task for each habit based on updated task IDs.

    Args:
        updated_task_ids (list): List of updated task IDs.

    Returns:
        list: List of first failed tasks for each habit.
    """
    escaped_updated_tasks_ids = escape_and_quote(updated_task_ids)
    ranked_updated_tasks_query = """
        SELECT * FROM (
            SELECT *, RANK() OVER(PARTITION BY habit_id ORDER BY task_number ASC) AS rk 
            FROM habit_data_base.habit_tasktracker
            WHERE id IN (%s)
        ) AS habit_rank 
        WHERE rk = 1
    """
    first_failed_tasks = TaskTracker.objects.raw(
                                    ranked_updated_tasks_query,
                                    [escaped_updated_tasks_ids]
                                    ).prefetch_related('streak')
    return first_failed_tasks
