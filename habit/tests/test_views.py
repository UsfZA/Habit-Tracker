import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from habit.views import HabitManagerView, HabitView
from habit.models import Habit, TaskTracker, Streak
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase



class ViewTestCase(TestCase): 
    """Test cases for Views."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = User.objects.create_user(username='test_user_1', password='123456')
        cls.factory = RequestFactory()
        cls.habit =  Habit.objects.create(user=cls.user, name='Test Habit', frequency=1, 
                                period='daily', goal=7, notes='', start_date=timezone.now())


    def test_add_habit_authenticated_user(self):
        request = self.factory.post('/add-habit')
        request.user = self.user
        response = HabitManagerView.add_habit(request)
        assert response.status_code == 200


    def test_add_habit_not_authenticated(self):
        request = self.factory.post('/add-habit')
        request.user = AnonymousUser()
        response = HabitManagerView.add_habit(request)
        assert response.status_code == 302 
        assert response.url == '/Login'


    def test_delete_habit_authenticated_user(self):
        request = self.factory.post(reverse('habit_deletion', args=[self.habit.pk]))
        request.user = self.user
        response = HabitManagerView.delete_habit(request, self.habit.pk)
        assert response.status_code == 302 
        assert not Habit.objects.filter(pk=self.habit.pk).exists()
        assert response.url == '/Habit-Manager/'


    def test_delete_habit_not_authenticated(self):
        request = self.factory.post(reverse('habit_deletion', args=[self.habit.pk]))
        request.user = AnonymousUser()
        response = HabitManagerView.delete_habit(request, self.habit.pk)
        assert response.status_code == 302
        assert Habit.objects.filter(pk=self.habit.pk).exists()
        assert response.url == '/Login'


    def test_mark_task_completed(self):
        task = TaskTracker.objects.create(habit=self.habit, task_number=1)
        streak = Streak.objects.filter(habit=self.habit).first()
        request = self.factory.post('/habit-home', {'task_id': task.id, 'habit_id': self.habit.id})
        request.user = self.user
        response = HabitView.as_view()(request)
        assert TaskTracker.objects.get(id=task.id).task_status == 'Completed'
        streak.refresh_from_db()
        assert streak is not None
        assert streak.current_streak == 1
        assert streak.num_of_completed_tasks == 1
        assert streak.longest_streak == 1
        assert response.status_code == 302
        assert response.url == '/'
