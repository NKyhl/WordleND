from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("play", views.play, name="play"),
    path("signout", views.signout, name="signout"),
    path("check-word", views.check_word, name="check-word"),
    path("create-game", views.create_game, name="create-game"),
    path("purchase", views.purchase, name="purchase"),
    path("stats", views.player_dashboard, name="stats")
]