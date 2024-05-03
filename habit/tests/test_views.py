from habit.models import Habit
import pytest
from django.contrib.auth.models import User
from habit.forms import HabitForm
from datetime import datetime
from django.utils import timezone
from django.test import TestCase



class ViewTestCase(TestCase): 
    """Test cases for Views."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(username='test_user', password='12345')


    def test_valid_habit_name(self):
        data = {'name': 'New Habit', 'frequency': -1, 'period': 'daily', 'goal': 7, 'notes': '', 'start_date': timezone.now()}
        form = HabitForm(data=data)
        form.is_valid()
        assert form.is_valid_habit_name(self.user) == True


    def test_invalid_habit_name(self):
        
        Habit.objects.create(user=self.user, name='Existing Habit', frequency=1, period='daily', goal=7, notes='', start_date=timezone.now())
        data = {'name': 'Existing Habit', 'frequency': 1, 'period': 'daily', 'goal': 7, 'notes': '', 'start_date': timezone.now()}
        form = HabitForm(data=data)
        form.is_valid()
        assert form.is_valid_habit_name(self.user) == False

    def test_invalid_value_goal_frequency(user):
        data = {'name': 'New Habit', 'frequency': -1, 'period': 'daily', 'goal': -7, 'notes': '', 'start_date': timezone.now()}
        form = HabitForm(data=data)

        # Check if form is invalid
        assert form.is_valid() == False
        
        # Check if the form errors contain the expected error messages for negative frequency and goal
        assert 'frequency' in form.errors
        assert 'goal' in form.errors
        assert "Ensure this value is greater than or equal to 1." in form.errors['frequency']
        assert "Select a valid choice. -7 is not one of the available choices." in form.errors['goal']