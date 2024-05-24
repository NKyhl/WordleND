from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    '''Represents a user's non-auth-related data'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True, default=None) # Optional
    extra_plays = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}'


class Play(models.Model):
    '''Represents one play of the game and its stats'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_date = models.DateTimeField('date played', auto_now_add=True, blank=True)
    outcome = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    in_progress = models.BooleanField(default=True)
    language = models.CharField(max_length=2, default='en') # de, es, fr, pt, en
    word = models.CharField(max_length=5, default='MILES')
    attempt1 = models.CharField(max_length=5, blank=True, null=True, default='')
    attempt2 = models.CharField(max_length=5, blank=True, null=True, default='')
    attempt3 = models.CharField(max_length=5, blank=True, null=True, default='')
    attempt4 = models.CharField(max_length=5, blank=True, null=True, default='')
    attempt5 = models.CharField(max_length=5, blank=True, null=True, default='')
    attempt6 = models.CharField(max_length=5, blank=True, null=True, default='')

    def __str__(self):
        return f'{self.game_date.date()} - {self.user} - {self.language} -  {self.word}' + (' - In Progress' if self.in_progress else (' - Won' if self.outcome else ' - Lost'))
