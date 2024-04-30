from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("play", views.play, name="play"),
    path("signout", views.signout, name="signout"),
    path("check-word", views.check_word, name="check-word")
]