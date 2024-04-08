from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Habit, Streak

@receiver(post_save, sender=Habit)
def create_streak(sender, instance, created, **kwargs):
    """
    Signal handler for creating a Streak instance when a Habit instance is created.

    This signal handler creates a new Streak instance associated with the Habit instance
    when the Habit instance is created.

    Parameters
    ----------
    sender : class
        The class sending the signal (Habit).
    instance : Habit
        The Habit instance that was created.
    created : bool
        A boolean indicating whether the instance was created or updated.
    **kwargs : dict
        Additional keyword arguments.

    Returns
    -------
    None

    """
    if created:
        Streak.objects.create(habit=instance)


@receiver(post_save, sender=Habit)
def save_streak(sender, instance, **kwargs):
    """
    Signal handler for updating a Streak instance when a Habit instance is saved.

    This signal handler updates the associated Streak instance when the Habit instance
    is saved.

    Parameters
    ----------
    sender : class
        The class sending the signal (Habit).
    instance : Habit
        The Habit instance that was saved.
    **kwargs : dict
        Additional keyword arguments.

    Returns
    -------
    None

    """
    # Check if the related Streak instance exists
    if hasattr(instance, 'streak'):
        # Get the Streak instance associated with the Habit
        streak_instance = instance.streak.first()
        if streak_instance:
            streak_instance.save()
