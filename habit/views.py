from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max
from django.http import JsonResponse, HttpResponseNotFound
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Users.utils import update_profile
from .forms import HabitForm
from .models import TaskTracker, Habit, Streak, Achievement
from .utils import extract_first_failed_task, convert_period_to_days
from .analytics import (
    due_today_tasks, available_tasks, 
    calculate_progress, longest_current_streak_over_all_habits,
    all_tracked_habits, habits_by_period,
    longest_streak_over_all_habits,

)



class HabitView():
    @staticmethod
    @login_required
    def habit_home(request):
        """
        View function to display the user's home page with tasks due today and available tasks, 
        and to mark tasks as completed.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: The HTTP response.
        """
        user_id = request.user.id

        # Update task status, and achievements
        updated_habit_tasks_ids = TaskTracker.update_task_statuses(user_id=user_id)
        updated_habit_ids, updated_task_ids = updated_habit_tasks_ids

        # Escape and quote task IDs for safe use
        # Define the SQL query with a placeholder for the parameter.
        # Using a window function to calculate the rank based on the task number.
        # This allows us to rank tasks within each habit, which is necessary to identify
        # The first failed task for each habit is used later to correctly identify
        # when the user breaks a Habit streak.
        first_failed_tasks = extract_first_failed_task(updated_task_ids)

        # Update achievements if failed task
        Achievement.update_achievements(first_failed_tasks)

        # Update Current Streak
        Streak.update_streak(updated_habit_ids)

        # Get the full name of the user to display on the home page
        user_full_name = ""
        try:
            user = User.objects.get(id=user_id)
            user_full_name = user.get_full_name()
        except User.DoesNotExist:
            pass


        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            habit_id = request.POST.get('habit_id')
            task_status = request.POST.get('task_status')

            try:
                # Update Task table
                task = TaskTracker.objects.get(id=task_id)
                task.task_status = 'Completed'
                task.task_completion_date = timezone.now()
                task.save()

                # Update streak and number of completed tasks in Streak and Habit tables
                if task and task_status == 'Completed':
                    habit = Habit.objects.get(id=habit_id)
                    streak = Streak.objects.get(habit_id=habit_id)
                    streak.current_streak += 1
                    streak.num_of_completed_tasks += 1
                    habit.num_of_completed_tasks += 1
                    Achievement.rewards_streaks(habit_id, streak)

                    habit.save()
                    streak.save()

                    messages.success(request, 'Task marked as done')

                    return redirect('habit-home')

            except TaskTracker.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Task not found'})

        context = {
            'due_today_tasks': due_today_tasks(user_id=user_id),
            'available_tasks': available_tasks(user_id=user_id),
            'user_full_name': user_full_name.split()[0].capitalize()
        }

        return render(request, 'home.html', context)

    @staticmethod
    @login_required
    def add_habit(request):
        """
        View function to handle adding a new habit.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: The HTTP response.
        """
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

                habit = form.save(commit=False)
                habit.user = request.user
                habit.save()

                # Create tasks with their due and start dates for the habit
                # to populate the Task table
                TaskTracker.create_tasks(habit)
                # Initiate a streak on Streak table
                Streak.initiate_streak(habit)
                # Update user's profile to increment the number of habits
                update_profile(request.user)

                habit_name = form.cleaned_data.get('name')
                messages.success(request, f'{habit_name} Habit created')
                return redirect('habit-home')
        else:
            form = HabitForm()

        return render(request, 'add_habit.html', {'form': form})

    @staticmethod
    @login_required
    def delete_habit(request, habit_id):
        habit = get_object_or_404(Habit, pk=habit_id)

        
        if request.method == 'POST':
            try:
                habit.delete()
                messages.success(request, f"{habit.name} Habit deleted successfully")
                return redirect('active_habits')
            except Habit.DoesNotExist:
                return HttpResponseNotFound("Habit does not exist")
        
        return render(request, 'habit_confirm_delete.html', {'habit': habit})


    @staticmethod
    @login_required
    def update_habit(request, habit_id):
        habit = get_object_or_404(Habit, pk=habit_id)
        failed_tasks = get_object_or_404(Streak, habit_id=habit_id).num_of_failed_tasks
        num_of_complted_tasks = habit.num_of_completed_tasks
        now = timezone.now()
        if request.method == 'POST':
            form = HabitForm(request.POST, instance=habit)
            if form.is_valid():
                # Validate if the goal is smaller than the period
                if not form.is_goal_achievable():
                    messages.error(request, '''The frequency results in a goal that is not
                                achievable. Choose a longer goal.''')
                    return render(request, 'add_habit.html', {'form': form})

                # Save the form to update the habit
                habit = form.save(commit=False)

                # Retrieve the maximum task number
                max_task_number_query = TaskTracker.objects.filter(habit_id=habit_id, task_status='Completed').aggregate(max_task_number=Max('task_number'))
                max_task_number = max_task_number_query['max_task_number']

                # delete incomplted tasks
                TaskTracker.objects.filter(habit=habit, task_status = 'In progress').delete()

                # Calculate or update num_of_tasks 
                num_of_period = convert_period_to_days(habit.period)
                habit.num_of_tasks = (habit.goal // num_of_period) * habit.frequency

                # Calculate or update completion_date if it's not provided in the form
                habit.completion_date = now + timedelta(hours=habit.goal * 24)

                # create new tasks for the habit
                TaskTracker.create_tasks(habit, max_task_number)

                #  Add progress on goal to the new goal
                habit.goal = habit.goal + (now - habit.creation_time).days

                # add completed task to the new num of tasks
                habit.num_of_tasks = habit.num_of_tasks + num_of_complted_tasks + failed_tasks

                # Save the form to update the habit
                habit = form.save()   

                messages.success(request, f"{habit.name} Habit updated successfully")
                return redirect('active_habits')
        else:
            form = HabitForm(instance=habit)
        return render(request, 'habit_update.html', {'form': form, 'habit': habit})


class AnalyticModel():
    @staticmethod
    def active_habits(request):
        """
        View function to display active habits for the logged-in user.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: The HTTP response.
        """
        user_id = request.user.id

        # Query all tracked habits with their longest streak and current streak
        all_active_habits = Habit.objects.filter(
                                    user_id=user_id,
                                    completion_date__gte=timezone.now()
                                    ).prefetch_related('streak')

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

        # Construct the context dictionary



        context = {
            'active_habits': all_active_habits,
            'daily_habits': daily_habits,
            'weekly_habits': weekly_habits,
            'monthly_habits': monthly_habits,
        }
        return render(request, 'active_habits.html', context)

    @staticmethod
    @login_required
    def habit_detail(request, habit_id):
        """
        View function to display all habit information (streaks, tasks, achievments) 
        for a given habit_id. including tables for Tasks jornal and Streak log

        Args:
            request (HttpRequest): The HTTP request.
            habit_id (int): The ID of the habit to display information for.

        Returns:
            HttpResponse: The HTTP response.
        """
        habit = Habit.objects.get(pk=habit_id)
        tasks = TaskTracker.objects.filter(habit_id=habit_id)
        streak = Streak.objects.get(habit_id=habit_id)
        achievement = Achievement.objects.filter(habit_id=habit_id)

        context = {
            'habit': habit,
            'tasks': tasks,
            'streak': streak,
            'achievement' : achievement
        }

        return render(request, 'habit_details.html', context)

from django.shortcuts import render

@login_required
def habit_analysis_view(request):
    user_id = request.user.id

    # Retrieve all tracked habits and filter them by period
    all_habits = all_tracked_habits(user_id=user_id)
    daily_habits = habits_by_period('daily')(all_habits)
    weekly_habits = habits_by_period('weekly')(all_habits)
    monthly_habits = habits_by_period('monthly')(all_habits)

    # Retrieve the habit with the longest streak
    longest_current_all_streak = longest_current_streak_over_all_habits()

    longest_all_streak = longest_streak_over_all_habits()

    calculate_progress(all_habits)
    calculate_progress(daily_habits)
    calculate_progress(weekly_habits)
    calculate_progress(monthly_habits)
    calculate_progress(longest_all_streak)
    calculate_progress(longest_current_all_streak)

    

    # Construct the context dictionary
    context = {
        'all_habits': all_habits,
        'daily_habits': daily_habits,
        'weekly_habits': weekly_habits,
        'monthly_habits': monthly_habits,
        'longest_all_streak': longest_all_streak,
        'longest_current_all_streak': longest_current_all_streak
    }

    # Render the template with the context data
    return render(request, 'analysis.html', context)
    
    
def about(request):
    """
    View function to display the About page.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The HTTP response.
    """
    return render(request, 'about.html', {'title': 'About'})
