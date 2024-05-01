from django.contrib import admin
from .models import Play, GameState, Profile

# Register your models here.
admin.site.register(Play)
admin.site.register(GameState)
admin.site.register(Profile)