# songbook/management/commands/populate_parsed_songs.py

from django.core.management.base import BaseCommand
from songbook.models import Song
from songbook.parsers import parse_chordpro  # Import the parse function

class Command(BaseCommand):
    help = "Populate metadata and lyrics_with_chords fields from songChordPro data"

    def handle(self, *args, **kwargs):
        # Retrieve all Song records
        songs = Song.objects.all()
        for song in songs:
            # Parse the ChordPro content of the song
            metadata, lyrics_with_chords = parse_chordpro(song.songChordPro)
            
             #Update the song record with parsed data
            song.metadata = metadata
    
            song.lyrics_with_chords = lyrics_with_chords
            song.save()  # Save changes to the database

