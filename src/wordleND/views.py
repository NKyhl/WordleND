from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User, Play
from .forms import SignUpUserForm
import json

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
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('play')
        else:
            messages.error(request, ("Invalid Credentials, Try Again..."))

    return render(request, "signin.html", {})

def signout(request):
    logout(request)
    messages.success(request, ("You Logged Out!"))
    return redirect('home')

def check_word(request):
    if request.method == "POST":
        # Get current game
        # play = Play.objects.filter(
        #     user=request.user,
        #     in_progress=True,
        # )
        play = {
            'word': 'MILES'
        }

        if not play:
            return {
                'error': 'No Game in Progress'
            }
        # else:
            # play = play[0]

        result = []
        word = json.loads(request.body.decode('utf-8'))['word']
        print(type(word))

        # Check word
        for i, char in enumerate(word):
            if char == play['word'][i]:    # Correct
                result.append('C')
            elif char in play['word']:     # Good
                result.append('G')
            else:                       # Bad
                result.append('B')

        # Upload game state - TODO

        # Return result to frontend
        print(result)
        result = json.dumps({'result': result})
        return HttpResponse(result, content_type='application/json')

    return redirect('home')