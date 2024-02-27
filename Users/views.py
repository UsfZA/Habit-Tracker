from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import UserRegisterForm



def start_view(request):
    pass

def register(request):
    if request.method == 'POST':   
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            #user = 
            form.save()
            #user = authenticate(request, username=user.username, password=request.POST['password1'])
            #login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'Users/register.html', {'form': form})

