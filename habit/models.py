from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime



class Habit(models.Model):
    name = models.CharField(max_length=255)
    frequency = models.IntegerField(default= 1)
    number_of_times = models.IntegerField(default=1)
    period = models.CharField(max_length=255)
    goal = models.IntegerField(default=90)
    num_of_tasks = models.FloatField()
    notes = models.CharField(max_length=255, default=None)
    creation_time = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        num = 1  # Initialize 'num' with a default value
        if self.period == 'daily':
            num = 1
        elif self.period == 'weekly':
            num = 7
        elif self.period == 'monthly':
            num = 30
        elif self.period == 'annual':
            num = 365

        if not self.num_of_tasks:
            self.num_of_tasks = ((self.goal // (num * self.number_of_times)) * self.frequency)

        if not self.completion_date:
            # Check if self.completion_date is None before performing addition
            self.completion_date = datetime.now() + timedelta(hours=self.goal*24)

        super().save(*args, **kwargs)



class Task(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    due_date = models.DateTimeField(null=True, blank=True)
    task_number = models.IntegerField(default=77)
    period_col = models.CharField(max_length=255, default='nontype')

    @classmethod
    def create_due_dates(cls, habit):
        time_jump = habit.goal / habit.num_of_tasks
        create_date = habit.creation_time
        time_skip = timedelta(hours=time_jump*24)
        period_col = ''
        if time_skip == timedelta(hours=24):
            period_col = 'daily'
        elif time_skip>timedelta(hours=24) and  time_skip < timedelta(hours=192):
            period_col = 'weekly'
        elif time_skip>timedelta(hours=168) and  time_skip<= timedelta(hours=720):
            period_col = 'monthly'

        for i in range(1, habit.num_of_tasks + 1):
            create_date += timedelta(hours=time_jump*24)
            cls.objects.create(habit=habit, due_date=create_date, task_number=i, period_col=period_col)
