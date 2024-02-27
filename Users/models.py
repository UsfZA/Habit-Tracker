from django.db import models
from django.contrib.auth.models import User
from habit.models import Habit #, Task
from django.utils import timezone



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    full_name = models.CharField(max_length=255)
    active_habit = models.IntegerField(default=0)
    email = models.EmailField(default="unknown@example.com")
    date_joined = models.DateTimeField(null=True, blank=True)
    #completed_habit = models.IntegerField(default=0)
    #achievements = models.ImageField()
    def save(self, *args, **kwargs):
        self.full_name = f"{self.user.first_name} {self.user.last_name}"
        self.active_habit = Habit.objects.filter(user=self.user).count()
        self.email = self.user.email
        self.date_joined = self.user.date_joined

        #self.completed_habit = 
        
        super().save(*args, **kwargs)

