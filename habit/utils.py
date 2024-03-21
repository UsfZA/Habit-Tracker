from django.db import connection
from .models import Task

def periodicty_number(period):   
    """
    Function to transform period to number of days
    args: periodicity string
    return: corresponding number of days
    """
    pass

def calculate_progress(habits):
    # Calculate progress percentage for each active habit
    for habit in habits:
        if habit.num_of_tasks > 0:
            habit.progress_percentage = round((habit.num_of_completed_tasks / habit.num_of_tasks) * 100, 2)
        else:
            habit.progress_percentage = 0.0

def escape_and_quote(ids):
    """
    Escape and quote task IDs for safe use in the raw SQL query.

    This function ensures that the IDs are properly formatted and protected
    against SQL injection attacks by escaping special characters and quoting
    the IDs as necessary before using them in the SQL query.

    Args:
        ids (iterable): An iterable containing the task IDs to be escaped and quoted.

    Returns:
        str: A string containing the properly escaped and quoted task IDs, suitable for use in a SQL query.
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
            FROM habit_data_base.habit_task
            WHERE id IN (%s)
        ) AS habit_rank 
        WHERE rk = 1
    """
    first_failed_tasks = Task.objects.raw(ranked_updated_tasks_query, [escaped_updated_tasks_ids]).prefetch_related('streak')

    
    return first_failed_tasks
