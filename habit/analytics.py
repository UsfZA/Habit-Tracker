"""
This module includes functions for analyzing habit data, such as calculating progress,
extracting first failed tasks, updating user activity, and ranking habits based on scores.

This module contains various utility functions used across the Habit application.
These functions include retrieval of tracked habits, filtering habits by period,
calculation of progress percentage, updating task statuses and achievements,
calculation of habit scores, normalization of scores, ranking of habits based on scores,
and analysis of habit data.


"""

from datetime import timedelta
from functools import partial
import numpy as np
from django.utils import timezone
from django.db.models import Min, Prefetch
from habit.models import TaskTracker, Habit, Streak, Achievement


def all_tracked_habits(user_id):
    """
    Retrieve all tracked habits for a given user.

    Parameters
    ----------
    user_id : int
        The ID of the user for whom habits are to be retrieved.

    Returns
    -------
    QuerySet
        A queryset containing all tracked habits for the user, including streak information.

    """
    return Habit.objects.filter(user_id=user_id,
                                completion_date__gte=timezone.now()
                                ).prefetch_related('streak')


def habits_by_period(period):
    """
    Return a function to filter habits by period.

    Parameters
    ----------
    period : str
        The period to filter habits by.

    Returns
    -------
    function
        A function that can be used to filter habits by the specified period.

    """
    return partial(filter_habits_by_period, period)


def filter_habits_by_period(period, habits):
    """
    Filter habits by a specified period.

    Parameters
    ----------
    period : str
        The period to filter habits by.
    habits : QuerySet
        A queryset containing habits to be filtered.

    Returns
    -------
    QuerySet
        A filtered queryset containing habits filtered by the specified period.

    """
    return habits.filter(period=period)


def longest_current_streak_over_all_habits():
    """
    Retrieve the habit ID of the habit with the longest current streak from the Streak table.

    Returns
    -------
    int
        The habit ID of the habit with the longest current streak.

    """
    first_streak = Streak.objects.order_by('-current_streak').first()
    if first_streak is None:
        return Habit.objects.none()  # Return an empty queryset if no streaks are found
    return Habit.objects.filter(id=first_streak.habit_id).prefetch_related('streak')


def longest_streak_over_all_habits():
    """
    Retrieve the habit ID of the habit with the longest streak from the Streak table.

    Returns
    -------
    int
        The habit ID of the habit with the longest streak.

    """
    first_streak = Streak.objects.order_by('-longest_streak').first()
    if first_streak is None:
        return Habit.objects.none()  # Return an empty queryset if no streaks are found
    return Habit.objects.filter(id=first_streak.habit_id).prefetch_related('streak')

def longest_streak_for_habit(id):
    """
    Retrieve the longest streak for a specific habit.

    Parameters
    ----------
    id : int
        The ID of the habit for which the longest streak is to be retrieved.

    Returns
    -------
    Habit
        The habit object with the longest streak, including streak information.

    """
    return Habit.objects.prefetch_related('streak').get(id=id)


def due_today_tasks(user_id):
    """
    Retrieve tasks due today for a given user.

    Parameters
    ----------
    user_id : int
        The ID of the user for whom tasks are to be retrieved.

    Returns
    -------
    QuerySet
        A queryset containing tasks due today for the user.

    """
    # Query tasks due today to be completed
    now = timezone.now()
    twenty_four_hours = now + timedelta(hours=25, minutes=2)
    due_today = TaskTracker.objects.filter(
        habit__user_id=user_id,
        due_date__range=(now, twenty_four_hours),
        task_status='In progress'
    )
    return due_today


def active_tasks(user_id):
    """
    Retrieve available tasks for a given user.

    Parameters
    ----------
    user_id : int
        The ID of the user for whom tasks are to be retrieved.

    Returns
    -------
    QuerySet
        A queryset containing available tasks for the user.

    """
    now = timezone.now()+timedelta(hours=1)
    # Query tasks that are available to be completed
    tasks = TaskTracker.objects.filter(
        habit__user_id=user_id,
        task_status='In progress',
        start_date__lte=now,
        due_date__gt=now
    )
    return tasks

def upcoming_tasks(user_id):
    """
    Retrieve upcoming tasks for a given user.

    Parameters
    ----------
    user_id : int
        The ID of the user for whom upcoming tasks are to be retrieved.

    Returns
    -------
    queryset
        A queryset containing upcoming tasks for the specified user, 
        starting at least one hour from the current time.
    """
    tasks = TaskTracker.objects.filter(habit__user_id=user_id,
                                       start_date__gte=timezone.now()+timedelta(hours=1),
                                       task_number=1)
    return tasks



def calculate_progress(habits):
    """
    Calculate progress percentage for each active habit.

    Parameters
    ----------
    habits : QuerySet
        A queryset containing active habits.

    """
    # Calculate progress percentage for each active habit
    for habit in habits:
        if habit.num_of_tasks > 0:
            streak = habit.streak.first()
            habit.progress_percentage = round(
                (streak.num_of_completed_tasks / habit.num_of_tasks) * 100, 2)
        else:
            habit.progress_percentage = 0.0

def num_inprogress_tasks(habit):
    """
    Update the number of tasks in progress for a habit.

    Parameters
    ----------
    habit : Habit
        The habit for which the number of in-progress tasks is to be updated.

    Returns
    -------
    None

    Notes
    -----
    This function counts the number of tasks in progress for the specified 
    habit in the TaskTracker table and updates the in_progress attribute of 
    the habit object accordingly.
    """
    in_progress_num = TaskTracker.objects.filter(habit=habit, task_status='In progress').count()
    habit.in_progress = in_progress_num


def calculate_score(completed_tasks, failed_tasks, longest_streak, current_streak,
                    num_of_tasks, duration, weights):
    """
    Calculate the score for a habit based on various factors and weights.

    Parameters
    ----------
    completed_tasks : int
        The number of completed tasks for the habit.
    failed_tasks : int
        The number of failed tasks for the habit.
    longest_streak : int
        The longest streak for the habit.
    num_of_tasks : int
        The total number of tasks for the habit.
    duration : int
        The duration of the habit in days.
    weights : dict
        A dictionary containing weights for different factors.

    Returns
    -------
    float
        The calculated score for the habit.

    """
    score = (weights['completed_tasks'] * completed_tasks +
             weights['failed_tasks'] * failed_tasks +
             weights['longest_streak'] * longest_streak +
             weights['current_streak'] *current_streak
             ) / (num_of_tasks * duration)
    return score


def normalize_scores(scores):
    """
    Normalize the scores to ensure they are on the same scale.

    Parameters
    ----------
    scores : list
        A list of scores to be normalized.

    Returns
    -------
    list
        A list of normalized scores.

    """
    mu = np.mean(scores)
    sigma = np.std(scores)
    z_scores = []
    for x in scores:
        if sigma != 0:
            z_scores.append((x - mu) / sigma)
        else:
            z_scores.append(np.nan)  # or handle the case where sigma is zero appropriately

    return z_scores


def rank_habits(weights, period):
    """
    Rank habits based on their scores.

    Parameters
    ----------
    weights : dict
        A dictionary containing weights for different factors.
    period : str
        The period for which habits should be ranked.

    Returns
    -------
    list
       A list of tuples containing habit objects and their corresponding normalized scores, 
       ranked in descending order.

    """
    scores = []
    now = timezone.now()
    last_month = now - timedelta(days=30)

    prefetch_streaks = Prefetch('streak', queryset=Streak.objects.all())
    # Fetch habits with prefetching of related streaks
    habits = Habit.objects.prefetch_related(prefetch_streaks).filter(period=period,
                                                creation_time__range=(last_month, now))

    for habit in habits:
        streak = habit.streak.latest('id')
        if streak is not None:
            num_of_tasks = habit.num_of_tasks
            completed_tasks = streak.num_of_completed_tasks
            failed_tasks = streak.num_of_failed_tasks
            longest_streak = streak.longest_streak
            current_streak = streak.current_streak
            # subtract one day from creation time to avoid ZeroDivisionError
            duration = (now - (habit.creation_time - timedelta(days=1))).days

            score = calculate_score(completed_tasks, failed_tasks, longest_streak,
                                    current_streak, num_of_tasks, duration, weights)

            scores.append(score)
        else:
            pass


    normalized_scores = normalize_scores(scores)
    ranked_habits = sorted(zip(habits, normalized_scores), key=lambda x: x[1], reverse=True)

    return ranked_habits

def all_completed_habits(user_id):
    """
    Retrieve all completed habits for a given user.

    Parameters
    ----------
    user_id : int
        The ID of the user for whom completed habits are to be retrieved.

    Returns
    -------
    queryset
        A queryset containing all completed habits for the specified user.
        
    Notes
    -----
    This function prefetches streak information for each habit and filters the habits
    based on the user ID and completion date.
    It returns a queryset containing all completed habits for the specified user, where the 
    habit completion date is earlier than the current time.
    """
    prefetch_streaks = Prefetch('streak', queryset=Streak.objects.all())
    # num_of_tasks = F'streak.num_of_completed_tasks' + F'streak.num_of_failed_tasks',
    return Habit.objects.prefetch_related(prefetch_streaks).filter(user_id=user_id, completion_date__lt=timezone.now())


def extract_first_failed_task(updated_task_ids):
    """
    Extract the first failed task for each habit based on updated task IDs.

    Parameters
    ----------
    updated_task_ids : list
        List of updated task IDs.

    Returns
    -------
    list
        List of first failed tasks for each habit.

    """
    # Annotate the minimum task number for each habit
    min_task_numbers = TaskTracker.objects.filter(
        id__in=updated_task_ids
        ).values('habit_id').annotate(min_task_number=Min('task_number'))

    # Fetch the first failed task for each habit using the annotated minimum task number
    first_failed_tasks = TaskTracker.objects.filter(
        id__in=updated_task_ids,
        task_number__in=min_task_numbers.values('min_task_number')
        ).order_by('habit_id')

    return first_failed_tasks


def update_user_activity(user_id):
    """
    Update user activity including tasks, achievements, and streaks.

    Parameters
    ----------
    user_id : int
        The ID of the user whose activity is to be updated.

    Returns
    -------
    None

    Notes
    -----
    This function updates the user's activity by first updating task statuses from 
    'in progress' to 'failed' and retrieving their IDs. It then extracts the first 
    failed task for each habit to identify when the user breaks a habit streak. 
    Achievements are updated based on failed tasks, and streaks are updated for 
    relevant habits.
    """

    # Update tasks statuses from in progress to failed and get their ids
    updated_habit_tasks_ids = TaskTracker.update_failed_tasks(user_id=user_id)
    updated_habit_ids, updated_task_ids = updated_habit_tasks_ids

    # The first failed task for each habit is used later to correctly identify
    # when the user breaks a Habit streak.
    first_failed_tasks = extract_first_failed_task(updated_task_ids)

    # Update achievements if failed task
    Achievement.update_achievements(first_failed_tasks)
    Streak.update_streak(updated_habit_ids)
