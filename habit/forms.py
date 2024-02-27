from django import forms
from django.core.validators import MinValueValidator
from habit.models import Habit


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


    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'number_of_times', 'period', 'goal', 'notes']