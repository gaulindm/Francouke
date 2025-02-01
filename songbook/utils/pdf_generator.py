from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Paragraph,Flowable, Table, TableStyle, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.platypus.flowables import Flowable
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak
import json
import os
import re
from .chord_utils import load_chords, extract_used_chords, draw_footer, ChordDiagram

def generate_songs_pdf(response, songs, user):
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=2,
        bottomMargin=80,
        leftMargin=20,
        rightMargin=20,
    )
    styles = getSampleStyleSheet()
    base_style = styles['BodyText']
    chorus_style = ParagraphStyle('Chorus', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    verse_style = ParagraphStyle('Verse', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12)
    intro_style = ParagraphStyle('Intro', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12)
    outro_style = ParagraphStyle('Outro', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    bridge_style = ParagraphStyle('Bridge', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)
    interlude_style = ParagraphStyle('Bridge', parent=base_style, fontSize=13, leading=14, spaceBefore=12, spaceAfter=12, alignment=1)

    elements = []



    # Get user preferences
    instrument = user.userpreference.instrument
    is_lefty = user.userpreference.is_lefty
    is_printing_alternate_chord = user.userpreference.is_printing_alternate_chord


    # Load chords and extract relevant ones
    chords = load_chords(instrument)
    used_chords = extract_used_chords(songs[0].lyrics_with_chords)  # Assuming one song for simplicity
    relevant_chords = [chord for chord in chords if chord["name"].lower() in map(str.lower, used_chords)]

    diagrams_to_draw = []
    for chord in relevant_chords:
        diagrams_to_draw.append({
            "name": chord["name"],
            "variation": chord["variations"][0]
        })
        if is_printing_alternate_chord and len(chord["variations"]) > 1:
            diagrams_to_draw.append({
                "name": chord["name"],
                "variation": chord["variations"][1]
            })


    # Calculate diagrams per row and rows needed
    chord_spacing = 50 if instrument == "ukulele" else 70  # Adjust spacing per instrument
    page_width, page_height = letter
    max_chords_per_row = int((page_width - 2 * doc.leftMargin) / chord_spacing)
    total_diagrams = len(relevant_chords) * (2 if len(relevant_chords) < 7 else 1)  # Include 2 variations if < 7 chords
    rows_needed = (total_diagrams + max_chords_per_row - 1) // max_chords_per_row  # Calculate rows needed

    row_spacing = 72  # Space between rows
    diagram_height = rows_needed * row_spacing

    # Adjust bottom margin dynamically
    if rows_needed > 1:
        doc.bottomMargin = max(80, diagram_height + 20)  # Ensure there's enough space for diagrams

    # Debugging output
    print(f"Total diagrams: {total_diagrams}, Rows needed: {rows_needed}, Bottom margin: {doc.bottomMargin}")



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
        fontSize=12,  # Optional: Adjust the font size
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

        #chorus_line_buffer = []
        #is_chorus = False
        #refrain_added = False

 

        # Initialize necessary variables
        section_type = None  # Tracks active section (Chorus, Intro, Bridge, Outro)
        section_buffer = []  # Stores lyrics inside structured sections
        section_table_data = []  # Stores formatted section content
        paragraph_buffer = []  # Stores unstructured verses (normal lyrics)

        for group in lyrics_with_chords:
            for item in group:
                if "directive" in item:
                    # Detect the start of a structured section
                    if item["directive"] in ["{soc}", "{soi}", "{sob}", "{soo}", "{sod}"]:
                        # Store any buffered verse before switching sections
                        if paragraph_buffer:
                            elements.append(Paragraph(" ".join(paragraph_buffer), verse_style))
                            elements.append(Spacer(1, 12))
                            paragraph_buffer = []

                        # Set section type
                        section_type = {
                            "{soc}": "Chorus",
                            "{soi}": "Intro",
                            "{sob}": "Bridge",
                            "{soo}": "Outro",
                            "{sod}": "Interlude"
                        }[item["directive"]]

                        section_table_data = []
                        section_buffer = []
                        continue

                    # Detect the end of a structured section
                    elif item["directive"] in ["{eoc}", "{eoi}", "{eob}", "{eoo}", "{eod}"]:
                        if section_type and section_buffer:
                            section_table_data.append([
                                "", 
                                Paragraph(" ".join(section_buffer), 
                                    chorus_style if section_type == "Chorus" 
                                    else intro_style if section_type == "Intro" 
                                    else bridge_style if section_type == "Bridge" 
                                    else outro_style if section_type == "Outro"
                                    else interlude_style)  # New Interlude Formatting
                            ])


                        if section_type and section_table_data:
                            # Insert section name at (0,0)
                            section_table_data.insert(0, [
                                Paragraph(f"<b>{section_type}:</b>", base_style), 
                                section_table_data.pop(0)[1]
                            ])

                            section_table = Table(section_table_data, colWidths=[80, 440], hAlign='LEFT')
                            section_table.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                                #('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for debugging
                            ]))

                            elements.append(section_table)
                            elements.append(Spacer(1, 12))

                        # Reset section tracking
                        section_type = None
                        section_buffer = []
                        continue

                elif "format" in item:
                    if item["format"] == "LINEBREAK":
                        if section_type and section_buffer:
                            full_line = " ".join(section_buffer)
                            section_table_data.append(["", Paragraph(full_line, 
                                chorus_style if section_type == "Chorus" 
                                else intro_style if section_type == "Intro" 
                                else bridge_style if section_type == "Bridge" 
                                else outro_style)])
                            section_buffer = []   

                        elif not section_type and paragraph_buffer:
                            paragraph_buffer.append("<br/>")  # Keep verse formatting

                    elif item["format"] == "PARAGRAPHBREAK":
                        if paragraph_buffer:
                            paragraph_text = " ".join(paragraph_buffer)
                            style = verse_style  # Verses always use verse_style
                            elements.append(Paragraph(paragraph_text, style))
                            elements.append(Spacer(1, 12))
                            paragraph_buffer = []

                elif "lyric" in item:
                    chord = item.get("chord", "")
                    lyric = item["lyric"]
                    line = f"<b>[{chord}]</b> {lyric}" if chord else lyric

                    if section_type:
                        section_buffer.append(line)  # Store for structured sections
                    else:
                        paragraph_buffer.append(line)  # Store for normal verses

        # Ensure any remaining structured section is processed
        if section_type and section_buffer:
            section_table_data.append([
                "", 
                Paragraph(" ".join(section_buffer), 
                    chorus_style if section_type == "Chorus" 
                    else intro_style if section_type == "Intro" 
                    else bridge_style if section_type == "Bridge" 
                    else outro_style)
            ])

        if section_type and section_table_data:
            section_table_data.insert(0, [
                Paragraph(f"<b>{section_type}:</b>", base_style), 
                section_table_data.pop(0)[1]
            ])

            section_table = Table(section_table_data, colWidths=[80, 440], hAlign='CENTER')
            section_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(section_table)
            elements.append(Spacer(1, 12))

        # Ensure any remaining verse is added as a paragraph
        if paragraph_buffer:
            elements.append(Paragraph(" ".join(paragraph_buffer), verse_style))
            elements.append(Spacer(1, 12))
            paragraph_buffer = []



        elements.append(PageBreak())  # Separate songs by page

    # Define spacing and build the document
    page_width, page_height = letter
    available_width = page_width - 2 * doc.leftMargin
    max_chords_per_row = 8
    chord_spacing = available_width / max_chords_per_row
    row_spacing = 72

    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_footer(
            c, d, relevant_chords, chord_spacing, row_spacing, is_lefty,
            instrument=instrument,
            is_printing_alternate_chord=user.userpreference.is_printing_alternate_chord
        ),
        onLaterPages=lambda c, d: draw_footer(
            c, d, relevant_chords, chord_spacing, row_spacing, is_lefty,
            instrument=instrument,
            is_printing_alternate_chord=user.userpreference.is_printing_alternate_chord
        )
    )

