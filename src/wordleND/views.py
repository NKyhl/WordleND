from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import User, Play, GameState
from .forms import SignUpUserForm
from .api import view_all_coins, view_balance_for_user, user_pay
from .utils import load_config
import random
import json
from datetime import datetime

# Create your views here.
def home(request):
    config = load_config('config.json')
    access_token = config['access_token']
    user = request.user
    current_date = timezone.now().date()
   
    if request.user.is_authenticated:
        user_email = request.user.email

    user_balance = view_balance_for_user(access_token, user_email)

    plays_today = Play.objects.filter(
        user=user, 
        in_progress = False,
        game_date__date=current_date
    )
    
    print(plays_today)
    
    return render(request, "index.html", {'balance':user_balance['amount']})

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

    print('language is ' + language)

    # open corresponding language file
    if language in {"en", "de", "es", "fr", "pt"}:
        language_path = f"wordleND/languages/{language}.txt"
    else:
        return redirect('home')
        
    # pick random word from file
    with open(language_path, "r") as file:
        words = file.readlines()

        random_word = random.choice(words).strip()

        print('word is ' + random_word)
    # create Play in database with user, word, language...
    p = Play(user=user, word=random_word, language=language)
    p.save()
    g = GameState(play=p)
    g.save()

    #redirect to /play
    return redirect('/play')

def check_word(request):
    if request.method == "POST":
        # Get current game
        play = Play.objects.filter(
            user=request.user,
            in_progress=True,
        )

        if not play:
            return {
                'error': 'No Game in Progress'
            }
        else:
            play = play[0]

        result = []
        j = json.loads(request.body.decode('utf-8'))
        word = j['word'].upper()
        attempt = j['attempt']

        # Validate word
        language_path = f"wordleND/languages/{play.language}.txt"
        with open(language_path, "r") as file:
            words = map(str.upper, map(str.strip, file.readlines()))
            if word.upper() not in words:
                print(f'{word} not in words')
                result = json.dumps({
                    'valid': False
                })
                return HttpResponse(result, content_type='application/json')

        # Check word
        correct = True
        for i, char in enumerate(word):
            if char == play.word[i]:    # Correct
                result.append('C')
            elif char in play.word:     # Good
                result.append('G')
                correct = False
            else:                       # Bad
                result.append('B')
                correct = False

        # Upload game state - TODO
        g = GameState.objects.filter(play=play)[0]
        if attempt == 1:
            g.attempt1 = word
        elif attempt == 2:
            g.attempt2 = word
        elif attempt == 3:
            g.attempt3 = word
        elif attempt == 4:
            g.attempt4 = word
        elif attempt == 5:
            g.attempt5 = word
        elif attempt == 6:
            g.attempt6 = word   
        g.save() 

        # If the game is correct
        if correct:
            play.in_progress = False
            play.attempts = attempt
            play.outcome = True
            play.save()
        
        # User lost
        elif attempt == 6:
            play.in_progress = False
            play.attempts = attempt
            play.outcome = False
            play.save()
            
        # Return result to frontend
        print(result)
        result = json.dumps({
            'valid': True,
            'result': result,
            'correct': correct
        })
        return HttpResponse(result, content_type='application/json')

    return redirect('home')
