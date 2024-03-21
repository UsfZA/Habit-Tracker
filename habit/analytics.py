from django.utils import timezone
from datetime import timedelta
from .models import Task


def due_today_tasks(user_id):
    # Query tasks due today to be completed
    
    now = timezone.now()
    twenty_four_hours = now + timedelta(hours=24)
    due_today_tasks = Task.objects.filter(
        habit__user_id=user_id, 
        due_date__range=(now, twenty_four_hours), 
        task_status='In progress'
    )
    return due_today_tasks

def available_tasks(user_id):
    
    now = timezone.now()
    # Query tasks that are available to be completed
    available_tasks = Task.objects.filter(
        habit__user_id=user_id,
        task_status='In progress',
        start_date__lte=now,
        due_date__gt=now
    )
    return available_tasks

