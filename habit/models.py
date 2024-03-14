from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone



class Habit(models.Model):
    name = models.CharField(max_length=255)
    frequency = models.IntegerField(default= 1)
    period = models.CharField(max_length=255)
    goal = models.IntegerField(default=90)
    num_of_tasks = models.FloatField()
    num_of_completed_tasks = models.FloatField(default = 0)
    notes = models.CharField(max_length=255, default=None)
    creation_time = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        """
        Override the save method to calculate tasks number and completion_date.

        """
        self.name = self.name.lower()
        num_of_period = 1 
        if self.period == 'daily':
            num_of_period = 1
        elif self.period == 'weekly':
            num_of_period = 7
        elif self.period == 'monthly':
            num_of_period = 30
        elif self.period == 'annual':
            num_of_period = 365

        # Calculate the number of tasks needed to achieve the habit goal
        if not self.num_of_tasks:
            self.num_of_tasks = ((self.goal // num_of_period) * self.frequency)

        # Calculate the completion date based on the goal
        if not self.completion_date:
            self.completion_date = datetime.now() + timedelta(hours=self.goal*24)

        super().save(*args, **kwargs)



class Task(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    task_number = models.IntegerField(default=77)
    period_col = models.CharField(max_length=255, default='nontype')
    task_status = models.CharField(max_length=255, default='In progress')


    def save(self, *args, **kwargs):
        """
        Override the save method to mark tasks as failed if due_date is passed
        and the task is not marked as completed
        
        """
        if self.due_date:
            if self.due_date < timezone.now() and self.task_status != 'Completed':
                self.task_status = 'failed'

        super().save(*args, **kwargs)


    @classmethod
    def create_due_dates(cls, habit):
        """
        Populate Task table with habit tasks and thier due dates 

        """
        # Calculate the time between a tasks
        time_jump = habit.goal / habit.num_of_tasks
        time_skip = timedelta(hours=time_jump*24)
        
        # Determine the periodicity of tasks
        period_col = ''
        if time_skip == timedelta(hours=24):
            period_col = 'daily'
        elif time_skip>timedelta(hours=24) and  time_skip < timedelta(hours=192):
            period_col = 'weekly'
        elif time_skip>timedelta(hours=168) and  time_skip<= timedelta(hours=720):
            period_col = 'monthly'

        # Initialize start and due dates for tasks
        due_date = start_date = habit.creation_time

        # Increment the due_date and start_date by time_skip, skip the first iteration for start_date
        for i in range(1, habit.num_of_tasks + 1):
            due_date += timedelta(hours=time_jump*24)
            if i == 1:
                current_start_date = start_date
            else:
                current_start_date += timedelta(hours=time_jump * 24)

            cls.objects.create(habit=habit, due_date=due_date, task_number=i, period_col=period_col, start_date=current_start_date)


