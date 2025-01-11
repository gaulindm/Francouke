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
    bridge_style = ParagraphStyle('Chorus', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    chorus_style = ParagraphStyle('Chorus', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    verse_style = ParagraphStyle('Verse', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12)

    elements = []

    songwriter_style = ParagraphStyle(
        'SongwriterStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=14,  # Adjust size if needed
        spaceBefore=6,
        spaceAfter=6
    )

    recording_style = ParagraphStyle(
        'RecordingStyle',
        parent=styles['Normal'],  # Inherit other properties from the Normal style
        alignment=1,  # Center alignment
        fontSize=13,  # Adjust size if needed
        spaceBefore=6,
        spaceAfter=6
    )

    first_vocal_note_style = ParagraphStyle(
        'FirstVocalNoteStyle',
        parent=styles['Normal'],  # Inherit from the Normal style
        alignment=2,  # Right-aligned text
        fontSize=13,  # Optional: Adjust the font size
        spaceBefore=6,  # Optional: Add space above the paragraph
        spaceAfter=6,  # Optional: Add space below the paragraph
    )

    for song in songs:
        #preferences = user.userpreference
        instrument = user.userpreference.instrument
        is_lefty = user.userpreference.is_lefty

        chords = load_chords(instrument)
        used_chords = extract_used_chords(song.lyrics_with_chords)
        relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, used_chords)]






        # Header Section
        metadata = song.metadata or {}
        artist = metadata.get('artist', 'Unknown Artist')
        album = metadata.get('album', 'Unknown')
        songwriter = metadata.get('songwriter', 'Unknown')
        year = metadata.get('year', 'Unknown')
        recording = metadata.get('recording', 'Unknown')

        #song = type('Song', (object,), {'songTitle': "Hey, Good Lookin'"})

       # metadata_text = f"""
       # <b>Artist:</b> {metadata.get('artist', 'Unknown Artist')}<br/>
       # <b>Album:</b> {metadata.get('album', 'Unknown')}<br/>
       # <b>Year:</b> {metadata.get('year', 'Unknown')}<br/>
       # <b>Chords Match YouTube Pitch:</b> {metadata.get('chords_match', 'N/A')}
       # """



        recorded_by_text = f"{metadata.get('recording', 'Unknown')} recording by {metadata.get('artist', 'Unknown Artist')}"
        #if metadata.get('album', ''):
        #    recorded_by_text += f" on {metadata['album']}"
        if metadata.get('year', ''):
            recorded_by_text += f" in {metadata['year']}"

        header_data = [
            [
                Paragraph(f"{metadata.get('timeSignature', '')}", styles['Normal']),
                Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Title']),
                Paragraph(f"First Vocal Note: {metadata.get('1stnote', 'N/A')}", first_vocal_note_style),
            ],
            [
               # Paragraph(f"Tempo: {metadata.get('tempo', '')}", styles['Normal']),    Uncertain of style to adopt
                Paragraph(f"{metadata.get('songwriter', '')}", songwriter_style),  # Ensure style is correct
                "",
                "",
            ],
            [
                Paragraph(recorded_by_text, recording_style),
                "",
                "",
            ],
        ]

        header_table = Table(header_data, colWidths=[120, 360, 120])
        header_table.setStyle(TableStyle([
            ('SPAN', (0, 1), (2, 1)),  # Merge all three cells in the second row
            ('SPAN', (0, 2), (2, 2)),  # Merge all three cells in the third row
            
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells as a base
            ('VALIGN', (1, 1), (1, 1), 'MIDDLE'),  # Specifically center align the songwriter cell
            ('LEFTPADDING', (1, 1), (1, 1), 10),
            ('RIGHTPADDING', (1, 1), (1, 1), 10),
            ('TOPPADDING', (1, 1), (2, 2), 0),
            ('BOTTOMPADDING', (1, 1), (1, 1), 5),
            #('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for debugging
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
