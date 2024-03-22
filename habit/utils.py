from django.db import connection
from .models import TaskTracker

def periodicty_number(period):   
    """
    Function to transform period to number of days
    args: periodicity string
    return: corresponding number of days
    """
    pass



def convert_goal_to_days(value):
    if value.endswith('d'):
        return int(value[:-1])
    elif value.endswith('w'):
        return int(value[:-1]) * 7
    elif value.endswith('m'):
        months = int(value[:-1])
        if months == 1:
            return 30
        elif months == 2:
            return 60
        elif months == 3:
            return 90
        elif months == 6:
            return 180
        else:
            raise ValueError("Invalid duration format")
    elif value.endswith('y'):
        return int(value[:-1]) * 365
    else:
        raise ValueError("Invalid duration format")
    
def convert_period_to_days(value : str):
    if value.startswith('d'):
        value_num = 1
    elif value.startswith('w'):
        value_num = 7
    elif value.startswith('m'):
        value_num = 30
    elif value.startswith('a'):
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
            FROM habit_data_base.habit_tasktracker
            WHERE id IN (%s)
        ) AS habit_rank 
        WHERE rk = 1
    """
    first_failed_tasks = TaskTracker.objects.raw(ranked_updated_tasks_query, [escaped_updated_tasks_ids]).prefetch_related('streak')

    
    return first_failed_tasks