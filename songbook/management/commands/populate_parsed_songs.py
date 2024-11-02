from django.core.management.base import BaseCommand
from songbook.models import Song, ParsedSong
from songbook.parsers import parse_chordpro  # Ensure this path is correct
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = "Populate ParsedSong records based on Song ChordPro data"

    def handle(self, *args, **kwargs):
        songs = Song.objects.all()
        success_count = 0
        failure_count = 0

        for song in songs:
            if not song.songChordPro:
                self.stdout.write(self.style.WARNING(f"Song '{song.title}' has no ChordPro data. Skipping."))
                failure_count += 1
                continue

            try:
                metadata, chords_and_lyrics = parse_chordpro(song.songChordPro)
                ParsedSong.objects.update_or_create(
                    song=song,
                    defaults={
                        "metadata": metadata,
                        "chords_and_lyrics": chords_and_lyrics,
                    },
                )
                success_count += 1
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Error updating ParsedSong for '{song.title}': {e}"))
                failure_count += 1

        self.stdout.write(self.style.SUCCESS(f"ParsedSong records populated: {success_count} succeeded, {failure_count} failed."))
