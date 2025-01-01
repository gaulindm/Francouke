from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph,Flowable, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
import json
import os
import re

def draw_footer(canvas, doc, relevant_chords, chord_spacing, row_spacing, is_lefty):
    """
    Draw footer with chord diagrams at the bottom of the page.
    """
    page_width, page_height = doc.pagesize
    footer_height = 10  # Height reserved for the footer
    
    # Calculate maximum number of chords that can fit in a row
    max_chords_per_row = int((page_width - 2 * doc.leftMargin) / chord_spacing)
    
    # Only include the first row of diagrams in the footer
    diagrams_to_draw = relevant_chords[:max_chords_per_row]

    # Calculate the starting x-coordinate to center the diagrams
    total_chords = len(diagrams_to_draw)
    total_diagram_width = total_chords * chord_spacing
    start_x = (page_width - total_diagram_width) / 2



    # Move to the bottom of the page
    canvas.saveState()
    canvas.translate(start_x, footer_height)

    # Draw the chord diagrams
    x_offset = 0
    for chord in diagrams_to_draw:
        diagram = UkuleleDiagram(chord["name"], chord["variations"][0], is_lefty=is_lefty)
        diagram.canv = canvas
        canvas.saveState()
        canvas.translate(x_offset, 0)
        diagram.draw()
        canvas.restoreState()
        x_offset += chord_spacing    
   
    canvas.restoreState()


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


class UkuleleDiagram(Flowable):
    def __init__(self, chord_name, variation, scale=0.65, is_lefty=False):
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



def add_chord_diagrams(elements, relevant_chords, is_lefty=False, chord_spacing=100, row_spacing=24):
    """
    Add ukulele chord diagrams to the PDF, with adjustable spacing between chords and rows.
    """
    max_chords_per_row = 8  # Max chords per row
    diagram_rows = []

    # Create diagram rows
    for i in range(0, len(relevant_chords), max_chords_per_row):
        row = [
            UkuleleDiagram(chord["name"], chord["variations"][0], is_lefty=is_lefty)
            for chord in relevant_chords[i:i + max_chords_per_row]
        ]
        diagram_rows.append(row)

    # Create a table for each row of diagrams
    for row in diagram_rows:
        diagram_table = Table([row], colWidths=[chord_spacing] * len(row))

        # Style the table
        diagram_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(diagram_table)
        elements.append(Spacer(1, row_spacing))  # Spacer between rows



def generate_song_pdf(response, song, user):
    """
    Generate a PDF for a song, including blank ukulele diagrams.
    """



    # Ensure the user has preferences
    if not hasattr(user, "preferences"):
        preferences.objects.create(user=user)


    # Fetch user preferences
    preferences = user.preferences  # Fetch once for clarity
    instrument = preferences.instrument  # Get the instrument
    is_lefty = user.preferences.is_lefty
    #print(f"User's selected instrument: {instrument}, Left-handed: {is_lefty}")


    # Load the appropriate chord definitions
    chords = load_chords(instrument)
    #print("Loaded chords:", chords[:5])  # Debugging loaded chords

    # Extract used chords from the song
    used_chords = extract_used_chords(song.lyrics_with_chords)
    #print("Used chords:", used_chords)

    # Find relevant chords for the song
    relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, used_chords)]
    #print("Relevant chords:", relevant_chords)
    
        # Handle case where no chords are relevant
    if not relevant_chords:
        styles = getSampleStyleSheet()
        elements = [Paragraph("No chords to display.", styles["Normal"])]
        SimpleDocTemplate(response).build(elements)
        return
 

    styles = getSampleStyleSheet()
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
        topMargin=2,
        bottomMargin=12,  # Reserve space for diagrams
        leftMargin=20,
        rightMargin=20,
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
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('SPAN', (0, 2), (-1, 2)),
        ('ALIGN', (0, 2), (0, 2), 'RIGHT'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
#        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Minimal grid lines
    ]))
    elements.append(header_table)    #Goodtable
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
    elements.append(content_table)   #Song content( Songs and chords)

      # --- Chord Diagram Section ---
    elements.append(Spacer(0, 12))


 # --- Dynamic Spacing Calculation ---
    page_width, page_height = letter
    available_width = page_width - 2 * doc.leftMargin  # Subtract left and right margins
    max_chords_per_row = 8  # You can adjust this based on layout preferences
    chord_spacing = available_width / max_chords_per_row
    row_spacing = 72  # Set a default or calculated row spacing

    # --- Chord Diagram Section ---
    #add_chord_diagrams(elements, relevant_chords, is_lefty=is_lefty, chord_spacing=chord_spacing, row_spacing=row_spacing)


 


 
#    add_chord_diagrams(elements, relevant_chords, is_lefty=is_lefty)

    # Build the PDF
    #SimpleDocTemplate(response).build(elements)
   # Build the document
    doc.build(elements, onFirstPage=lambda c, d: draw_footer(c, d, relevant_chords, chord_spacing, row_spacing, is_lefty),
              onLaterPages=lambda c, d: draw_footer(c, d, relevant_chords, chord_spacing, row_spacing, is_lefty))

    