from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User

# Create your views here.
def home(request):
    return render(request, "index.html")

def signup(request):
    return render(request, "signup.html")

def signin(request):
    return render(request, "signin.html")

def create_user(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']

    # Validate input
    if not username:
        return render(request, 'wordleND/signup.html', {
            'error_message': "You didn't enter a username",
        })
    if not email or '@' not in email:
        return render(request, 'wordleND/signup.html', {
            'error_message': "You didn't enter a valid email",
        })
    if not password:
        return render(request, 'wordleND/signup.html', {
            'error_message': "You didn't enter a password",
        })
    
    # Check to see if a user already exists with this username
    username_taken = False # TODO

    if username_taken:
        return render(request, 'wordleND/signup.html', {
            'error_message': "Sorry, this username is taken",
        })
    
    # Check to see if a user already exists with this email
    email_taken = False # TODO

    if email_taken:
        return render(request, 'wordleND/signup.html', {
            'error_message': "An account already exists with this email",
        })

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return HttpResponseRedirect(reverse('wordleND:play.html'))