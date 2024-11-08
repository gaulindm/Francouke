# songbook/management/commands/populate_parsed_songs.py

from django.core.management.base import BaseCommand
from songbook.models import Song
from songbook.parsers import parse_song_data # Import the parse function

class Command(BaseCommand):
    help = "Populate metadata and lyrics_with_chords fields from songChordPro data"

    def handle(self, *args, **kwargs):
        # Retrieve all Song records
        songs = Song.objects.all()
        for song in songs:
            # Parse the ChordPro content of the song
            lyrics_with_chords = parse_song_data(song.songChordPro)
            
             #Update the song record with parsed data
            #song.metadata = metadata
    
            song.lyrics_with_chords = lyrics_with_chords
            song.save()  # Save changes to the database

    #    self.stdout.write(self.style.SUCCESS("Successfully populated Song records"))
      #  song = Song.objects.first()
      #  metadata, lyrics_with_chords = parse_chordpro(song.songChordPro)

        # Ensure lyrics_with_chords is a list of dictionaries, not a JSON string
      #  if isinstance(lyrics_with_chords, str):
      #      import json
      #      lyrics_with_chords = json.loads(lyrics_with_chords)

      #  song.metadata = metadata
      #  song.lyrics_with_chords = lyrics_with_chords
      #  song.save()