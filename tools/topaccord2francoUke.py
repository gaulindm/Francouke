import re
import os
import django
from django.utils.timezone import now
from django.contrib.auth.models import User
from songbook.models import Song  # Update with your app name

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FrancoUke.settings")
django.setup()

def convert_and_add_song_to_django(file_path, contributor_id):
    """
    Converts ChordPro format and adds the song to the Django database.

    Args:
        file_path (str): Path to the input file.
        contributor_id (int): ID of the user contributing the song.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        if len(lines) < 2:
            raise ValueError("Input file must have at least two lines for artist and title.")
        
        # Extract artist and title from the first two lines
        artist = lines[0].strip()
        title = lines[1].strip()
        
        # Remaining content after artist and title
        content = "".join(lines[2:])
        
        # Use regular expression to find and replace patterns
        converted_content = re.sub(r"\{\{(.*?)\}\}", r"[\1]", content)
        
        # Prepare metadata
        metadata = {
            "artist": artist,
            "title": title,
        }
        
        # Get contributor (user)
        contributor = User.objects.get(pk=contributor_id)
        
        # Add the song to the Django database
        song = Song.objects.create(
            songTitle=title,
            songChordPro=content,
            metadata=metadata,
            date_posted=now(),
            contributor=contributor
        )
        print(f"Song '{title}' by {artist} added to the database.")
    
    except User.DoesNotExist:
        print(f"Contributor with ID {contributor_id} does not exist.")
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    input_file = "example.txt"  # Replace with the full path if necessary
    contributor_id = 1  # Replace with the actual ID of the user contributing the song
    convert_and_add_song_to_django(input_file, contributor_id)
