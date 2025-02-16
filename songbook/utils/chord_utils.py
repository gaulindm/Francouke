import os
import json
from django.conf import settings
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Table, TableStyle, Spacer, Flowable
from reportlab.lib import colors
from reportlab.lib.units import inch

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
            self.canv.setFont("Helvetica-Bold", 10)  # Slightly larger font
            self.canv.setFillColor(colors.red)  # Use a distinct color
            self.canv.drawString(-15, fret_spacing * (num_frets - 1) + 5, f"{fret_offset}")
            self.canv.setFillColor(colors.black)  # Reset color for other elements
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
                adjusted_fret = fret - fret_offset
                if adjusted_fret > 0:  # Only draw if the fret is within the diagram
                    x = flip_x(string_idx * string_spacing)
                    y = max_height - ((adjusted_fret - 0.5) * fret_spacing)
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
    #base_dir = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
    #chord_files_dir = os.path.join(base_dir, '..', 'chord_definitions')  # Adjust path
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'js')  # Adjust path for static location


    file_map = {
        'ukulele': os.path.join(static_dir, 'ukulele_chords.json'),
        'guitar': os.path.join(static_dir, 'guitar_chords.json'),
        'mandolin': os.path.join(static_dir, 'mandolin_chords.json'),
        "banjo": os.path.join(static_dir, "banjo_chords.json"),
        "baritone_ukulele": os.path.join(static_dir, "baritoneUke_chords.json"),
    }

    file_path = file_map.get(instrument, file_map['ukulele'])  # Default to ukulele
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Chord file not found for {instrument}")
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

def draw_footer(
    canvas, doc, relevant_chords, chord_spacing, row_spacing, 
    is_lefty, instrument="ukulele", secondary_instrument=None,
    is_printing_alternate_chord=False, acknowledgement=''
):
    """
    Draw footer with chord diagrams, handling both primary and secondary instruments.
    """

    # Page dimensions
    page_width, _ = doc.pagesize
    footer_height = 36  

    # Instrument-specific adjustments
    min_chord_spacing = 10 if instrument == "ukulele" else 70

    # Categorize chords by instrument
    primary_chords = [chord for chord in relevant_chords if chord.get("instrument") == instrument]
    secondary_chords = [chord for chord in relevant_chords if secondary_instrument and chord.get("instrument") == secondary_instrument]

    def prepare_chords(chords):
        diagrams = []
        for chord in chords:
            diagrams.append({
                "name": chord["name"],
                "variation": chord["variations"][0]
            })
            if is_printing_alternate_chord and len(chord["variations"]) > 1:
                diagrams.append({
                    "name": chord["name"],
                    "variation": chord["variations"][1]
                })
        return diagrams

    primary_diagrams = prepare_chords(primary_chords)
    secondary_diagrams = prepare_chords(secondary_chords)

    total_primary = len(primary_diagrams)
    total_secondary = len(secondary_diagrams)
    
    # Single instrument scenario: center align
    if not secondary_instrument:
    
        start_x = (page_width - (total_primary * chord_spacing)) / 2
    
        sections = [(primary_diagrams, start_x)]
    
    # Dual instrument scenario: split left and right
    else:
        mid_x = page_width / 2
        primary_x = mid_x / 2 - (total_primary * chord_spacing) / 2
        secondary_x = mid_x + (mid_x / 2) - (total_secondary * chord_spacing) / 2
        sections = [(primary_diagrams, primary_x), (secondary_diagrams, secondary_x)]
    


    y_offset = footer_height
    for diagrams, start_x in sections:
        total_width = len(diagrams) * chord_spacing
        canvas.saveState()
        canvas.translate(start_x, y_offset)

        x_offset = 0
        for chord in diagrams:
            diagram = ChordDiagram(
                chord["name"], chord["variation"], 
                scale=0.5, is_lefty=is_lefty
            )
            diagram.canv = canvas
            canvas.saveState()
            canvas.translate(x_offset, 0)
            diagram.draw()
            canvas.restoreState()
            x_offset += chord_spacing

        canvas.restoreState()

    # Draw labels for instruments only if both are present
    if secondary_instrument and total_secondary > 0:
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawCentredString(mid_x / 2, y_offset + 60, instrument.title())  # Centered in left half
        canvas.drawCentredString(mid_x + (mid_x / 2), y_offset + 60, secondary_instrument.title())  # Centered in right half


    if acknowledgement:
        canvas.setFont("Helvetica-Oblique", 10)
        canvas.drawCentredString(
            doc.pagesize[0] / 2, 0.2 * inch,  
            f"Gracieusté de: {acknowledgement}"
        )  
