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

    # Custom paragraph style for reduced line spacing
    reduced_line_style = ParagraphStyle(
        name="ReducedLineStyle",
        parent=styles['BodyText'],
        leading=8,  # Optimal line spacing for readability
        spaceAfter=0,  # Remove default space after paragraphs
    )

    # Prepare the document with adjusted margins
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=24,  # Reasonable top margin for better layout
        bottomMargin=36,
        leftMargin=36,
        rightMargin=36,
    )
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
        [
            Paragraph(f"Time Signature: {time_signature}", styles['Normal']),
            Paragraph(f"<b>{title}</b>", styles['Heading1']),
            Paragraph(f"First Note: {first_note}", styles['Normal']),
        ],
        [
            Paragraph(f"Tempo: {tempo}", styles['Normal']),
            Paragraph(f"Composer: {composer}<br />Lyricist: {lyricist}", styles['Normal']),
            "",
        ],
        [
            Paragraph(f"As recorded by {artist} in {year}", styles['Italic']),
        ],
    ]

    # Create Table with Song Header Data
    header_table = Table(
        header_data,
        colWidths=[150, 300, 150]
    )
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (-1, 2)),  # Merge all cells in the third row
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center Time Signature
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Center Title
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),  # Center First Note
        ('ALIGN', (1, 1), (1, 1), 'CENTER'),  # Center Composer/Lyricist
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
    ]))

    # Add the header table to the top
    elements.append(header_table)
    elements.append(Spacer(1, 24))  # Add space after the header

    # Process lyrics and chords
    lyrics_json = song.lyrics_with_chords
    for section in lyrics_json:
        current_line = []
        for entry in section:
            if "directive" in entry:
                if entry["directive"] == "PARAGRAPHBREAK":
                    if current_line:
                        elements.append(Paragraph(" ".join(current_line), reduced_line_style))
                        current_line = []
                    elements.append(Spacer(1, 24))  # Custom space for paragraph breaks
                continue
            elif "chord" in entry and "lyric" in entry:
                chord = entry["chord"]
                lyric = entry["lyric"]
                formatted_piece = f"<b>[{chord}]</b> {lyric}" if chord else lyric
                current_line.append(formatted_piece)
            elif "format" in entry and entry["format"] == "LINEBREAK":
                if current_line:
                    elements.append(Paragraph(" ".join(current_line), reduced_line_style))
                    current_line = []

        if current_line:
            elements.append(Paragraph(" ".join(current_line), reduced_line_style))

    # Build the PDF
    doc.build(elements)
