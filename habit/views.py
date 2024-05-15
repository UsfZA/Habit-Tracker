import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import HabitForm
from .models import TaskTracker, Habit, Streak, Achievement
from .analytics import (
    due_today_tasks, active_tasks, upcoming_tasks,
    calculate_progress, longest_current_streak_over_all_habits,
    all_tracked_habits, habits_by_period,
    longest_streak_over_all_habits, num_inprogress_tasks,
    update_user_activity, rank_habits, all_completed_habits
)

class HabitView(View):
    """
    View class for handling habit-related operations.

    Methods
    -------
    get(request, *args, **kwargs)
        Handles GET requests for displaying the home page.
    post(request, *args, **kwargs)
        Handles POST requests for completing tasks.
    about(request)
        Displays the About page.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for displaying the home page.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """
        user_id = request.user.id
        update_user_activity(user_id)
        today_tasks = due_today_tasks(user_id=user_id)
        active_task = active_tasks(user_id=user_id)
        upcoming_task = upcoming_tasks(user_id=user_id)
        user_full_name = User.objects.get(id=user_id).get_full_name().split()[0].capitalize()

        context = {
            'upcoming_tasks': upcoming_task,
            'due_today_tasks': today_tasks,
            'available_tasks': active_task,
            'user_full_name': user_full_name
        }

        return render(request, 'home.html', context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for completing tasks.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """

        task_id = request.POST.get('task_id')
        habit_id = request.POST.get('habit_id')

        task = get_object_or_404(TaskTracker, id=task_id)
        habit = get_object_or_404(Habit, id=habit_id)
        streak = get_object_or_404(Streak, habit_id=habit_id)

        try:
            # Update Task table
            task.task_status = 'Completed'
            task.task_completion_date = timezone.now()
            task.save()

            # Update streak and number of completed tasks in Streak and Habit tables
            if task.task_status == 'Completed':
                streak.current_streak += 1
                streak.num_of_completed_tasks += 1
                Achievement.rewards_streaks(habit_id, streak)

                habit.save()
                streak.save()

                # messages.success(request, f' {habit.name} Task marked as done')

                return redirect('habit-home')

        except TaskTracker.DoesNotExist:
            pass

        # If an error occurs or the task is not found, redirect to habit home page
        return redirect('habit-home')



class HabitManagerView(View):
    """
    View class for managing habits.

    Methods
    -------
    active_habits(request)
        Displays active habits for the logged-in user.
    habit_detail(request, habit_id)
        Displays detailed information about a habit.
    add_habit(request)
        Handles adding a new habit.
    delete_habit(request, habit_id)
        Handles deleting a habit.
    """
    
    @staticmethod
    def add_habit(request):
        """
        Handles adding a new habit.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """
        if not request.user.is_authenticated:
            return redirect('login')
        pre_defined_habits = {
                            'Exercise': {
                                'frequency': '2',
                                'period': 'weekly',
                                'goal': '1 month',
                                'notes': 'Exercising regularly to maintain physical fitness.'
                            },
                            'Reading': {
                                'frequency': '1',
                                'period': 'daily',
                                'goal': '1 month',
                                'notes': 'Reading habit for personal growth and learning.'
                            },
                            'Brush your Teeth': {
                                'frequency': '2',
                                'period': 'daily',
                                'goal': '1 month',
                                'notes': 'Reminder to maintain oral hygiene by brushing teeth twice daily.'
                            },
                            'Budgeting': {
                                'frequency': '1',
                                'period': 'weekly',
                                'goal': '1 month',
                                'notes': 'Budget finances regularly for financial stability and planning'
                            },
                            'Meditation': {
                                'frequency': '1',
                                'period': 'daily',
                                'goal': '1 month',
                                'notes': 'Daily meditation practice for mental well-being and stress relief.'
                            },
                             'Monthly Review': {
                                'frequency': '1',
                                'period': 'monthly',
                                'goal': '1 year',
                                'notes': 'Reflect on achievements and set goals for the upcoming month.'
                            }
                        }
        if request.method == 'POST':
            form = HabitForm(request.POST)
            if form.is_valid():
                # Validate if the goal is smaller than the period
                if not form.is_goal_achievable():
                    messages.error(request, '''The frequency results in a goal that is not
                                achievable. Choose a longer goal.''')
                    return render(request, 'add_habit.html', {'form': form})

                # Validate if the habit name is not already used or existed
                if not form.is_valid_habit_name(request.user):
                    messages.error(request, "You already used that name for another habit")
                    return render(request, 'add_habit.html', {'form': form})

                start_date = form.cleaned_data['start_date']
                # Save the form with the provided start_date
                habit = form.save(commit=False)
                habit.user = request.user
                habit.start_date = start_date
                habit.save()

                # Create tasks with their due and start dates for the habit
                # to populate the Task table
                TaskTracker.create_tasks(habit)

                habit_name = form.cleaned_data.get('name')
                messages.success(request, f'{habit_name} Habit created')
                return redirect('habit-home')
        else:
            form = HabitForm()
        context = {
            'form': form, 
            'pre_defined_habits': pre_defined_habits
        }

        return render(request, 'add_habit.html', context)

    @staticmethod
    def delete_habit(request, habit_id):
        """
        Handles deleting a habit.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.
        habit_id : int
            The ID of the habit to delete.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """
        if not request.user.is_authenticated:
            return redirect('login')
        
        habit = get_object_or_404(Habit, pk=habit_id)

        
        if request.method == 'POST':
            try:
                habit.delete()
                # messages.success(request, f"{habit.name} Habit deleted successfully")
                return redirect('active_habits')
            except Habit.DoesNotExist:
                pass            
        return render(request, 'habit_confirm_delete.html', {'habit': habit})
        
    @staticmethod
    def active_habits(request):
        """
        Displays active habits for the logged-in user.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_id = request.user.id

        # Query all tracked habits with their longest streak and current streak
        all_active_habits = all_tracked_habits(user_id=user_id)

        # Filter tracked habits with the same periodicity
        daily_habits = habits_by_period('daily')(all_active_habits)
        weekly_habits = habits_by_period('weekly')(all_active_habits)
        monthly_habits = habits_by_period('monthly')(all_active_habits)



        # Calculate progress percentage for each active habit
        # based on (num_complted + num_failed)/num_of_tasks
        calculate_progress(all_active_habits)
        calculate_progress(daily_habits)
        calculate_progress(weekly_habits)
        calculate_progress(monthly_habits)

        context = {
            'active_habits': all_active_habits,
            'daily_habits': daily_habits,
            'weekly_habits': weekly_habits,
            'monthly_habits': monthly_habits,
        }
        return render(request, 'habit_manager.html', context)

    @staticmethod
    def habit_detail(request, habit_id):
        """
        View function to display all habit information (streaks, tasks, achievments) 
        for a given habit_id. including tables for Tasks jornal and Streak log

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.
        habit_id : int
            The ID of the habit to display information for.

        Returns
        -------
        HttpResponse
            The HTTP response.
        """
        if not request.user.is_authenticated:
            return redirect('login')

        habit = get_object_or_404(Habit, pk=habit_id)
        tasks = TaskTracker.objects.filter(habit_id=habit_id)
        streak = Streak.objects.get(habit_id=habit_id)
        achievement = Achievement.objects.filter(habit_id=habit_id)
        num_inprogress_tasks(habit)

        context = {
            'habit': habit,
            'tasks': tasks,
            'streak': streak,
            'achievement' : achievement
        }

        return render(request, 'habit_details.html', context)



class HabitAnalysis(View):
    """
    View class for managing habits.

    This class provides methods for handling habit analysis.

    Methods
    -------
    get(request, *args, **kwargs)
        Handles GET requests for habit analysis.
    post(request, *args, **kwargs)
        Handles POST requests for habit analysis.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for habit analysis.

        Retrieves habit data for the user and renders the analysis template.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        HttpResponse
            Rendered analysis template with habit data.
        """

        user_id = request.user.id

        # Retrieve all tracked habits and filter them by period
        all_habits = all_tracked_habits(user_id=user_id)
        daily_habits = habits_by_period('daily')(all_habits)
        weekly_habits = habits_by_period('weekly')(all_habits)
        monthly_habits = habits_by_period('monthly')(all_habits)

        #retrieve completed habits
        completed_habits = all_completed_habits(user_id)

        # Retrieve the habit with the current longest streak
        longest_current_all_streak = longest_current_streak_over_all_habits()
        # Retrieve the habit with longest streak
        longest_all_streak = longest_streak_over_all_habits()

        weights = {
            'completed_tasks': -0.2,
            'failed_tasks': 0.8,
            'longest_streak': -0.2,
            'current_streak': -0.1
        }

        daily_struggled_most = rank_habits(weights, 'daily')
        weekly_struggled_most = rank_habits(weights, 'weekly')

        print(weekly_struggled_most)
        calculate_progress(all_habits)
        calculate_progress(daily_habits)
        calculate_progress(weekly_habits)
        calculate_progress(monthly_habits)
        calculate_progress(longest_all_streak)
        calculate_progress(longest_current_all_streak)

        context = {
            'all_habits': all_habits,
            'daily_habits': daily_habits,
            'weekly_habits': weekly_habits,
            'monthly_habits': monthly_habits,
            'daily_struggled_most' : daily_struggled_most,
            'weekly_struggled_most' : weekly_struggled_most,
            'longest_all_streak': longest_all_streak,
            'longest_current_all_streak': longest_current_all_streak,
            'completed_habits': completed_habits
        }

        return render(request, 'analysis.html', context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for habit analysis.

        Retrieves selected habit data and its related streak information.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        JsonResponse
            JSON response containing habit data with related streak information.

        Notes
        -----
        The ID of the selected habit is obtained from the request payload.
        """
        selected_value = request.POST.get('selectedValue')

        # Retrieve the habit object with related streak using prefetch_related
        habit = Habit.objects.prefetch_related('streak').get(id=selected_value)

        # Serialize the habit object along with related streak data
        habit_data = serializers.serialize('json', [habit])

        # Convert serialized data to Python dictionary
        habit_dict = json.loads(habit_data)[0]['fields']

        # Add streak data to habit dictionary
        habit_dict['streak'] = list(habit.streak.values())

        return JsonResponse(habit_dict, safe=False)
