from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile for the user when a new user is created.

    Parameters:
    ----------
        sender: The sender of the signal.
        instance (User): The instance of the User model being saved.
        created (bool): Indicates if the User instance was newly created.
        **kwargs: Additional keyword arguments.

    Returns:
    -------
        None
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the profile associated with the user.

    Parameters:
    ----------
        sender: The sender of the signal.
        instance (User): The instance of the User model being saved.
        **kwargs: Additional keyword arguments.

    Returns:
    -------
        None
    """
    instance.profile.save()
