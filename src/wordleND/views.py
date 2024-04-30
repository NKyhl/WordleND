from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import SignUpUserForm
import random

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
            return redirect('home')
    else:
        form = SignUpUserForm()

    return render(request, "signup.html", {'form': form})

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, ("Invalid Credentials, Try Again..."))

    return render(request, "signin.html", {})

def signout(request):
    logout(request)
    messages.success(request, ("You Logged Out!"))
    return redirect('home')

def create_game(request):
    # get user and preferred language from request
    user = request.user
    language = request.POST.get('language')
    # open corresponding language file
    if language == "en.txt":
        language_path = f"../languages/{language}.txt"
    elif language == "de.txt":
        language_path = f"../languages/{language}.txt"
    elif language == "es.txt":
        language_path = f"../languages/{language}.txt"
    elif language == "fr.txt":
        language_path = f"../languages/{language}.txt"
    elif lanugage == "pt.txt":
        language_path = f"../languages/{language}.txt"
    else:
        return redirect('home')
        
    # pick random word from file
    with open(language_path, "r") as file:
        words = file.readlines()

        random_word = random.choice(words).strip()
    # create Play in database with user, word, language...
    p = Play(user=user, word=random_word, language=language)
    p.save()

    #redirect to /play
    return redirect('/play')