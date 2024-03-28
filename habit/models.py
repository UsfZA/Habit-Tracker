from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q


class Habit(models.Model):
    name = models.CharField(max_length=255)
    frequency = models.IntegerField(default= 1)
    period = models.CharField(max_length=255)
    goal = models.IntegerField(default=90)
    num_of_tasks = models.IntegerField()
    num_of_completed_tasks = models.IntegerField(default = 0)
    notes = models.CharField(max_length=255, default=None)
    creation_time = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Override the save method to calculate tasks number and completion_date.

        """
        from .utils import convert_period_to_days
        self.name = self.name.lower()

        num_of_period = convert_period_to_days(self.period)

        # Calculate the number of tasks needed to achieve the habit goal
        if not self.num_of_tasks:
            self.num_of_tasks = (self.goal // num_of_period) * self.frequency

        # Calculate the completion date based on the goal
        if not self.completion_date:
            self.completion_date = timezone.now() + timedelta(hours=self.goal*24)

        super().save(*args, **kwargs)


class TaskTracker(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    task_number = models.IntegerField()
    task_status = models.CharField(max_length=255)
    task_completion_date = models.DateTimeField(null=True, blank=True)


    @classmethod
    def update_task_statuses(cls, user_id):
        """
        Update task statuses based on due dates for a specific user.

        This class method updates the status of tasks that are overdue 
        (i.e., their due date is in the past) for the specified user. 

        Args:
            user_id (int): The ID of the user for whom tasks should be updated.

        Returns:
            Tuple[List[int], List[int]]: A tuple containing two lists:
                - A list of habit IDs that have tasks updated to 'Failed'.
                - A list of task IDs that have been updated to 'Failed'.

        Note:
            The method marks tasks as 'Failed' if their due date is in the 
            past and their status is not 'Completed'.
        """
        updated_habit_ids = []
        updated_task_ids = []
        tasks_to_update = cls.objects.filter(habit__user_id=user_id,
                                            due_date__lt=timezone.now(),
                                            task_status='In progress')
        for task in tasks_to_update:
            task.task_status = 'Failed'
            task.task_completion_date = task.due_date
            task.save()
            updated_habit_ids.append(task.habit_id)
            updated_task_ids.append(task.id)
        return (updated_habit_ids, updated_task_ids)


    @classmethod
    def create_tasks(cls, habit, r=0):
        """
        Populate Task table with habit tasks and their due dates 
        """
        # Calculate the time between tasks
        time_jump = habit.goal / habit.num_of_tasks
        time_skip = timedelta(hours=time_jump*24)

        # Initialize start and due dates for tasks
        due_date = start_date = habit.creation_time
        default='In progress'

        # Increment the due_date and start_date by time_skip,
        # skip the first iteration for start_date
        for i in range(r+1, habit.num_of_tasks+(r+1)):
            due_date += time_skip
            if i == r+1:
                current_start_date = start_date
            else:
                current_start_date += time_skip
            cls.objects.create(habit=habit, due_date=due_date, task_number=i,
                               task_status=default, start_date=current_start_date)


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
        """
        intiate streak instance to be incremented
        """
        cls.objects.create(habit=habit)


class Achievement(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    streak_length = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    date = models.DateTimeField(null=True, blank=True)

    @classmethod
    def update_achievements(cls, tasks):
        """
        Update achievements when a user breaks a habit.
        """
        for task in tasks:
            title = 'Break The Habit'
            # Fetch the streak information associated with the habit
            streak = cls.get_habit_streak(task.habit)
            # Assign the streak length from the fetched streak information
            streak_length = streak.longest_streak if streak else 0
            cls.objects.create(habit=task.habit, date=task.due_date,
                               title=title, streak_length=streak_length)

    @classmethod
    def get_habit_streak(cls, habit):
        """
        Fetch the streak information associated with the given habit.

        Args:
            habit (Habit): The habit for which to fetch the streak information.

        Returns:
            Streak: The streak information associated with the habit.
        """
        # Fetch the related Streak object associated with the habit
        try:
            streak = habit.streak.get()
            return streak
        except Streak.DoesNotExist:
            return None


    @classmethod
    def rewards_streaks(cls, habit_id, streak):
        """
        reward streaks when it reaches a defined echievements
        """
        if streak.current_streak == 7:
            title = '7-Day Streak'
            habit = Habit.objects.get(pk=habit_id)  # Retrieve the Habit instance using the habit_id
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak == 14:
            title = '14-Day Streak'
            habit = Habit.objects.get(pk=habit_id)  # Retrieve the Habit instance using the habit_id
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak == 30:
            title = '30-Day Streak'
            habit = Habit.objects.get(pk=habit_id)  # Retrieve the Habit instance using the habit_id
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
            