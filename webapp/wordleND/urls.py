from django.urls import path
from . import views

urlpatterns = [
	path("", views.home, name="home"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("play", views.play, name="play")
from .views import home, signup, signin

urlpatterns = [
	path("", home, name="home"),
    path("signup", signup, name="signup"),
    path("signin", signin, name="signin")
]
