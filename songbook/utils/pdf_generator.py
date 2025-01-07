from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph,Flowable, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
import json
import os
import re
from .chord_utils import load_chords, extract_used_chords, add_chord_diagrams, draw_footer, ChordDiagram



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .chord_utils import load_chords, extract_used_chords, draw_footer



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from .chord_utils import load_chords, extract_used_chords, draw_footer

def generate_songs_pdf(response, songs, user):
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=2,
        bottomMargin=12,
        leftMargin=20,
        rightMargin=20,
    )
    styles = getSampleStyleSheet()
    base_style = styles['BodyText']
    chorus_style = ParagraphStyle('Chorus', parent=base_style, fontSize=12, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    verse_style = ParagraphStyle('Verse', parent=base_style, fontSize=12, leading=14, spaceBefore=12, spaceAfter=12)

    elements = []

    for song in songs:
        preferences = user.userpreference
        instrument = user.userpreference.instrument
        is_lefty = user.userpreference.is_lefty

        chords = load_chords(instrument)
        used_chords = extract_used_chords(song.lyrics_with_chords)
        relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, used_chords)]

        # Header Section
        metadata = song.metadata or {}
        header_data = [
            [
                Paragraph(f"Time Signature: {metadata.get('timeSignature', 'Unknown')}", styles['Normal']),
                Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Title']),
                Paragraph(f"First Vocal Note: {metadata.get('1stnote', 'N/A')}", styles['Normal']),
            ],
            [
                Paragraph(f"Tempo: {metadata.get('tempo', 'Unknown')}", styles['Normal']),
                Paragraph(f"Songwriter: {metadata.get('songwriter', 'Unknown')}", styles['Normal']),
                "",
            ],
            [
                Paragraph(f"As recorded by {metadata.get('artist', 'Unknown Artist')} on {metadata.get('album', 'Unknown album')} in {metadata.get('year', 'Unknown')}", styles['Normal']),
                "",
                "",
            ],
        ]

        header_table = Table(header_data, colWidths=[150, 300, 150])
        header_table.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))

        # Lyrics Section with section handling
        lyrics_with_chords = song.lyrics_with_chords or []
        paragraph_buffer = []
        is_chorus = False

        for group in lyrics_with_chords:
            for item in group:
                if "directive" in item:
                    if item["directive"] == "{soc}":
                        is_chorus = True
                        if paragraph_buffer:
                            elements.append(Paragraph(" ".join(paragraph_buffer), verse_style))
                            paragraph_buffer = []
                        continue
                    elif item["directive"] == "{eoc}":
                        is_chorus = False
                        if paragraph_buffer:
                            elements.append(Paragraph(" ".join(paragraph_buffer), chorus_style))
                            paragraph_buffer = []
                        continue
                elif "format" in item:
                    if item["format"] == "LINEBREAK":
                        paragraph_buffer.append("<br/>")
                    elif item["format"] == "PARAGRAPHBREAK":
                        if paragraph_buffer:
                            paragraph_text = " ".join(paragraph_buffer)
                            style = chorus_style if is_chorus else verse_style
                            elements.append(Paragraph(paragraph_text, style))
                            paragraph_buffer = []
                elif "lyric" in item:
                    chord = item.get("chord", "")
                    lyric = item["lyric"]
                    paragraph_buffer.append(f"<b>[{chord}]</b> {lyric}" if chord else lyric)

            if paragraph_buffer:
                paragraph_text = " ".join(paragraph_buffer)
                style = chorus_style if is_chorus else verse_style
                elements.append(Paragraph(paragraph_text, style))
                paragraph_buffer = []

        elements.append(PageBreak())  # Separate songs by page

    # Define spacing and build the document
    page_width, page_height = letter
    available_width = page_width - 2 * doc.leftMargin
    max_chords_per_row = 8
    chord_spacing = available_width / max_chords_per_row
    row_spacing = 72

    doc.build(elements, 
              onFirstPage=lambda c, d: draw_footer(c, d, relevant_chords, chord_spacing, row_spacing, is_lefty),
              onLaterPages=lambda c, d: draw_footer(c, d, relevant_chords, chord_spacing, row_spacing, is_lefty))





"""
#def generate_song_pdf(response, song, user):

    Generate a PDF for a song, including blank ukulele diagrams.




    # Ensure the user has preferences
    if not hasattr(user, "userpreference"):
        preferences.objects.create(user=user)


    # Fetch user preferences
    preferences = user.userpreference  # Fetch once for clarity
    instrument = preferences.instrument  # Get the instrument
    is_lefty = user.userpreference.is_lefty
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

    """