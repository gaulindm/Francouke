from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


def generate_song_pdf(response, song):
    """
    Generate a PDF for a song using tables for the header and content,
    with one table row per paragraph (determined by PARAGRAPHBREAK).
    """
    styles = getSampleStyleSheet()


    # Define a custom base style for the whole page
    base_style = ParagraphStyle(
        name="BaseStyle",
        parent=styles['BodyText'],  # Use BodyText as the base
        fontSize=14,  # Set desired font size
        leading=14,  # Set line spacing
    )

    # Update existing styles to inherit from base_style
    heading_style = ParagraphStyle(name="Heading", parent=base_style, fontSize=16, spaceAfter=12)
    lyric_style = ParagraphStyle(name="LyricStyle", parent=base_style, fontSize=12)
    centered_style = ParagraphStyle(name="CenteredStyle", parent=base_style, alignment=1)




    # Custom paragraph style for lyrics and chords
    lyric_style = ParagraphStyle(
        name="LyricStyle",
        parent=styles['BodyText'],
        leading=14,
        fontSize=12,
        spaceAfter=6,
    )

    # Document setup
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        topMargin=24,
        bottomMargin=36,
        leftMargin=36,
        rightMargin=36,
    )
    elements = []

    # Custom style for centered text
    centered_style = ParagraphStyle(
        name="CenteredStyle",
        parent=styles['Normal'],
        fontSize=12,
        borderPadding=2,
        alignment=1,  # 1 = Center
    )

    # --- Song Header ---
    metadata = song.metadata or {}
    
    header_data = [
        [
            Paragraph(f"Time Signature: {metadata.get('timeSignature', 'Unknown')}", styles['Normal']),
            Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", centered_style),  # Centered song title
            Paragraph(f"First Vocal Note: {metadata.get('1stnote', 'N/A')}", styles['Normal']),
        ],
        [
            Paragraph(f"Tempo: {metadata.get('tempo', 'Unknown')}", styles['Normal']),
            Paragraph(f"Songwriter: {metadata.get('songwriter', 'Unknown')}", centered_style),  # Centered songwriter
            "",
        ],
        [
            Paragraph(f"As recorded by {metadata.get('artist', 'Unknown Artist')} in {metadata.get('year', 'Unknown')}", centered_style),  # Centered artist
            "",
            "",
        ],
    ]

    header_table = Table(header_data, colWidths=[150, 300, 150])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (-1, 2)),  # Merge the last row
        ('ALIGN', (0, 2), (0, 2), 'RIGHT'),  # Right aligned
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align all cells to center (double-check alignment)
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
       # ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
       # ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))


    elements.append(header_table)
    elements.append(Spacer(1, 12))  # Add space below the header

    # Update the Song Content Section
    lyrics_with_chords = song.lyrics_with_chords or []
    content_table_data = []  # Table data for the Song Content

    # Custom centered style for lines following {soc}
    centered_lyric_style = ParagraphStyle(
        name="CenteredLyricStyle",
        parent=styles['BodyText'],  # Base style
        alignment=1,  # Center align
        leading=14,
        fontSize=12,
        spaceAfter=6,
    )

    paragraph_buffer = []  # Collect lines for the current paragraph
    is_soc_active = False  # Track whether we are in a {soc} section

    for group in lyrics_with_chords:
        for item in group:
            if "directive" in item:
                if item["directive"] == "{soc}":
                    # Mark that we are in a Start of Chorus section
                    is_soc_active = True
                    continue
                elif item["directive"] == "{eoc}":
                    # End of Chorus; reset the SOC state
                    is_soc_active = False
                    continue
                # Skip other directives
                continue
            elif "format" in item:
                if item["format"] == "LINEBREAK":
                    # Add a spacer within the current paragraph
                    paragraph_buffer.append("<br/>")
                elif item["format"] == "PARAGRAPHBREAK":
                    # Flush the current paragraph as a new table row
                    if paragraph_buffer:
                        paragraph_text = " ".join(paragraph_buffer)
                        if is_soc_active:
                            # Center rows for the chorus
                            content_table_data.append([Paragraph(paragraph_text, centered_lyric_style)])
                        else:
                            content_table_data.append([Paragraph(paragraph_text, lyric_style)])
                        paragraph_buffer = []  # Clear the buffer
            elif "lyric" in item:
                chord = item.get("chord", "")
                lyric = item["lyric"]
                if chord:
                    paragraph_buffer.append(f"<b>[{chord}]</b> {lyric}")
                else:
                    paragraph_buffer.append(lyric)

        # Flush the paragraph at the end of each group
        if paragraph_buffer:
            paragraph_text = " ".join(paragraph_buffer)
            if is_soc_active:
                # Center rows for the chorus
                content_table_data.append([Paragraph(paragraph_text, centered_lyric_style)])
            else:
                content_table_data.append([Paragraph(paragraph_text, lyric_style)])
            paragraph_buffer = []

    # Create the Song Content table
    content_table = Table(content_table_data, colWidths=[500])  # Single column for content
    content_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(content_table)




    # Build the document
    doc.build(elements)
