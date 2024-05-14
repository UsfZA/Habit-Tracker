from django.db import models
from django.contrib.auth.models import User
from habit.models import Habit



class Profile(models.Model):
    """
    Model representing a user profile.

    Attributes:
    ----------
        user (User): The associated user for the profile.
        image (ImageField): The profile picture of the user.
        full_name (CharField): The full name of the user.
        active_habit (IntegerField): The number of active habits for the user.
        email (EmailField): The email address of the user.
        date_joined (DateTimeField): The date and time when the user joined.

    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    active_habit = models.IntegerField(default=0)
    email = models.EmailField(default="unknown@example.com")
    date_joined = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to update profile fields based on the associated user and habits.

        Parameters:
        ----------
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.full_name = f"{self.user.first_name} {self.user.last_name}"
        self.active_habit = Habit.objects.filter(user=self.user).count()
        self.email = self.user.email
        self.date_joined = self.user.date_joined
        super().save(*args, **kwargs)
