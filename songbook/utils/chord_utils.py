import os
import json
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Spacer, Flowable
from reportlab.lib import colors

class ChordDiagram(Flowable):
    def __init__(self, chord_name, variation, scale=0.5, is_lefty=False):
        super().__init__()
        self.chord_name = chord_name
        self.variation = variation  # e.g., [0, 0, 0, 3]
        self.scale = scale
        self.is_lefty = is_lefty  # New parameter to handle left-handed diagrams

    def draw(self):
        string_spacing = 15 * self.scale
        fret_spacing = 15 * self.scale
        num_frets = 5
        num_strings = len(self.variation)

        # Detect if the chord needs an offset (all non-open frets above the 3rd fret)
        non_open_frets = [fret for fret in self.variation if fret > 0]
        min_fret = min(non_open_frets, default=0)  # Use default=0 if no valid frets
        needs_offset = min_fret > 3

        # Calculate offset
        fret_offset = min_fret - 1 if needs_offset else 0

        # Flip x-coordinates if lefty
        def flip_x(x):
            return (num_strings - 1) * string_spacing - x if self.is_lefty else x

        # Draw nut or offset label
        if needs_offset:
            self.canv.setFont("Helvetica-Bold", 8)
            self.canv.drawString(-10, fret_spacing * (num_frets - 1), f"{fret_offset}")
        else:
            self.canv.setLineWidth(2)
            self.canv.line(0, fret_spacing * num_frets, string_spacing * (num_strings - 1), fret_spacing * num_frets)
            self.canv.setLineWidth(1)

        # Draw strings
        for i in range(num_strings):
            x = flip_x(i * string_spacing)
            self.canv.line(x, 0, x, fret_spacing * num_frets)

        # Draw frets
        for i in range(num_frets + 1):
            y = i * fret_spacing
            self.canv.line(0, y, string_spacing * (num_strings - 1), y)

        # Draw chord name
        self.canv.setFont("Helvetica-Bold", 12)
        self.canv.drawCentredString(
            (num_strings - 1) * string_spacing / 2,
            fret_spacing * (num_frets + 1),
            self.chord_name
        )

        # Calculate max height for y-axis flipping
        max_height = num_frets * fret_spacing

        # Draw finger positions (dots)
        self.canv.setFillColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret > 0:  # Ignore open strings
                x = flip_x(string_idx * string_spacing)
                y = max_height - ((fret - fret_offset) - 0.5) * fret_spacing  # Adjust for offset
                self.canv.circle(x, y, 4 * self.scale, fill=1)

        # Draw open strings
        self.canv.setFillColor(colors.white)
        self.canv.setStrokeColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret == 0:  # Open string
                x = flip_x(string_idx * string_spacing)
                y = max_height + 5  # Position above the first fret
                self.canv.circle(x, y, 4 * self.scale, fill=1)



def load_chords(instrument):
    """
    Load chord definitions based on the selected instrument.
    """
    # Dynamically locate the directory where chord files are stored
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
    chord_files_dir = os.path.join(base_dir, '..', 'chord_definitions')  # Adjust path

    file_map = {
        'ukulele': os.path.join(chord_files_dir, 'ukulele_chords.json'),
        'guitar': os.path.join(chord_files_dir, 'guitar_chords.json'),
        'mandolin': os.path.join(chord_files_dir, 'mandolin_chords.json'),
        "banjo": os.path.join(chord_files_dir, "banjo_chords.json"),
        "baritone_ukulele": os.path.join(chord_files_dir, "baritoneUke_chords.json"),
    }

    file_path = file_map.get(instrument, file_map['ukulele'])  # Default to ukulele
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Chord file still not found for {instrument}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}: {e}")
        return []

    
def extract_used_chords(lyrics_with_chords):
    """
    Extract chord names from the lyrics_with_chords JSON structure.
    Handles nested lists and dictionaries containing 'chord' keys.
    """
    chords = set()  # Use a set to avoid duplicates

    def traverse_structure(data):
        """
        Traverse through the JSON structure to find and collect chords.
        """
        if isinstance(data, dict):
            # Check if this dictionary contains a 'chord' key
            if "chord" in data and data["chord"]:
                chords.add(data["chord"])  # Add the chord to the set
            # Recursively check other values in the dictionary
            for value in data.values():
                traverse_structure(value)
        elif isinstance(data, list):
            # Traverse each item in the list
            for item in data:
                traverse_structure(item)

    # Start traversing the provided JSON structure
    traverse_structure(lyrics_with_chords)

    # Debug: Print collected chords
    #print("Extracted chords:", chords)

    # Return the chords as a sorted list
    return sorted(chords)

def draw_footer(canvas, doc, relevant_chords, chord_spacing, row_spacing, is_lefty, instrument="ukulele"):
    """
    Draw footer with chord diagrams at the bottom of the page, dynamically adjusting for the instrument.
    """
    page_width, _ = doc.pagesize
    footer_height = 10  # Height reserved for the footer

    # Instrument-specific adjustments
    string_count = 4 if instrument == "ukulele" else 6  # Default to 4 for ukulele, 6 for guitar
    diagram_scale = 0.6 if instrument == "ukulele" else 0.5  # Scale for diagrams
    min_chord_spacing = 50 if instrument == "ukulele" else 70  # Minimum spacing

    diagrams_to_draw = []
    for chord in relevant_chords:
        diagrams_to_draw.append({
            "name": chord["name"],
            "variation": chord["variations"][0]
        })
        if len(relevant_chords) < 7 and len(chord["variations"]) > 1:  # Display second variation if < 7 chords
            diagrams_to_draw.append({
                "name": chord["name"],
                "variation": chord["variations"][1]
            })

    # Calculate chord_spacing dynamically
    total_diagrams = len(diagrams_to_draw)
    chord_spacing = max((page_width - 2 * doc.leftMargin) / total_diagrams, min_chord_spacing)
    max_chords_per_row = int((page_width - 2 * doc.leftMargin) / chord_spacing)

    # Split diagrams into rows
    rows = [
        diagrams_to_draw[i:i + max_chords_per_row]
        for i in range(0, total_diagrams, max_chords_per_row)
    ]

    # Draw each row of chords
    y_offset = footer_height
    for row in rows:
        total_row_width = len(row) * chord_spacing
        start_x = (page_width - total_row_width) / 2  # Center the row
        canvas.saveState()
        canvas.translate(start_x, y_offset)

        x_offset = 0
        for chord in row:
            diagram = ChordDiagram(chord["name"], chord["variation"], scale=diagram_scale, is_lefty=is_lefty)
            diagram.canv = canvas
            canvas.saveState()
            canvas.translate(x_offset, 0)
            diagram.draw()
            canvas.restoreState()
            x_offset += chord_spacing

        canvas.restoreState()
        y_offset += row_spacing  # Move to the next row
