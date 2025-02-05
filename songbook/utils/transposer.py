# transposer.py
from collections import Counter

def detect_key(parsed_data):
    key_chords = {
        'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am'],
        'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em'],
        'Gm': ['Gm', 'Adim', 'Bb', 'Cm', 'Dm', 'Eb','F'],
        'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm'],
        'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m'],
        'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m'],
        'B': ['B', 'C#m', 'D#m', 'E', 'F#', 'G#m'],
        'F#': ['F#', 'G#m', 'A#m', 'B', 'C#', 'D#m'],
        'C#': ['C#', 'D#m', 'E#m', 'F#', 'G#', 'A#m'],
        'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm'],
        'Bb': ['Bb', 'Cm', 'Dm', 'Eb', 'F', 'Gm'],
        'Eb': ['Eb', 'Fm', 'Gm', 'Ab', 'Bb', 'Cm'],
        'Ab': ['Ab', 'Bbm', 'Cm', 'Db', 'Eb', 'Fm'],
        'Db': ['Db', 'Ebm', 'Fm', 'Gb', 'Ab', 'Bbm'],
        'Gb': ['Gb', 'Abm', 'Bbm', 'Cb', 'Db', 'Ebm'],
        'Cb': ['Cb', 'Dbm', 'Ebm', 'Fb', 'Gb', 'Abm']
    }

    chords = extract_chords(parsed_data, unique=False)
    chord_counts = Counter(chords)
    key_scores = {key: sum(chord_counts[chord] for chord in chords) for key, chords in key_chords.items()}
    detected_key = max(key_scores, key=key_scores.get)

    return detected_key

# transposer.py
def extract_chords(parsed_data, unique=False):
    chords = []
    for section in parsed_data:
        for item in section:
            if isinstance(item, dict) and 'chord' in item and item['chord']:
                chords.append(item['chord'])
    
    if unique:
        return list(set(chords))  # Return unique chords
    return chords  # Return all chords

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chord(chord, semitones):
    """Transpose a chord up/down by a given number of semitones."""
    if not chord:
        return chord  # If no chord, return as-is

    base_chord = ""  # Extract root note (C, D#, etc.)
    suffix = ""  # Store additional chord info (m, 7, maj7, etc.)

    # Split the chord into its base note and suffix
    for i, char in enumerate(chord):
        if char.isdigit() or char in ["m", "M", "b", "#"]:
            suffix = chord[i:]  # The rest is the suffix
            break
        base_chord += char  # The beginning is the root note

    if base_chord not in CHORDS:
        return chord  # If not a valid root chord, return unchanged

    # Find the new chord position
    index = CHORDS.index(base_chord)
    new_index = (index + semitones) % len(CHORDS)

    return CHORDS[new_index] + suffix  # Reattach the suffix


def calculate_steps(original_key, new_key):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    original_index = notes.index(original_key)
    new_index = notes.index(new_key)
    return new_index - original_index

def transpose_lyrics(parsed_data, steps):
    transposed_data = []
    for section in parsed_data:
        transposed_section = []
        for item in section:
            if 'chord' in item and item['chord']:
                transposed_chord = transpose_chord(item['chord'], steps)
                transposed_section.append({'chord': transposed_chord, 'lyric': item['lyric']})
            else:
                transposed_section.append(item)
        transposed_data.append(transposed_section)
    return transposed_data

