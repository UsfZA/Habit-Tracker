from django import forms
from django.core.validators import MinValueValidator
from .models import Habit
from .models import Habit
from .utils import convert_goal_to_days

class HabitForm(forms.ModelForm):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual')
    ]

    GOAL_CHOICES = [
        ('1w', '1 Week'),
        ('1m', '1 Month'),
        ('2m', '2 Months'),
        ('3m', '3 months'),
        ('6m', '6 months'),
        ('1y', '1 year')
    ]   

    period    = forms.ChoiceField(choices=PERIOD_CHOICES, widget=forms.Select, required=True)
    frequency = forms.IntegerField(initial=1, required=False, validators=[MinValueValidator(1)])
    notes     = forms.CharField(required=False)
    goal      = forms.ChoiceField(choices=GOAL_CHOICES, widget=forms.Select, required=True)


    def clean_goal(self):
        selected_goal = self.cleaned_data.get('goal')
        habit = Habit()
        return convert_goal_to_days(selected_goal)
    

    def is_valid_habit_name(self, user):
        """
        Check if the habit name is unique for the given user.

        Args:
            user (User): The user for whom the habit name uniqueness is checked.

        Returns:
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
        model = Habit
        fields = ['name', 'frequency', 'period', 'goal', 'notes']