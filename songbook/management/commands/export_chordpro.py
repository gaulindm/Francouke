import os
from django.core.management.base import BaseCommand
from songbook.models import Song  # Update with the correct app name
from pathlib import Path

class Command(BaseCommand):
    help = "Export songs in ChordPro format"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Directory to save the ChordPro files',
            default=str(Path.home() / "Downloads")  # Default to Downloads folder
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)

        songs = Song.objects.all()
        for song in songs:
            chordpro_content = self.convert_to_chordpro(song)
            # Use songTitle or a fallback for the filename
            filename = f"{song.songTitle or 'Untitled'}.chordpro"
            safe_filename = "".join(c for c in filename if c.isalnum() or c in " ._-").strip()
            file_path = os.path.join(output_dir, safe_filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(chordpro_content)

            self.stdout.write(f"Exported: {file_path}")

    def convert_to_chordpro(self, song):
        """
        Convert a Song instance to ChordPro format.
        """
        # Use songTitle for the title
        title = song.songTitle if song.songTitle else "Untitled"
        header = f"{{title: {title}}}\n"

        # Optional metadata like artist or contributor
        contributor = song.contributor.username if song.contributor else "Unknown"
        header += f"{{artist: {contributor}}}\n\n"

        # Use songChordPro field for the ChordPro content
        return header + song.songChordPro

