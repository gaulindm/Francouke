from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

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
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Add song title and artist
    elements.append(Paragraph(f"<b>{song.songTitle}</b>", styles['Heading1']))
    elements.append(Paragraph(f"Artist: {song.metadata.get('artist', 'Unknown')}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Process the JSON structure of lyrics_with_chords
    lyrics_json = song.lyrics_with_chords
    for section in lyrics_json:
        for entry in section:
            if "directive" in entry:
                # Handle directives (e.g., section titles)
                directive = entry["directive"]
                elements.append(Paragraph(f"<i>{directive}</i>", styles['BodyText']))
                elements.append(Spacer(1, 6))
            elif "chord" in entry and "lyric" in entry:
                # Handle lyrics with chords
                chord = entry["chord"]
                lyric = entry["lyric"]
                formatted_line = f"<b>{chord}</b> {lyric}" if chord else lyric
                elements.append(Paragraph(formatted_line, styles['BodyText']))
                elements.append(Spacer(1, 6))
            elif "format" in entry:
                # Handle formatting directives
                if entry["format"] == "LINEBREAK":
                    elements.append(Spacer(1, 6))
                elif entry["format"] == "PARAGRAPHBREAK":
                    elements.append(Spacer(1, 12))

    # Build and return the PDF
    doc.build(elements)
