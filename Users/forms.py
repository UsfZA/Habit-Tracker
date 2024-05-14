from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    """
    Form for registering a new user.

    Attributes:
    ----------
        email (EmailField): The email address of the user.
    """

    email = forms.EmailField()

    class Meta:
        """
        Meta class for defining the model and fields for the UserRegisterForm.
        """
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    
