from django.apps import AppConfig


class HabitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'habit'

    def ready(self) -> None:
        import habit.signals
