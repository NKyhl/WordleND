from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.db.models import Count
from .models import User, Play, GameState, Profile
from .forms import SignUpUserForm
from .api import view_all_coins, view_balance_for_user, user_pay
from .utils import load_config
import random
import json
from datetime import datetime
from operator import countOf

# Create your views here.
def home(request):
    config = load_config('config.json')
    access_token = config['access_token']
    current_date = timezone.now().date()
    user = request.user
   
    if request.user.is_authenticated:
        user_email = request.user.email

        user_balance = view_balance_for_user(access_token, user_email)

        active_plays_today = Play.objects.filter(
            user=user, 
            in_progress = True,
            game_date__date=current_date
        ).count()

        completed_plays_today = Play.objects.filter(
            user=user, 
            in_progress = False,
            game_date__date=current_date
        ).count()
        
        print('In Progress Games Today:', active_plays_today)
        print('Completed Games Today:', completed_plays_today)

        profile = Profile.objects.get(user=user)
        extra_plays = profile.extra_plays

        if completed_plays_today >= 3 and not extra_plays:
            if user_balance['amount'] == 0:
                messages.success(request, ("You have used all of your available games today. Come back tomorrow!"))
            else:
                messages.success(request, ("You have used all of your available games today. Want to use your coins?"))


        return render(request, "index.html", {
            'balance': user_balance['amount'],
            'in_progress': True if active_plays_today else False,
            'limit_reached': True if completed_plays_today >= 3 and not extra_plays else False,
            'plays_today': active_plays_today + completed_plays_today
        })
    
    return render(request, "index.html", {'balance':0})

def play(request):
    if not request.user.is_authenticated:
        return render(request, "play.html")

    # Get current game
    play = Play.objects.filter(
        user=request.user,
        in_progress=True,
        game_date__date=datetime.now().today()
    )

    if not play:
        return redirect('home')
    else:
        play = play[0]

    # Get game state
    print(play)
    g = GameState.objects.filter(
        play=play
    )
    print(g)

    if not g:
        return redirect('home')
    else:
        g = g[0]

    # Get colors too
    attempts = [g.attempt1, g.attempt2, g.attempt3, g.attempt4, g.attempt5, g.attempt6]
    colors = []
    for attempt in attempts:
        result = []
        for i, char in enumerate(attempt):
            if char == play.word[i].upper():    # Correct
                result.append('C')
            elif char in play.word.upper():     # Good
                result.append('G')
            else:                               # Bad
                result.append('B')
        colors.append(result)


    return render(request, "play.html", {
        'attempts': [g.attempt1, g.attempt2, g.attempt3, g.attempt4, g.attempt5, g.attempt6],
        'colors': colors,
        'word': play.word
    })

def signup(request):
    if request.method == "POST":
        form = SignUpUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            profile = Profile(user=user)
            profile.save()
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
            return redirect('/play')
        else:
            play = play[0]

        result = []
        j = json.loads(request.body.decode('utf-8'))
        guess = j['guess']
        attempt = j['attempt']

        # Validate word
        language_path = f"wordleND/languages/{play.language}.txt"
        with open(language_path, "r") as file:
            words = map(str.upper, map(str.strip, file.readlines()))
            if guess not in words:
                print(f'{guess} not in words')
                result = json.dumps({
                    'valid': False
                })
                return HttpResponse(result, content_type='application/json')

        # Check word
        correct = True
        for i, char in enumerate(guess):
            if char == play.word[i].upper():    # Correct
                result.append('C')
            elif char in play.word.upper():     # Good
                result.append('G')
                correct = False
            else:                               # Bad
                result.append('B')
                correct = False

        # Upload game state - TODO
        g = GameState.objects.filter(play=play)[0]
        if attempt == 1:
            g.attempt1 = guess
        elif attempt == 2:
            g.attempt2 = guess
        elif attempt == 3:
            g.attempt3 = guess
        elif attempt == 4:
            g.attempt4 = guess
        elif attempt == 5:
            g.attempt5 = guess
        elif attempt == 6:
            g.attempt6 = guess   
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
            'correct': correct,
            'word': play.word
        })
        return HttpResponse(result, content_type='application/json')

    return redirect('home')

def purchase(request):
    config = load_config('config.json')
    access_token = config['access_token']
    if request.method == 'POST':
        
        amount = request.POST.get('amount')
        email = request.user.email 
        balance = view_balance_for_user(access_token, email)
        
        
        transaction_result = user_pay(access_token, email, amount)
        print(transaction_result)
        balance = view_balance_for_user(access_token, email)
        
        return render(request, 'purchase.html', {'transaction_result': transaction_result, 'balance':balance['amount']})
    else:
        config = load_config('config.json')
        access_token = config['access_token']
        email = request.user.email 
        balance = view_balance_for_user(access_token, email)
        return render(request, 'purchase.html', {'balance':balance['amount']})

def player_dashboard(request):
    all_plays = Play.objects.filter(user=request.user, in_progress=False)
    
    total_plays = all_plays.count()
    total_wins = all_plays.filter(outcome=True).count()
    win_percentage = (total_wins / total_plays) * 100 if total_plays > 0 else 0
    attempt_history = [p.attempts for p in Play.objects.filter(user=request.user, in_progress=False, outcome=True)]
    print(total_plays)
    attempts_distribution = [
        countOf(attempt_history, 1),
        countOf(attempt_history, 2),
        countOf(attempt_history, 3),
        countOf(attempt_history, 4),
        countOf(attempt_history, 5),
        countOf(attempt_history, 6),
    ]
    print(attempts_distribution)

    time_period = request.GET.get('time_period', 'all')
    if time_period == 'last_week':
        all_plays = Play.objects.filter(user=request.user, game_date__gte=timezone.now() - timezone.timedelta(days=7))
    elif time_period == 'last_month':
        all_plays = Play.objects.filter(user=request.user, game_date__gte=timezone.now() - timezone.timedelta(days=30))
    elif time_period == 'last_year':
        all_plays = Play.objects.filter(user=request.user, game_date__gte=timezone.now() - timezone.timedelta(days=365))

    context = {
        'all_plays': all_plays,
        'time_period':time_period,
        'total_plays': total_plays,
        'total_wins': total_wins,
        'win_percentage': win_percentage,
        'attempts_distribution': attempts_distribution
    }
    return render(request, "stats.html", context)