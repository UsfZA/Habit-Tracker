from datetime import datetime
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from habit.models import Habit
from habit.forms import HabitForm


class ViewTestCase(TestCase):
    """Test cases for Views."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(username='test_user_1', password='123456')
    # def user():
    #     return User.objects.create_user(username='test_user', password='12345')


    @pytest.mark.django_db
    def test_valid_habit_name(cls):
        start_date = timezone.make_aware(datetime(2024, 4, 19, 12, 0))
        data = {'name': 'New Habit', 'frequency': -1, 'period': 'daily', 
                'goal': -7, 'notes': '', 'start_date': start_date}
        form = HabitForm(data=data)
        form.is_valid()
        assert form.is_valid_habit_name(cls.user) == True


    @pytest.mark.django_db
    def test_invalid_habit_name(cls):
        start_date = timezone.make_aware(datetime(2024, 4, 19, 12, 0))
        existing_habit = Habit.objects.create(user=cls.user, name='Existing Habit', frequency=1,
                                              period='daily', goal=7, notes='', start_date=start_date)
        data = {'name': 'Existing Habit', 'frequency': 1, 'period': 'daily',
                'goal': 7, 'notes': '', 'start_date': start_date}
        form = HabitForm(data=data)
        form.is_valid()
        assert form.is_valid_habit_name(cls.user) == False

    @pytest.mark.django_db
    def test_in(cls):
        start_date = timezone.make_aware(datetime(2024, 4, 19, 12, 0))
        data = {'name': 'New Habit', 'frequency': -1, 'period': 'daily', 'goal': -7, 'notes': '', 'start_date': start_date}
        form = HabitForm(data=data)

        # Check if form is invalid
        assert form.is_valid() == False

        # Check if the form errors contain the expected error messages for negative frequency and goal
        assert 'frequency' in form.errors
        assert 'goal' in form.errors
        assert "Ensure this value is greater than or equal to 1." in form.errors['frequency']
        assert "Select a valid choice. -7 is not one of the available choices." in form.errors['goal']
