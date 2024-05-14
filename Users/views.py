from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Profile

def register(request):
    """
    View function for user registration.

    This view handles the registration of new users. If the request method is POST,
    it validates the user registration form, saves the user if the form is valid,
    and redirects to the login page. If the request method is GET, it renders the
    user registration form.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The HTTP response object.

    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'Users/register.html', {'form': form})


@login_required
def profile(request):
    """
    View function to display user profile and handle profile picture upload.

    If the request method is POST, it validates the profile update form, saves the
    profile if the form is valid, and redirects to the profile page with a success message.
    If the request method is GET, it renders the profile update form with the current
    user profile instance.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The HTTP response object.

    """
    if request.method == 'GET':
        profile_instance, create = Profile.objects.get_or_create(user=request.user)

    return render(request, 'Users/profile.html', {'profile': profile_instance})
