from django.db import models

# Create your models here.
class User(models.Model):
    '''Represents a player profile'''
    username = models.CharField(max_length=50, primary_key=True)
    email = models.CharField(max_length=260, unique=True)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=100, blank=True, null=True, default=None) # Optional

class Play(models.Model):
    '''Represents one play of the game and its stats'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_date = models.DateTimeField('date played')
    outcome = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)