from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable, Table, TableStyle, Spacer
from django.conf import settings
import json
import os
import re

import re

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
    print("Extracted chords:", chords)

    # Return the chords as a sorted list
    return sorted(chords)



def load_chords(instrument):
    """
    Load chord definitions based on the selected instrument.
    """
    file_map = {
        'ukulele': os.path.join('static', 'js', 'ukulele_chords.json'),
        'guitar': os.path.join('static', 'js', 'guitar_chords.json'),
        'mandolin': os.path.join('static', 'js', 'mandolin_chords.json'),
        "banjo": os.path.join("static", "js", "banjo_chords.json"),
        "baritone_ukulele": os.path.join("static", "js", "baritoneUke_chords.json"),
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



def print_chord_definition(chords, chord_name):
    """
    Print the definition for a specific chord by name.
    """
    for chord in chords:
        if chord["name"] == chord_name:
            print(f"Chord '{chord_name}' definition: {chord}")
            return chord
    print(f"Chord '{chord_name}' not found in definitions.")
    return None

from reportlab.platypus import Flowable
from reportlab.lib import colors

class UkuleleDiagram(Flowable):
    """
    A Flowable to render a ukulele chord diagram based on a specific variation.
    """
    def __init__(self, chord_name, variation, scale=0.75, is_lefty=False):
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

        # Flip x-coordinates if lefty
        def flip_x(x):
            return (num_strings - 1) * string_spacing - x if self.is_lefty else x


    # Draw strings
        for i in range(num_strings):
            x = flip_x(i * string_spacing)
            self.canv.line(x, 0, x, fret_spacing * num_frets)

        # Draw frets
        for i in range(num_frets + 1):
            y = i * fret_spacing
            self.canv.line(0, y, string_spacing * (num_strings - 1), y)

        # Draw chord name
        self.canv.setFont("Helvetica-Bold", 10)
        self.canv.drawCentredString(
            (num_strings - 1) * string_spacing / 2,
            fret_spacing * (num_frets + 0.5),
            self.chord_name
        )

        # Calculate max height for y-axis flipping
        max_height = num_frets * fret_spacing

        # Draw finger positions (dots)
        self.canv.setFillColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret > 0:  # Ignore open strings
                x = flip_x(string_idx * string_spacing)
                y = max_height - (fret - 0.5) * fret_spacing  # Flip y-axis
                self.canv.circle(x, y, 4 * self.scale, fill=1)

        # Draw open strings
        self.canv.setFillColor(colors.white)
        self.canv.setStrokeColor(colors.black)
        for string_idx, fret in enumerate(self.variation):
            if fret == 0:  # Open string
                x = flip_x(string_idx * string_spacing)
                y = max_height + 5  # Position above the first fret
                self.canv.circle(x, y, 4 * self.scale, fill=1)


def add_chord_diagrams(elements, relevant_chords, is_lefty=False):
    """
    Add ukulele chord diagrams to the PDF using JSON chord data.
    """ 

    from reportlab.platypus import Table, TableStyle, Spacer

    diagram_row = [
        UkuleleDiagram(chord["name"], chord["variations"][0], is_lefty=is_lefty)  # Use the first variation
        for chord in relevant_chords[:6]
    ]
    diagram_table = Table([diagram_row], colWidths=[100] * len(diagram_row))

    # Style the table
    diagram_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    elements.append(Spacer(1, 48))  # Adjust as necessary
    elements.append(diagram_table)
       


def generate_song_pdf(response, song, user):
    """
    Generate a PDF for a song, including blank ukulele diagrams.
    """



    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    # Ensure the user has preferences
    if not hasattr(user, "preferences"):
        preferences.objects.create(user=user)


    # Fetch user preferences
    preferences = user.preferences  # Fetch once for clarity
    instrument = preferences.instrument  # Get the instrument

    is_lefty = user.preferences.is_lefty
    print(f"User's selected instrument: {instrument}, Left-handed: {is_lefty}")


    # Load the appropriate chord definitions
    chords = load_chords(instrument)
    print("Loaded chords:", chords[:5])  # Debugging loaded chords

    # Extract used chords from the song
    used_chords = extract_used_chords(song.lyrics_with_chords)
    print("Used chords:", used_chords)

    # Find relevant chords for the song
    relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, used_chords)]
    print("Relevant chords:", relevant_chords)
    
        # Handle case where no chords are relevant
    if not relevant_chords:
        styles = getSampleStyleSheet()
        elements = [Paragraph("No chords to display.", styles["Normal"])]
        SimpleDocTemplate(response).build(elements)
        return
 

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(response)

    elements = []



    # Define base styles (unchanged from your code)
    base_style = ParagraphStyle(
        name="BaseStyle",
        parent=styles['BodyText'],
        fontSize=14,
        leading=14,
    )
    heading_style = ParagraphStyle(name="Heading", parent=base_style, fontSize=16, spaceAfter=12)
    lyric_style = ParagraphStyle(name="LyricStyle", parent=base_style, fontSize=12)
    centered_style = ParagraphStyle(name="CenteredStyle", parent=base_style, alignment=1)

    # Document setup
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=24,
        bottomMargin=72,  # Reserve space for diagrams
        leftMargin=36,
        rightMargin=36,
    )
    elements = []

    # --- Header Section ---
    metadata = song.metadata or {}
    header_data = [
        [
            Paragraph(f"Time Signature: {metadata.get('timeSignature', 'Unknown')}", styles['Normal']),
            Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", centered_style),
            Paragraph(f"First Vocal Note: {metadata.get('1stnote', 'N/A')}", styles['Normal']),
        ],
        [
            Paragraph(f"Tempo: {metadata.get('tempo', 'Unknown')}", styles['Normal']),
            Paragraph(f"Songwriter: {metadata.get('songwriter', 'Unknown')}", centered_style),
            "",
        ],
        [
            Paragraph(f"As recorded by {metadata.get('artist', 'Unknown Artist')} on {metadata.get('album', 'Unknown album')} in {metadata.get('year', 'Unknown')}", centered_style),
            "",
            "",
        ],
    ]

    header_table = Table(header_data, colWidths=[150, 300, 150])
    header_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), -1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
        ('SPAN', (0, 2), (-1, 2)),
        ('ALIGN', (0, 2), (0, 2), 'RIGHT'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # --- Content Section ---
    # (Same as your current implementation)
    lyrics_with_chords = song.lyrics_with_chords or []
    content_table_data = []
    centered_lyric_style = ParagraphStyle(
        name="CenteredLyricStyle",
        parent=styles['BodyText'],
        alignment=1,
        leading=14,
        fontSize=12,
        spaceAfter=6,
    )

    paragraph_buffer = []
    is_soc_active = False

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                if item["directive"] == "{soc}":
                    is_soc_active = True
                    continue
                elif item["directive"] == "{eoc}":
                    is_soc_active = False
                    continue
                continue
            elif "format" in item:
                if item["format"] == "LINEBREAK":
                    paragraph_buffer.append("<br/>")
                elif item["format"] == "PARAGRAPHBREAK":
                    if paragraph_buffer:
                        paragraph_text = " ".join(paragraph_buffer)
                        if is_soc_active:
                            content_table_data.append([Paragraph(paragraph_text, centered_lyric_style)])
                        else:
                            content_table_data.append([Paragraph(paragraph_text, lyric_style)])
                        paragraph_buffer = []
            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]
                if chord:
                    paragraph_buffer.append(f"<b>[{chord}]</b> {lyric}")
                else:
                    paragraph_buffer.append(lyric)

        if paragraph_buffer:
            paragraph_text = " ".join(paragraph_buffer)
            if is_soc_active:
                content_table_data.append([Paragraph(paragraph_text, centered_lyric_style)])
            else:
                content_table_data.append([Paragraph(paragraph_text, lyric_style)])
            paragraph_buffer = []

    content_table = Table(content_table_data, colWidths=[500])
    elements.append(content_table)

      # --- Chord Diagram Section ---
    elements.append(Spacer(1, 24))


    # Create a table to align diagrams horizontally
    diagram_row = [
        UkuleleDiagram(chord["name"], chord["variations"][0])  # Use the first variation
        for chord in relevant_chords
        if "variations" in chord and chord["variations"]  # Ensure variations exist
    ][:4]  # Limit to 4 diagrams


    # Create a table to layout diagrams horizontally
    diagram_table = Table([diagram_row], colWidths=[60] * 4)  # Adjust width as needed

    # Style the table
    diagram_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    # Add the diagram table to the PDF
 
    add_chord_diagrams(elements, relevant_chords, is_lefty=is_lefty)

    # Build the PDF
    SimpleDocTemplate(response).build(elements)

    