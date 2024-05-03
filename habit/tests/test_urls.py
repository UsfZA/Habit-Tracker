from django.urls import resolve, reverse
from habit import views as habit_views



class TestUrls:
    
    def test_home_url(self):
        path = reverse('habit-home')
        assert resolve(path).func.view_class == habit_views.HabitView

    def test_habit_analysis(self):
        path = reverse('HabitsAnalysis')
        assert resolve(path).func.view_class == habit_views.HabitAnalysis

    def test_add_habit_url(slef):
        path = reverse('habit_creation')
        assert resolve(path).func.__name__ == 'add_habit'

    def test_delete_habit_url(self):
        path = reverse('habit_deletion', kwargs={'habit_id': 55})
        assert resolve(path).func.__name__ == 'delete_habit'

    def test_habit_detail_url(self):
        path = reverse('habit_detail', kwargs={'habit_id': 58})
        assert resolve(path).func.__name__ == 'habit_detail'

    def test_habit_manager_url(self):
        path = reverse('active_habits')
        assert resolve(path).func.__name__ == 'active_habits'
