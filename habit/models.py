from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone
from .utils import periodicty_number



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

        # assign a number to periodicity 
        num_of_period = periodicty_number(self.period)

        # Calculate the number of tasks needed to achieve the habit goal
        if not self.num_of_tasks:
            self.num_of_tasks = ((self.goal // num_of_period) * self.frequency)

        # Calculate the completion date based on the goal
        if not self.completion_date:
            self.completion_date = timezone.now() + timedelta(hours=self.goal*24)

        super().save(*args, **kwargs)



class Task(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    task_number = models.IntegerField()
    task_status = models.CharField(max_length=255)


    
    @classmethod
    def update_task_statuses(cls, user_id):

        """
        Class method to update task statuses based on due dates for a specific user.
        Returns a list of habit IDs that have been updated to "failed".
        """
        updated_habit_ids = []
        tasks_to_update = cls.objects.filter(habit__user_id=user_id, due_date__lt=timezone.now(), task_status='In progress')
        for task in tasks_to_update:
            task.task_status = 'Failed'
            task.save()
            updated_habit_ids.append(task.habit_id)

        return updated_habit_ids
    


    @classmethod   
    def create_due_dates(cls, habit):
        """
        Populate Task table with habit tasks and their due dates 
        """
        # Calculate the time between tasks
        time_jump = habit.goal / habit.num_of_tasks
        time_skip = timedelta(hours=time_jump*24)
        

        # Initialize start and due dates for tasks
        due_date = start_date = habit.creation_time
        default='In progress'

        # Increment the due_date and start_date by time_skip, skip the first iteration for start_date
        for i in range(1, habit.num_of_tasks+1):
            due_date += time_skip
            if i == 1:
                current_start_date = start_date
            else:
                current_start_date += time_skip
            cls.objects.create(habit=habit, due_date=due_date, task_number=i, task_status=default, start_date=current_start_date)



class Streak(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='streak')
    num_of_completed_tasks = models.IntegerField(default = 0)
    num_of_failed_tasks = models.IntegerField(default = 0)
    longest_streak = models.IntegerField(default = 0)
    current_streak = models.IntegerField(default = 0)


    def save(self, *args, **kwargs):
        # assign current streak to longest streak if its larger
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        super().save(*args, **kwargs)


    @classmethod
    def update_streak(cls, updated_habit_ids):
        """
        Class method to update the longest streak and the current streak.
        """

        # reset the currents streaks of the failed habit tasks
        for habit_id in updated_habit_ids:
            habit_streak = cls.objects.get(habit_id=habit_id)
            habit_streak.num_of_failed_tasks += 1
            habit_streak.current_streak = 0
            habit_streak.save()

    @classmethod
    def initiate_streak(cls, habit):
        cls.objects.create(habit=habit)