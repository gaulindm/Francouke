from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
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
    # Define custom styles
    styles = {
        'Title': ParagraphStyle('Title', fontSize=18, leading=22, alignment=1, spaceAfter=12, textColor=colors.darkblue),
        'Artist': ParagraphStyle('Artist', fontSize=14, leading=18, spaceAfter=12, textColor=colors.black),
        'BodyText': ParagraphStyle('BodyText', fontSize=12, leading=15, spaceAfter=6),
        'Directive': ParagraphStyle('Directive', fontSize=12, leading=15, textColor=colors.gray, italic=True, spaceAfter=6),
    }

    # PDF setup
    doc = SimpleDocTemplate(
        response, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    elements = []

    # Add song title and artist
    elements.append(Paragraph(f"<b>{song.songTitle}</b>", styles['Title']))
    elements.append(Paragraph(f"Artist: {song.metadata.get('artist', 'Unknown')}", styles['Artist']))
    elements.append(Spacer(1, 12))

    # Process the JSON structure of lyrics_with_chords
    lyrics_json = song.lyrics_with_chords
    if not isinstance(lyrics_json, list):
        raise ValueError("lyrics_with_chords should be a list of sections.")

    for section in lyrics_json:
        for entry in section:
            if "directive" in entry:
                directive_text = entry["directive"].capitalize()
                elements.append(Paragraph(f"<i>{directive_text}</i>", styles['Directive']))
                elements.append(Spacer(1, 6))
            elif "chord" in entry and "lyric" in entry:
                chord = entry["chord"]
                lyric = entry["lyric"]
                data = [[f"<b>{chord}</b>", lyric]]
                table = Table(data, colWidths=[50, None])
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 6))
            elif "format" in entry:
                if entry["format"] == "LINEBREAK":
                    elements.append(Spacer(1, 6))
                elif entry["format"] == "PARAGRAPHBREAK":
                    elements.append(Spacer(1, 12))

    # Build and return the PDF
    try:
        doc.build(elements)
    except Exception as e:
        raise RuntimeError(f"Failed to generate PDF: {e}")
