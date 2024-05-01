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
        if not user_balance:
            user_balance = {'amount': 0}

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
                messages.success(request, ("You have used all of your available games today. Come back tomorrow for three more!"))
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
            name = form.cleaned_data['name']
            user = authenticate(username=username, password=password)
            profile = Profile(user=user)
            if name:
                profile.name = name
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
    if not request.user.is_authenticated:
        messages.warning(request, ('Sign in to start a new game'))
        return redirect('home')

    user = request.user
    language = request.POST.get('language')

    # Don't create a new game if they are in the middle of one
    active_plays_today = Play.objects.filter(
        user=user, 
        in_progress = True,
        game_date__date=datetime.now().today()
    ).count()

    if active_plays_today:
        messages.success(request, ('Resuming game in progress...'))
        return redirect('play')

    # Check if an extra_game should be used or if they need to use coins
    completed_plays_today = Play.objects.filter(
        user=user, 
        in_progress = False,
        game_date__date=datetime.now().today()
    ).count()

    profile = Profile.objects.get(user=user)
    extra_plays = profile.extra_plays

    if completed_plays_today >= 3:
        if not extra_plays:
            return redirect('home')
        else:
            profile.extra_plays -= 1
            profile.save()
            messages.success(request, (f'You have used an extra play! You have {profile.extra_plays} remaining'))

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
        result = ['B'] * 5
        unflagged_guess = []
        unflagged_word = []
        # Greens
        for i, char in enumerate(guess):
            if char == play.word[i].upper():    # Correct
                result[i] = 'C'
            else:
                unflagged_word.append(i)
                unflagged_guess.append(i)
        
        correct = True if not unflagged_word else False
        
        # Yellow
        skip_guess = []
        skip_word = []
        for i in unflagged_guess:            # Go through remaining
            if i in skip_guess:
                continue
            for j in unflagged_word:
                if j in skip_word:
                    continue
                if guess[i] == play.word[j]:
                    result[i] = 'G'
                    skip_guess.append(i)
                    skip_word.append(j)

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

    profile = Profile.objects.get(user=request.user)
    extra_plays = profile.extra_plays

    if request.method == 'POST':
        
        amount = request.POST.get('amount')
        email = request.user.email 
        balance = view_balance_for_user(access_token, email)
        if not balance:
            balance = {'amount': 0}
        
        
        transaction_result = user_pay(access_token, request.user, amount)
        print(transaction_result)
        balance = view_balance_for_user(access_token, email)
        if not balance:
            balance = {'amount': 0}

        profile = Profile.objects.get(user=request.user)
        extra_plays = profile.extra_plays
        
        return render(request, 'purchase.html', {
            'transaction_result': transaction_result, 
            'balance': balance['amount'],
            'extra_plays': extra_plays
        })
    else:
        config = load_config('config.json')
        access_token = config['access_token']
        email = request.user.email 
        balance = view_balance_for_user(access_token, email)
        if not balance:
            balance = {'amount': 0}
        return render(request, 'purchase.html', {
            'balance':balance['amount'],
            'extra_plays': extra_plays
        })

def player_dashboard(request):
    if not request.user.is_authenticated:
        messages.warning(request, ('Sign in to view stats'))
        return redirect('home')

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

    config = load_config('config.json')
    access_token = config['access_token']

    balance = view_balance_for_user(access_token, request.user.email)
    if not balance:
        balance = {'amount': 0}

    context = {
        'all_plays': all_plays,
        'time_period':time_period,
        'total_plays': total_plays,
        'total_wins': total_wins,
        'win_percentage': win_percentage,
        'attempts_distribution': attempts_distribution,
        'balance': balance['amount']
    }
    return render(request, "stats.html", context)