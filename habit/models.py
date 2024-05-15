from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import convert_period_to_days


class Habit(models.Model):
    """
    Represents a habit tracked by the user.

    Attributes
    ----------
    name : str
        The name of the habit.
    frequency : int
        The frequency of performing the habit.
    period : str
        The period over which the habit is frequently (i.e. frequency) performed.
    goal : int
        The number of days to complete a habit.
    num_of_tasks : int
        The total number of tasks for the habit.
    num_of_completed_tasks : int
        The number of completed tasks.
    notes : str
        Additional notes for the habit.
    creation_time : DateTime
        The timestamp when the habit was created.
    completion_date : DateTime
        The timestamp when the habit is expected to be completed.
    user : User
        The user who owns the habit.
    """

    name = models.CharField(max_length=255)
    frequency = models.IntegerField(default= 1)
    period = models.CharField(max_length=255)
    goal = models.IntegerField(default=90)
    num_of_tasks = models.IntegerField()
    notes = models.CharField(max_length=255, default=None)
    creation_time = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        """
        Overrides the save method to perform calculations before saving the object.

        Calculates the number of tasks required to achieve the habit's goal based on the specified period
        and frequency. If the completion date is not provided, it calculates it based on the goal.

        Parameters
        ----------
        *args
            Additional positional arguments.
        **kwargs
            Additional keyword arguments.
        """
 
        self.name = self.name.lower()

        # Calculate the completion date based on the goal
        if not self.completion_date:
            self.completion_date = self.start_date + timedelta(days=self.goal)

        # Calculate the number of tasks needed to achieve the habit goal
        num_of_period = convert_period_to_days(self.period)
        if not self.num_of_tasks:
            self.num_of_tasks = (self.goal // num_of_period) * self.frequency


        super().save(*args, **kwargs)


class TaskTracker(models.Model):
    """
    Represents a tracker for habit-related tasks.

    Attributes
    ----------
    habit : Habit
        The habit associated with the task.
    start_date : DateTime
        The start date of the task.
    due_date : DateTime
        The due date of the task.
    task_number : int
        The number of the task.
    task_status : str
        The status of the task.
    task_completion_date : DateTime
        The completion date of the task.
    """

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    task_number = models.IntegerField()
    task_status = models.CharField(max_length=255)
    task_completion_date = models.DateTimeField(null=True, blank=True)


    @classmethod
    def create_tasks(cls, habit, n=0):
        """
        Populates the TaskTracker table with tasks for a given habit.

        Generates tasks for the specified habit and inserts them into 
        the TaskTracker table, assigning due dates and task numbers 
        based on the habit's creation time, goal, and frequency.

        Parameters
        ----------
        habit : Habit
            The habit for which tasks are to be created.
        n : int, optional
            The starting task number. Defaults to 0.
        """

        # Calculate the time between tasks
        time_jump = habit.goal / habit.num_of_tasks
        time_skip = timedelta(hours=time_jump*24)

        # Initialize start and due dates for tasks
        due_date = start_date = habit.start_date
        default= 'In progress'

        # Increment the due_date and start_date by time_skip,
        # skip the first iteration for start_date
        for i in range(n+1, habit.num_of_tasks+(n+1)):
            due_date += time_skip
            if i == n+1:
                current_start_date = start_date
            else:
                current_start_date += time_skip
            cls.objects.create(habit=habit, due_date=due_date, task_number=i,
                               task_status=default, start_date=current_start_date)



    @classmethod
    def update_failed_tasks(cls, user_id):
        """
        Updates task statuses based on due dates for a specific user.

        Updates the status of tasks that are overdue (i.e., their due date is in the past)
        for the specified user.

        Parameters
        ----------
        user_id : int
            The ID of the user for whom tasks should be updated.

        Returns
        -------
        Tuple[List[int], List[int]]
            A tuple containing two lists:
                - A list of habit IDs that have tasks updated to 'Failed'.
                - A list of task IDs that have been updated to 'Failed'.
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


class Streak(models.Model):
    """
    Represents a streak associated with a habit.

    Attributes
    ----------
    habit : Habit
        The habit associated with the streak.
    num_of_completed_tasks : int
        The number of completed tasks in the streak.
    num_of_failed_tasks : int
        The number of failed tasks in the streak.
    longest_streak : int
        The longest streak achieved.
    current_streak : int
        The current streak.
    """
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='streak')
    num_of_completed_tasks = models.IntegerField(default=0)
    num_of_failed_tasks = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to update the longest streak.

        Checks if the current streak is longer than the longest streak
        and updates the longest streak accordingly before saving the Streak instance.

        Parameters
        ----------
        *args
            Additional positional arguments.
        **kwargs
            Additional keyword arguments.
        """
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        super().save(*args, **kwargs)

    @classmethod
    def num_completed_tasks(cls, habit):
        """
        Update the number of completed tasks for a habit and update the streak.

        Parameters
        ----------
        habit : Habit
            The habit for which the number of completed tasks is to be updated.

        Returns
        -------
        None

        Notes
        -----
        This method counts the number of completed tasks for the specified habit in the TaskTracker 
        table and updates the num_of_completed_tasks attribute in the associated streak object.
        """
        completed_num = TaskTracker.objects.filter(habit=habit, task_status='Completed').count()
        streak = habit.streak.first()
        streak.num_of_completed_tasks = completed_num
        streak.save()

    @classmethod
    def update_streak(cls, habit_ids):
        """
        Updates streak information for specified habit IDs.

        This class method updates the streak information for the specified habit IDs.
        It resets the current streak to zero and increments the number of failed tasks
        for each habit.

        Parameters
        ----------
        habit_ids : list
            A list of habit IDs to update streak information for.
        """

        for habit_id in habit_ids:
            habit_streak = cls.objects.get(habit_id=habit_id)
            habit_streak.num_of_failed_tasks += 1
            habit_streak.current_streak = 0
            habit_streak.save()


class Achievement(models.Model):
    """
    Represents an achievement associated with a habit.

    Attributes
    ----------
    habit : Habit
        The habit associated with the achievement.
    streak_length : int
        The length of the streak associated with the achievement.
    title : str
        The title of the achievement.
    date : DateTime
        The date of the achievement.
    """
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='achievement')
    streak_length = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    date = models.DateTimeField(null=True, blank=True)


    @classmethod
    def update_achievements(cls, tasks):
        """
        Update achievements for habits when a user breaks their streak.

        This method updates the achievements associated with habits 
        when a user fails to maintain their streak. It iterates through 
        the provided tasks and creates an Achievement object for each 
        habit where the streak has been broken.

        Parameters
        ----------
        tasks : QuerySet
            A queryset containing TaskTracker objects representing the tasks associated with habits.
        """
        for task in tasks:
            # Check if the task number is greater than 1 to avoid index out of range error
            if task.task_number > 1:
                prev_task = TaskTracker.objects.get(task_number=task.task_number - 1)
                # Check if the previous task was failed to avoid repeating Break habit title
                if prev_task.task_status == 'Failed':
                    continue
            streak = task.habit.streak.get()
            # Check if the streak is not None and its current_streak is not 0
            if streak and streak.current_streak != 0:
                title = 'Break The Habit'
                # Assign the streak length from the fetched streak information
                streak_length = streak.current_streak if streak else 0
                cls.objects.create(habit=task.habit, date=task.due_date,
                                    title=title, streak_length=streak_length)


    @classmethod
    def rewards_streaks(cls, habit_id, streak):
        """
        Reward streaks when they reach predefined milestones.

        This method rewards streaks when they achieve specific milestones, 
        such as 7, 14, or 30 days.
        It creates Achievement instances for the specified habit when the 
        streak reaches each milestone.

        Parameters
        ----------
        habit_id : int
            The ID of the habit associated with the streak.
        streak : Streak
            The streak object representing the current streak.
        """
        habit = Habit.objects.get(pk=habit_id)  # Retrieve the Habit instance using the habit_id

        if streak.current_streak / habit.frequency == 7 and habit.period == 'daily':
            title = '7-Day Streak'
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak / habit.frequency == 14 and habit.period == 'daily':
            title = '14-Day Streak'
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak / habit.frequency == 30 and habit.period == 'daily':
            title = '30-Day Streak'
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)

        # Weekly Achievements
        if habit.period == 'weekly' and (streak.current_streak / habit.frequency) == 1 :
            title = '1-Week Streak'
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if (streak.current_streak / habit.frequency) == 2 and habit.period == 'weekly':
            title = "2-Week's Streak"
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if (streak.current_streak / habit.frequency) == 4 and habit.period == 'weekly':
            title = "4-Week's Streak"
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)

        # Monthly Achievements
        if streak.current_streak // habit.frequency == 1  and habit.period == 'monthly':
            title = '1-Month Streak'
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak // habit.frequency == 2 and habit.period == 'monthly':
            title = "2-Month's Streak"
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)
        if streak.current_streak // habit.frequency == 4 and habit.period == 'monthly':
            title = "4-Month's Streak"
            cls.objects.create(habit=habit, date=timezone.now(), title=title,
                               streak_length=streak.current_streak)