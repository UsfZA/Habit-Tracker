"""
Forms for managing habits in the Habit application.

This module defines Django forms used for creating and managing habits in the Habit application.
These forms include the HabitForm, which allows users to input habit details such as name, 
frequency, period, goal, and notes.

Classes:
    HabitForm: A form for creating and managing habits.

"""

from django import forms
from django.core.validators import MinValueValidator
from .models import Habit
from .utils import convert_goal_to_days



class HabitForm(forms.ModelForm):
    """
    Form for creating or updating a Habit.

    Attributes:
    ----------
        PERIOD_CHOICES (list): Choices for the habit period.
        GOAL_CHOICES (list): Choices for the habit goal duration.
    """

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual')
    ]

    GOAL_CHOICES = [
        ('3 days', "3 Day's"),
        ('1 week', '1 Week'),
        ('1 month', '1 Month'),
        ('2 months', "2 Month's"),
        ('3 months', "3 Month's"),
        ('6 months', "6 Month's"),
        ('1 year', '1 Year')
    ]

    period = forms.ChoiceField(choices=PERIOD_CHOICES, widget=forms.Select, required=True)
    frequency = forms.IntegerField(initial=1, required=False, validators=[MinValueValidator(1)])
    notes = forms.CharField(required=False)
    goal = forms.ChoiceField(choices=GOAL_CHOICES, widget=forms.Select, required=True)
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'start-date-field'}),
        required=True
    )

    def clean_goal(self):
        """
        Clean and validate the 'goal' field.

        Returns:
        -------
            int: The number of days corresponding to the selected goal.
        """
        selected_goal = self.cleaned_data.get('goal')
        return convert_goal_to_days(selected_goal)

    def is_valid_habit_name(self, user):
        """
        Check if the habit name is unique for the given user.

        Parameters:
        ----------
            user (User): The user for whom the habit name uniqueness is checked.

        Returns:
        -------
            bool: True if the habit name is unique; False otherwise.
        """
        habit_name = self.cleaned_data['name']

        # Check if a habit with the same name and user already exists
        if Habit.objects.filter(user=user, name__iexact=habit_name).exists():
            return False
        return True

    def is_goal_achievable(self):
        """
        Check if the specified goal for the habit is achievable based on frequency and period.

        Returns:
        -------
            bool: True if the goal is achievable; False otherwise.
        """
        goal = self.cleaned_data.get('goal')
        period = self.cleaned_data.get('period')

        num = 1  # Initialize 'num' with a default value
        if period == 'daily':
            num = 1
        elif period == 'weekly':
            num = 7
        elif period == 'monthly':
            num = 30
        elif period == 'annual':
            num = 365

        return num < goal

    class Meta:
        """
        Meta class for defining the model and fields for the HabitForm.
        """
        model = Habit
        fields = ['name', 'frequency', 'period', 'goal', 'notes', 'start_date']