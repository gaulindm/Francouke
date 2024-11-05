import re

def parse_chordpro(content):
    metadata = {}
    lyrics_with_chords = []

    # Split content by line
    lines = content.splitlines()
    for line in lines:
        # Extract metadata (e.g., title, artist)
        if line.startswith("{"):
            if "title:" in line.lower():
                metadata["title"] = line.split(":")[1].strip("} ")
            elif "artist:" in line.lower():
                metadata["artist"] = line.split(":")[1].strip("} ")
            # Add more metadata parsing here if needed
            continue
        
        # Parse lyrics with chords
        parsed_line = []
        parts = re.split(r'(\[.*?\])', line)  # Split by chords in brackets
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                chord = part.strip("[]")
                parsed_line.append({"chord": chord, "lyric": ""})  # Add empty lyric if chord-only
            else:
                if parsed_line and "lyric" in parsed_line[-1] and parsed_line[-1]["lyric"] == "":
                    # Attach lyrics to the previous chord dictionary if it exists
                    parsed_line[-1]["lyric"] = part
                else:
                    # Add lyrics without chord if no chord was found before
                    parsed_line.append({"chord": "", "lyric": part})
        
        # Only add non-empty parsed lines to lyrics_with_chords
        if parsed_line:
            lyrics_with_chords.append(parsed_line)

    return metadata, lyrics_with_chords
