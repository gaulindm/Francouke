import re

class SongParser:
    def __init__(self, data):
        self.data = data
        self.lines = data.split('\n')
        self.section = None
        self.parsed_data = {
            'Chorus': [],
            'Bridge': [],
            'Verse': [],
            'Other': []
        }

    def parse(self):
        for line in self.lines:
            if '{soc}' in line:
                self.section = 'Chorus'
            elif '{eoc}' in line:
                self.section = None
            elif '{sob}' in line:
                self.section = 'Bridge'
            elif '{eob}' in line:
                self.section = None
            elif '{sov}' in line:
                self.section = 'Verse'
            elif '{eov}' in line:
                self.section = None
            else:
                self.parse_line(line)
        return self.parsed_data

    def parse_line(self, line):
        if self.section:
            chords, lyrics = self.extract_chords_lyrics(line)
            self.parsed_data[self.section].append({'chords': chords, 'lyrics': lyrics})
        else:
            self.parsed_data['Other'].append(line)

    def extract_chords_lyrics(self, line):
        parts = line.split(']')
        chords = []
        lyrics = []
        for part in parts:
            if '[' in part:
                chord, lyric = part.split('[')
                chords.append(chord.strip())
                lyrics.append(lyric.strip())
            else:
                lyrics.append(part.strip())
        return chords, ' '.join(lyrics)