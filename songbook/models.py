from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Song(models.Model):
    songTitle = models.CharField(max_length=100, blank=True, null=True)
    songChordPro = models.TextField()
    date_posted = models.DateField(default=timezone.now)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.songTitle or "Untitled Song"
    
    def get_absolute_url(self):
        return reverse('song-detail', kwargs={'pk': self.pk})

class ParsedSong(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="parsed_data")
    metadata = models.JSONField(blank=True, null=True)  # JSON to store parsed metadata
    chords_and_lyrics = models.JSONField(blank=True, null=True)  # JSON to store structured chords and lyrics
    last_parsed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parsed data for {self.song.songTitle}" if self.song.songTitle else "Parsed data"
