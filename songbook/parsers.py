import re

def parse_song_data(data):
    song_parts = []
    current_part = []

    for line in data.split('\n'):
        line = line.strip()

        if line.startswith('{'):  # Directive line
            if current_part:
                song_parts.append(current_part)
            current_part = [{"directive": line}]
        elif line:  # Chord/lyric line or lyric-only line
            # Split the line into parts based on chords 
            parts = re.split(r"(\[[^\]]+\])", line)
            parts = [part for part in parts if part]  # Remove empty parts

            for i, part in enumerate(parts):
                if part.startswith("["):  # Chord
                    # Get the corresponding lyric
                    lyric = parts[i + 1].strip() if i + 1 < len(parts) else ""
                    current_part.append({"chord": part[1:-1], "lyric": lyric}) 
                elif i == 0 or not parts[i - 1].startswith("["):  # Intro text or lyric without preceding chord
                    current_part.append({"chord": "", "lyric": part.strip()})

            current_part.append({"format": "LINEBREAK"})  # Add LINEBREAK at the end

    if current_part:
        song_parts.append(current_part)

    return song_parts
# Parse the data
#parsed_data = parse_song_data(data)

# To see the output, run the code.

#print(parsed_data)