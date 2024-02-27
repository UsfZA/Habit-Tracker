from .models import Profile
from habit.models import Task


def update_profile(user):
    profile_instance, created = Profile.objects.get_or_create(user=user)

    # Add logic to update the profile fields
    profile_instance.active_habit = Task.objects.filter(habit__user_id=user.id).count()

    profile_instance.save()