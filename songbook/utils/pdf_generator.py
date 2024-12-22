from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable, Table, TableStyle, Spacer
from django.conf import settings
import json
import os

def load_chords():
    chord_file = os.path.join(settings.BASE_DIR, "static", "js", "ukulele_chords.json")
    print(f"Resolved chord file path: {chord_file}")  # Debugging statement
    try:
        with open(chord_file, "r") as file:
            chords = json.load(file)
        return chords
    except FileNotFoundError:
        print(f"Error: File not found at {chord_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {chord_file}: {e}")
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



class UkuleleDiagram(Flowable):
    """
    A Flowable to render a ukulele chord diagram.
    """
    def __init__(self):
        Flowable.__init__(self)

    def draw(self):
        # Diagram dimensions
        scale = 0.75
        string_spacing = 15 * scale
        fret_spacing = 15 * scale
        num_frets = 4
        num_strings = 4

        # Draw vertical strings
        for i in range(num_strings):
            x = i * string_spacing
            self.canv.line(x, 0, x, fret_spacing * num_frets)

        # Draw horizontal frets
        for i in range(num_frets + 1):
            y = i * fret_spacing
            self.canv.line(0, y, string_spacing * (num_strings - 1), y)

def add_chord_diagrams(elements):
    """
    Add a row of four ukulele chord diagrams to the bottom of the PDF,
    scaled down to 75%.
    """
    # Create a table to align diagrams horizontally
    diagram_row = [UkuleleDiagram() for _ in range(4)]
    diagram_table = Table([diagram_row], colWidths=[60] * 4)  # Adjust width as needed

    # Style the table
    diagram_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))

    # Add space to ensure the diagrams are near the bottom
    elements.append(Spacer(1, 24))  # Adjust as necessary
    elements.append(diagram_table)            


def generate_song_pdf(response, song):
    """
    Generate a PDF for a song, including blank ukulele diagrams.
    """



    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors


    chords = load_chords()
    styles = getSampleStyleSheet()

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
    diagram_row = [UkuleleDiagram() for _ in range(4)]
    diagram_table = Table([diagram_row], colWidths=[60] * 4)  # Adjust width as needed

    # Style the table
    diagram_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    # Add the diagram table to the PDF
 
    add_chord_diagrams(elements)

    # Build the PDF
    doc.build(elements)

    