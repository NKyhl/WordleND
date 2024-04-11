from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import SignUpUserForm

# Create your views here.
def home(request):
    return render(request, "index.html", {})

def play(request):
    return render(request, "play.html", {})

def signup(request):
    if request.method == "POST":
        form = SignUpUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Account Created!"))
            print(f'LOG - user {username} created!')
            return redirect('play')
    else:
        form = SignUpUserForm()

    return render(request, "signup.html", {'form': form})

def signin(request):
    return render(request, "signin.html", {})