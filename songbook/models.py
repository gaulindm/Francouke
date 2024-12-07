# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import re
import json
from .parsers import parse_song_data  # Import the parse_song_data function
from .transposer import detect_key

class Song(models.Model):
    songTitle = models.CharField(max_length=100, blank=True, null=True)
    songChordPro = models.TextField()  # Original
    lyrics_with_chords = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)  # Stores metadata as JSON
    date_posted = models.DateField(default=timezone.now)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        # Only parse title if songTitle is not manually set
        if not self.songTitle:
            self.songTitle, self.metadata = self.parse_metadata_from_chordpro()
        else:
            # Only update metadata
            _, self.metadata = self.parse_metadata_from_chordpro()
        
        # Parse the songChordPro content of the song
        self.lyrics_with_chords = parse_song_data(self.songChordPro)

        # Detect the key if not already specified
        if not self.metadata.get('key'):
            self.metadata['key'] = detect_key(self.lyrics_with_chords)
            
        super().save(*args, **kwargs)

    def parse_metadata_from_chordpro(self):
        # Regular expressions to find all relevant metadata tags
        tags = {
            "title": re.search(r'{(?:title|t):\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "comment": re.search(r'{(?:comment|c):\s*(.+?)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "artist": re.search(r'{artist:\s*([^\}]+)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "album": re.search(r'{album:\s*(.+?)}', self.songChordPro, re.IGNORECASE | re.UNICODE),
            "year": re.search(r'{year:\s*(\d{4})}', self.songChordPro, re.IGNORECASE),
            "key": re.search(r'{key:\s*(.+?)}', self.songChordPro, re.IGNORECASE),
            "youtube": re.search(r'{youtube:\s*(https?://[^\s\}]+)}', self.songChordPro, re.IGNORECASE),  # New tag
        }
        
        # Extract each tag's value, or use None if not found
        metadata = {tag: match.group(1) if match else None for tag, match in tags.items()}
        
        # Set title separately as it is also stored in songTitle
        title = metadata.pop("title", "Untitled Song")

        return title, metadata

    def __str__(self):
        return self.songTitle or "Untitled Song"
    
    def get_absolute_url(self):
        return reverse('score', kwargs={'pk': self.pk})
