from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def generate_song_pdf(response, song):
    """
    Generates a PDF for a single song and writes it to the given HTTP response.

    Args:
        response: HttpResponse object for writing the PDF content.
        song: Song object containing the song data.

    Returns:
        None
    """
    styles = getSampleStyleSheet()

    # Create a custom paragraph style with reduced line spacing
    reduced_line_style = ParagraphStyle(
        name="ReducedLineStyle",
        parent=styles['BodyText'],  # Base it on BodyText
        leading=10,  # Reduced line height
        spaceAfter=0  # Remove additional space after paragraphs
    )

    # Prepare the document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Extract metadata for the song header
    title = song.songTitle
    artist = song.metadata.get('artist', 'Unknown Artist')
    time_signature = song.metadata.get('timeSignature', 'Unknown')
    tempo = song.metadata.get('tempo', 'Unknown')
    composer = song.metadata.get('composer', 'Unknown Composer')
    lyricist = song.metadata.get('lyricist', 'Unknown Lyricist')
    year = song.metadata.get('year', 'Unknown Year')
    first_note = song.metadata.get('1stnote', 'N/A')  # Retrieve 1st note directly from metadata

    # Song Header Table Data
    header_data = [
        [  # Row 1: Time Signature, Title, First Note
            Paragraph(f"Time Signature: {time_signature}", styles['Normal']),
            Paragraph(f"<b>{title}</b>", styles['Heading1']),
            Paragraph(f"First Note: {first_note}", styles['Normal']),
        ],
        [  # Row 2: Tempo, Composer/Lyricist, Empty
            Paragraph(f"Tempo: {tempo}", styles['Normal']),
            Paragraph(f"Composer: {composer}<br />Lyricist: {lyricist}", styles['Normal']),
            "",
        ],
        [  # Row 3: Merged row with "As recorded by artist"
            Paragraph(f"As recorded by {artist} in {year}", styles['Italic']),
        ],
    ]

    # Create Table with Song Header Data
    header_table = Table(
        header_data,
        colWidths=[150, 300, 150]  # Column widths for Time Signature, Title, First Note
    )

    # Table Styling
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (-1, 2)),  # Merge all cells in the third row
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Align Time Signature to the left
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Center-align the Title
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),  # Align First Note to the right
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Padding between rows
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),  # Optional background color
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),  # Underline the first row
    ]))

    # Add the header table at the very top
    elements = [header_table, Spacer(1, 12)]  # Add the header with initial spacing

    # Process the JSON structure of lyrics_with_chords
    lyrics_json = song.lyrics_with_chords
    for section in lyrics_json:
        current_line = []  # To collect entries for the current line
        for entry in section:
            if "directive" in entry:
                if entry["directive"] == "PARAGRAPHBREAKER":
                    # Add a paragraph break spacer
                    if current_line:
                        elements.append(Paragraph(" ".join(current_line), reduced_line_style))
                        current_line = []  # Reset for the next line
                    elements.append(Spacer(1, 18))  # Wider space for paragraph break
                continue  # Skip directives in general
            elif "chord" in entry and "lyric" in entry:
                chord = entry["chord"]
                lyric = entry["lyric"]
                formatted_piece = f"<b>[{chord}]</b> {lyric}" if chord else lyric
                current_line.append(formatted_piece)
            elif "format" in entry and entry["format"] == "LINEBREAK":
                # End the current line without adding a spacer
                if current_line:
                    elements.append(Paragraph(" ".join(current_line), reduced_line_style))
                    current_line = []  # Reset for the next line

        # Handle any remaining line at the end of the section
        if current_line:
            elements.append(Paragraph(" ".join(current_line), reduced_line_style))

    # Build and return the PDF
    doc.build(elements)
