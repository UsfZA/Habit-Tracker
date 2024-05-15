from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from habit.models import Habit, Streak
from habit.analytics import rank_habits


class AnalyticTestCase(TestCase):
    """Test cases for the Habit model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user_1 = User.objects.create_user(username='test_user_1', password='123456')
        cls.user_2 = User.objects.create_user(username='test_user', password='12345')

        # Create Habit objects one by one
        cls.habit_1 = Habit.objects.create(
            id=55, name='brush your teeth', frequency=1, period='daily',goal=30,
            num_of_tasks=30, notes='', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 3, 28, 1, 38, 47, 450258)), 
            completion_date=timezone.make_aware(datetime(2024, 4, 27, 1, 38, 47, 450258)),
            start_date=timezone.make_aware(datetime(2024, 4, 7, 15, 0, 37, 712030))
        )

        cls.habit_2 = Habit.objects.create(
            id=56, name='read books', frequency=2, period='weekly', goal=30,
            num_of_tasks=8, notes='', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 3, 28, 1, 39, 4, 545451)), 
            completion_date=timezone.make_aware(datetime(2024, 4, 27, 1, 39, 4, 545451)),
            start_date=timezone.make_aware(datetime(2024, 3, 28, 1, 39, 4, 545451))
        )

        cls.habit_3 = Habit.objects.create(
            id=57, name='exercise', frequency=2, period='weekly', goal=30,
            num_of_tasks=8, notes='', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 3, 28, 1, 41, 55, 500895)), 
            completion_date=timezone.make_aware(datetime(2024, 4, 27, 1, 41, 55, 500895)),
            start_date=timezone.make_aware(datetime(2024, 3, 28, 1, 41, 55, 500895))
        )

        cls.habit_4 = Habit.objects.create(
            id=58, name='healthy eating', frequency=1, period='daily', goal=30,
            num_of_tasks=30, notes='', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 3, 28, 1, 42, 56, 350832)),
            completion_date=timezone.make_aware(datetime(2024, 4, 27, 1, 42, 56, 350832)),
            start_date=timezone.make_aware(datetime(2024, 4, 7, 15, 0, 50, 209682))   
        )

        cls.habit_5 = Habit.objects.create(
            id=59, name='budgeting', frequency=2, period='weekly', goal=30,
            num_of_tasks=8, notes='', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 3, 28, 1, 43, 40, 63651)),
            completion_date=timezone.make_aware(datetime(2024, 4, 27, 1, 43, 40, 62617)),
            start_date=timezone.make_aware(datetime(2024, 4, 7, 15, 3, 32, 628966))
        )

        cls.habit_6 = Habit.objects.create(
            id=76, name='meditation', frequency=1, period='daily', goal=30, num_of_tasks=30,
            notes='Daily meditation practice for mental well-being and stress relief.', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 4, 2, 20, 49, 49, 987603)),
            completion_date=timezone.make_aware(datetime(2024, 5, 2, 20, 49, 49, 987603)),
            start_date=timezone.make_aware(datetime(2024, 4, 7, 21, 13, 3, 316327)),
        )

        cls.habit_7 = Habit.objects.create(
            id=143, name='monthly review', frequency=1, period='monthly', goal=180, num_of_tasks=6,
            notes='Reflect on achievements and set goals for the upcoming month.', user=cls.user_1,
            creation_time=timezone.make_aware(datetime(2024, 4, 8, 2, 30, 14, 774289)),
            completion_date=timezone.make_aware(datetime(2024, 10, 28, 22, 0)),
            start_date=timezone.make_aware(datetime(2024, 5, 1, 22, 0)),
        )

        #Daily Habits
        cls.streak_1 = Streak.objects.create(habit_id=55, num_of_completed_tasks=16, num_of_failed_tasks=14,
                                             longest_streak=9, current_streak=0)
        
        cls.streak_6 = Streak.objects.create(habit_id=76, num_of_completed_tasks=18, num_of_failed_tasks=12,
                                             longest_streak=6, current_streak=6)
        
        cls.streak_4 = Streak.objects.create(habit_id=58, num_of_completed_tasks=18, num_of_failed_tasks=12,
                                             longest_streak=7, current_streak=0)
        
        # Weekly Habits
        cls.streak_2 = Streak.objects.create(habit_id=56, num_of_completed_tasks=6, num_of_failed_tasks=2,
                                             longest_streak=3, current_streak=3)
        
        cls.streak_3 = Streak.objects.create(habit_id=57, num_of_completed_tasks=5, num_of_failed_tasks=3,
                                             longest_streak=3, current_streak=2)
        
        cls.streak_5 = Streak.objects.create(habit_id=59, num_of_completed_tasks=7, num_of_failed_tasks=1,
                                             longest_streak=4, current_streak=0)


    def test_rank_daily_habits_scores(self):
        # Define weights and period
        period = 'daily'
        weights = {'completed_tasks': -0.2, 'failed_tasks': 0.8, 'longest_streak': -0.2, 'current_streak': -0.1}            
        ranked_habits = rank_habits(weights=weights, period=period)

        assert ranked_habits[0][0] == Habit.objects.get(pk=55)
        assert ranked_habits[1][0] == Habit.objects.get(pk=58)
        assert ranked_habits[2][0] == Habit.objects.get(pk=76)

        assert ranked_habits[0][1] == 1.3887301496588267
        assert ranked_habits[1][1] == -0.4629100498862762
        assert ranked_habits[2][1] == -0.9258200997725524

    def test_rank_weekly_habits_scores(self):
        # Define weights and period
        period = 'weekly'
        weights = {'completed_tasks': -0.2, 'failed_tasks': 0.8, 'longest_streak': -0.2, 'current_streak': -0.1}            
        ranked_habits = rank_habits(weights=weights, period=period)

        assert ranked_habits[0][0] == Habit.objects.get(pk=57)
        assert ranked_habits[1][0] == Habit.objects.get(pk=56)
        assert ranked_habits[2][0] == Habit.objects.get(pk=59)

        assert ranked_habits[0][1] == 1.2634656762057948
        assert ranked_habits[1][1] == -0.08151391459392247
        assert ranked_habits[2][1] == -1.1819517616118722