from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time
from habit.models import Habit, TaskTracker, Streak, Achievement
from habit.analytics import extract_first_failed_task


class HabitTestCase(TestCase):
    """Test cases for the Habit model."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user_1 = User.objects.create_user(username='test_user_1', password='123456')
        cls.user_2 = User.objects.create_user(username='test_user', password='12345')

        cls.habit_1 = Habit.objects.create(
            name='Exercise',
            frequency=2,
            period='weekly',
            goal=35,
            num_of_tasks=0,
            notes='Regular exercise for fitness',
            start_date=timezone.now(),
            user=cls.user_1
        )

        cls.habit_2 = Habit.objects.create(
            name='brush your teeth',
            frequency=2,
            period='weekly',
            goal=30,
            num_of_tasks=0,
            notes='Reminder to maintain oral hygiene by brushing teeth twice daily.',
            start_date=timezone.now(),
            user=cls.user_2
        )


    def setUp(self):
        """Set up each test."""
        self.start_date = timezone.now()

    def test_habit_creation(self):
        """Test creation of Habit objects."""

        # Assertions for habit_1
        assert self.habit_1.name.capitalize() == 'Exercise'
        assert self.habit_1.frequency == 2
        assert self.habit_1.period == 'weekly'
        assert self.habit_1.goal == 35
        assert self.habit_1.notes == 'Regular exercise for fitness'
        assert self.habit_1.user == self.user_1
        assert self.habit_1.num_of_tasks == 10


        # Assertions for habit_2
        assert self.habit_2.name == 'brush your teeth'
        assert self.habit_2.frequency == 2
        assert self.habit_2.period == 'weekly'
        assert self.habit_2.goal == 30
        assert self.habit_2.notes == 'Reminder to maintain oral hygiene by brushing teeth twice daily.'
        assert self.habit_2.user == self.user_2
        assert self.habit_2.num_of_tasks == 8

        # Check if num_of_tasks was calculated correctly
        expected_num_of_tasks_1 = (self.habit_1.goal // 7) * self.habit_1.frequency
        expected_num_of_tasks_2 = (self.habit_2.goal // 7) * self.habit_2.frequency
        assert self.habit_1.num_of_tasks == expected_num_of_tasks_1
        assert self.habit_2.num_of_tasks == expected_num_of_tasks_2

        # Check if start_date and completion_date were set correctly
        assert self.habit_1.start_date is not None
        assert self.habit_1.completion_date is not None
        assert self.habit_1.completion_date == self.habit_1.start_date + timedelta(days=self.habit_1.goal)

        assert self.habit_2.start_date is not None
        assert self.habit_2.completion_date is not None
        assert self.habit_2.completion_date == self.habit_2.start_date + timedelta(days=self.habit_2.goal)

class TaskTrackerTestCase(TestCase):
    """Test cases for the TaskTracker model."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user_1 = User.objects.create_user(username='test_user_1', password='123456')
        cls.habit = Habit.objects.create(name='Exercise', frequency=1, period='daily', goal=3,
                                         num_of_tasks=0, notes='Regular exercise for fitness',
                                         start_date=timezone.now(), user=cls.user_1)

    def test_task_creation(self):
        """Test creation of TaskTracker objects."""
        TaskTracker.create_tasks(self.habit)
        tasks = TaskTracker.objects.filter(habit=self.habit)

        # Check if tasks were created for the habit
        assert tasks.exists()

        # Check if the number of tasks created matches the habit's num_of_tasks
        assert tasks.count() == self.habit.num_of_tasks

        # Check if the task numbers are assigned correctly
        for index, task in enumerate(tasks, start=1):
            assert task.task_number == index

    def test_task_due_dates(self):
        """Test due dates calculation for TaskTracker objects."""
        TaskTracker.create_tasks(self.habit)

        # Calculate the time between tasks
        time_jump = self.habit.goal / self.habit.num_of_tasks
        time_skip = timedelta(hours=time_jump * 24)

        # Check if the due dates are calculated correctly
        tasks = TaskTracker.objects.filter(habit=self.habit)
        current_due_date = self.habit.start_date
        for task in tasks:
            assert task.due_date == (current_due_date + time_skip)
            current_due_date += time_skip

    def test_default_task_status(self):
        """Test default status for TaskTracker objects."""
        TaskTracker.create_tasks(self.habit)

        # Check if the default task status is set correctly
        tasks = TaskTracker.objects.filter(habit=self.habit)
        for task in tasks:
            assert task.task_status == 'In progress'

    def test_update_failed_tasks(self):
        """Test updating failed tasks for TaskTracker objects."""
        TaskTracker.create_tasks(self.habit)
        tasks = TaskTracker.objects.filter(habit=self.habit)

        # Freeze time to time where two first tasks are overdue
        frozen_time = timezone.now() + timedelta(days=2)
        with freeze_time(frozen_time):
            # Call the method to update failed tasks
            updated_habit_ids, updated_task_ids = TaskTracker.update_failed_tasks(self.user_1.id)

            for task in tasks:
                # Refresh the task from the database to get the latest status
                task.refresh_from_db()
                if task.task_number == 3:
                    assert task.task_status == 'In progress'
                else:
                    # Assert that the task status is updated to 'Failed'
                    assert task.task_status == 'Failed'
                    assert task.task_completion_date == task.due_date

                    # Assert that the method returns the correct updated habit and task IDs
                    assert task.habit_id in updated_habit_ids
                    assert task.id in updated_task_ids


class StreakTestCase(TestCase):
    """Test cases for the Streak model."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user_1 = User.objects.create_user(username='test_user_1', password='123456')
        cls.habit = Habit.objects.create(name='Exercise', frequency=1, period='daily',
                                goal=12, num_of_tasks=0, notes='Regular exercise for fitness',
                                start_date=timezone.now(), user=cls.user_1)

    def test_streak_creation_on_habit_creation(self):
        """Test streak creation upon habit creation."""
        streak = Streak.objects.filter(habit=self.habit).first()
        assert streak is not None
        assert streak.current_streak == 0
        assert streak.longest_streak == 0

    def test_longest_streak_update(self):
        """Test updating the longest streak."""
        streak = Streak.objects.create(
            habit=self.habit,
            longest_streak=10,
            current_streak=11,
        )
        streak.save()
        assert streak.longest_streak == 11

    def test_update_streak_information(self):
        """Test updating streak information."""
        TaskTracker.create_tasks(self.habit)
        streak = Streak.objects.get(habit=self.habit)
        tasks = TaskTracker.objects.filter(habit=self.habit)

        # Mark the first 7 tasks and task number 10 as completed
        for task in tasks:
            if task.task_number <= 7:
                task.task_status = 'Completed'
                streak.current_streak += 1
                task.save()
                streak.save()

        # Freeze time to a date where tasks 8 and 9 are considered overdue
        frozen_time = timezone.now() + timedelta(days=9)
        with freeze_time(frozen_time):
            # Call the method to update failed tasks
            updated_habit_ids, updated_task_ids = TaskTracker.update_failed_tasks(self.user_1.id)
        streak.update_streak(updated_habit_ids)
        streak.num_completed_tasks(habit=self.habit)
        streak.refresh_from_db()

        for task in tasks:
            if 10 <= task.task_number <= 12:
                task.task_status = 'Completed'
                streak.current_streak += 1
                task.save()
                streak.save()

        streak.num_completed_tasks(habit=self.habit)
        streak.refresh_from_db()

        # Check if the streak lengths are updated accurately
        assert streak.num_of_completed_tasks == 10
        assert streak.num_of_failed_tasks == 2
        assert streak.longest_streak == 7
        assert streak.current_streak == 3

class AchievementTestCase(TestCase):
    """Test cases for the Achievement model."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user_1 = User.objects.create_user(username='test_user_1', password='123456')
        cls.habit_1 = Habit.objects.create(name='Exercise', frequency=1, period='daily',
                                goal=30, num_of_tasks=0, notes='Regular exercise for fitness',
                                start_date=timezone.now(), user=cls.user_1)
        cls.habit_2 = Habit.objects.create(name='read books', frequency=2, period='weekly',
                                goal=30, num_of_tasks=0, notes='',
                                start_date=timezone.now(), user=cls.user_1)

    def test_update_daily_achievement_information(self):
        """Test updating streak information."""
        TaskTracker.create_tasks(self.habit_1)
        streak = Streak.objects.get(habit=self.habit_1)
        tasks = TaskTracker.objects.filter(habit=self.habit_1)

        # Mark the first 7 tasks and task number 10 as completed
        for task in tasks:
            if task.task_number <= 8:
                task.task_status = 'Completed'
                streak.current_streak += 1
                task.save()
                streak.save()
                Achievement.rewards_streaks(task.habit_id, streak)

        # Freeze time to a date where tasks 9 and 10 are considered overdue
        frozen_time_1 = timezone.now() + timedelta(days=10)
        with freeze_time(frozen_time_1):
            # Call the method to update failed tasks
            updated_habit_ids, updated_task_ids = TaskTracker.update_failed_tasks(self.user_1.id)
            first_failed_tasks = extract_first_failed_task(updated_task_ids)
            Achievement.update_achievements(first_failed_tasks)
            streak.update_streak(updated_habit_ids)
            streak.refresh_from_db()

        # Freeze time to a date where tasks 11 and 12 are considered overdue
        # test for avoiding repeated Break habit title
        frozen_time_2 = timezone.now() + timedelta(days=12)
        with freeze_time(frozen_time_2):
            # Call the method to update failed tasks
            updated_habit_ids, updated_task_ids = TaskTracker.update_failed_tasks(self.user_1.id)
            first_failed_tasks = extract_first_failed_task(updated_task_ids)
            Achievement.update_achievements(first_failed_tasks)
            streak.update_streak(updated_habit_ids)
            streak.refresh_from_db()

        # test for 14 day and 7 day streak titles
        for task in tasks:
            if 12 < task.task_number < 28:
                task.task_status = 'Completed'
                streak.current_streak += 1
                task.save()
                streak.save()
                Achievement.rewards_streaks(task.habit_id, streak)

        achievements = Achievement.objects.filter(habit=self.habit_1)
        streak.refresh_from_db()

        # assert that four achievement objects are created
        assert Achievement.objects.count() == 4
        assert achievements[0].title == '7-Day Streak'
        assert achievements[0].streak_length == 7
        assert achievements[1].title == 'Break The Habit'
        assert achievements[1].streak_length == 8
        assert achievements[2].title == '7-Day Streak'
        assert achievements[2].streak_length == 7
        assert achievements[3].title == '14-Day Streak'
        assert achievements[3].streak_length == 14

    def test_update_weekly_achievement(self):
        """Test updating streak information."""
        TaskTracker.create_tasks(self.habit_2)
        streak = Streak.objects.get(habit=self.habit_2)
        tasks = TaskTracker.objects.filter(habit=self.habit_2)

        # Mark the first 7 tasks and task number 10 as completed
        for task in tasks:
            if task.task_number <= 8:
                task.task_status = 'Completed'
                streak.current_streak += 1
                task.save()
                streak.save()
                Achievement.rewards_streaks(task.habit_id, streak)

        streak.refresh_from_db()
        achievements = Achievement.objects.filter(habit=self.habit_2)

        # assert that four achievement objects are created
        assert Achievement.objects.count() == 3
        assert achievements[0].title == '1-Week Streak'
        assert achievements[0].streak_length == 2
        assert achievements[1].streak_length == 4
        assert achievements[1].title == "2-Week's Streak"
        assert achievements[2].title == "4-Week's Streak"
        assert achievements[2].streak_length == 8
