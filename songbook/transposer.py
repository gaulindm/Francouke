# transposer.py
from collections import Counter

def detect_key(parsed_data):
    key_chords = {
        'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am'],
        'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em'],
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
