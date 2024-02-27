from django import forms
from django.core.validators import MinValueValidator
from habit.models import Habit
from .models import Task

class HabitForm(forms.ModelForm):
    PERIOD_CHOICES = [
        ('daily', 'Day'),
        ('weekly', 'Week'),
        ('monthly', 'Month'),
        ('annual', 'Year')
    ]

            
    period = forms.ChoiceField(choices=PERIOD_CHOICES, widget=forms.Select, required=True)
    number_of_times = forms.IntegerField(initial=1, label='Number of Times', required=False, validators=[MinValueValidator(1)])
    frequency = forms.IntegerField(initial=1, required=False, validators=[MinValueValidator(1)])
    notes = forms.CharField(required=False)
    goal = forms.IntegerField(initial=1, required=True, validators=[MinValueValidator(1)])


    def is_valid_habit_name(self, user):
        self.cleaned_data['name'] = self.cleaned_data['name'].lower()
        # Check if a habit with the same name and user already exists
        if Habit.objects.filter(user=user, name=self.cleaned_data['name'].lower()).exists():
            return False
        return True
    
    num = 1  # Initialize 'num' with a default value
    # Rest of your save method code...


    def is_goal_achievable(self):
        num_times = self.cleaned_data.get('number_of_times')
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

        return num * num_times < goal

    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'number_of_times', 'period', 'goal', 'notes']