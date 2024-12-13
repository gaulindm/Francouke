import re
import os

def convert_chord_pro_format(file_path):
    """
    Converts chord pro format from `{{C}}` to `[C]` in a given file,
    adds metadata tags at the beginning, and saves the output to 'Song.songchordpro'.

    Args:
        file_path (str): Path to the input file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read the content of the file
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Use regular expression to find and replace patterns
        converted_content = re.sub(r"\{\{(.*?)\}\}", r"[\1]", content)
        
        # Define the metadata tags
        metadata = """
{title: }
{artist: }
{album: }
{capo: }
{composer: }
{lyricist: }
{key: }
{recording: }
{year: }
{1stnote: }
{tempo: }
{timeSignature: }

"""

        # Combine metadata and converted content
        final_content = metadata.strip() + "\n\n" + converted_content
        
        # Save the final content to 'Song.songchordpro'
        output_path = "Song.songchordpro"
        with open(output_path, 'w') as file:
            file.write(final_content)
        
        print(f"File successfully converted and saved to {output_path}.")
    
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    input_file = "example.txt"  # Replace with the full path if necessary
    convert_chord_pro_format(input_file)
