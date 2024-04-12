from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    '''Represents a user's non-auth-related data'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True, default=None) # Optional


class Play(models.Model):
    '''Represents one play of the game and its stats'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_date = models.DateTimeField('date played')
    outcome = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)