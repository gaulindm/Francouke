import re
from typing import Tuple, Dict, List

def parse_chordpro(content: str) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """
    Parses ChordPro format content and returns metadata and structured chords and lyrics.
    """
    metadata = {}
    chords_and_lyrics = []

    lines = content.splitlines()
    for line in lines:
        if line.startswith("{"):
            directive = line.strip("{}").split(":")
            if len(directive) >= 2:
                key = directive[0].strip().lower()
                value = ":".join(directive[1:]).strip()

                if key in ["title", "artist", "album", "key", "capo"]:
                    metadata[key] = value
                elif key == "c":  # Comment directive
                    chords_and_lyrics.append({"comment": value})
        else:
            line_content = []
            parts = re.split(r"(\[.*?\])", line)
            for part in parts:
                if part.startswith("[") and part.endswith("]"):
                    chord = part.strip("[]")
                    line_content.append({"chord": chord})
                else:
                    line_content.append({"lyric": part})
            chords_and_lyrics.append(line_content)

    return metadata, chords_and_lyrics
