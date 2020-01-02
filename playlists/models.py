from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Playlist(models.Model):
    # stores songs as a string of song id's separated by commas
    songs = models.TextField(default = '')
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    playlist_name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    time_created_at = models.DateTimeField(default=now)
    genre = models.CharField(max_length=100)
    tempo = models.IntegerField(default = 0)
    duration = models.TextField(default = '0')
    title = models.TextField(default = 'Default Title')