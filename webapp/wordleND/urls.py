from django.urls import path
from .views import signup

app_name = 'wordleND'

urlpatterns = [
	path("", signup, name="sign_up")
]
