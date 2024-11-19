import os
import re
import yaml

class Instrument:
    def __init__(self, name, tuning, is_lefty=False):
        self.name = name
        self.tuning = tuning
        self.is_lefty = is_lefty
        self.chords = []

    def add_chord(self, chord):
        self.chords.append(chord)

    def get_chord(self, chord_name):
        for chord in self.chords:
            if chord.name == chord_name:
                return chord
        return None

    def __repr__(self):
        return f"Instrument(name={self.name}, tuning={self.tuning.strings}, is_lefty={self.is_lefty})"

class Chord:
    def __init__(self, name, frets, fingers=None):
        self.name = name
        self.frets = frets
        self.fingers = fingers if fingers else []

    def get_chord_info(self):
        return {
            "name": self.name,
            "frets": self.frets,
            "fingers": self.fingers
        }

class Tuning:
    def __init__(self, strings):
        self.strings = strings

def parse_chord_definitions(file_path, instrument):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return
    
    with open(file_path, 'r') as file:
        content = file.read()
        pattern = re.compile(r'{define: (\w+) frets ([\d\s]+)( fingers [\d\s]+)?}')
        matches = pattern.findall(content)
        for match in matches:
            chord_name = match[0]
            frets = match[1].strip().split()
            #fingers = match[2].strip().split() if match[2] else []
            fingers = [int(f) for f in match[2].strip().split() if f.isdigit()] if match[2] else []
            chord = Chord(name=chord_name, frets=frets, fingers=fingers)
            instrument.add_chord(chord)

def load_instruments_from_yaml(file_path):
    if not os.path.exists(file_path):
        print(f"YAML file {file_path} does not exist.")
        return []
    
    with open(file_path, 'r') as file:
        instruments_data = yaml.safe_load(file)
    
    instruments = []
    base_dir = os.path.dirname(file_path)  # Get the directory of the YAML file
    for data in instruments_data:
        tuning = Tuning(strings=list(data['tuning']))
        instrument = Instrument(name=data['name'], tuning=tuning)
        chord_definitions_path = os.path.join(base_dir, data['chord_definitions'])  # Construct the absolute path
        parse_chord_definitions(chord_definitions_path, instrument)
        instruments.append(instrument)
    
    return instruments
