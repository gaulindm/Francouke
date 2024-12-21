def generate_song_pdf(response, song):
    """
    Generate a PDF for a song, ensuring that chord-lyric pairs are displayed on the same line.
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    directive_style = ParagraphStyle(
        name="DirectiveStyle",
        parent=styles['Italic'],
        leading=2,
        spaceAfter=2,
        textColor=colors.grey,
    )
    lyric_style = ParagraphStyle(
        name="LyricStyle",
        parent=styles['BodyText'],
        leading=4,
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

    # --- Song Header ---
    metadata = song.metadata or {}  # Handle case where metadata is None
    header_data = [
        [
            Paragraph(f"Time Signature: {metadata.get('timeSignature', 'Unknown')}", styles['Normal']),
            Paragraph(f"<b>{song.songTitle or 'Untitled Song'}</b>", styles['Heading1']),
            Paragraph(f"First Note: {metadata.get('1stnote', 'N/A')}", styles['Normal']),
        ],
        [
            Paragraph(f"Tempo: {metadata.get('tempo', 'Unknown')}", styles['Normal']),
            Paragraph(f"Composer: {metadata.get('composer', 'Unknown')}<br/>Lyricist: {metadata.get('lyricist', 'Unknown')}", styles['Normal']),
            "",
        ],
        [
            Paragraph(f"As recorded by {metadata.get('artist', 'Unknown Artist')} in {metadata.get('year', 'Unknown')}", styles['Italic']),
            "",
            "",
        ],
    ]
    header_table = Table(header_data, colWidths=[150, 300, 150])
    header_table.setStyle(TableStyle([
        ('SPAN', (0, 2), (-1, 2)),  # Merge the last row
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))  # Add space below the header

    # --- Song Content ---
    lyrics_with_chords = song.lyrics_with_chords or []  # Handle case where lyrics_with_chords is None
    for group in lyrics_with_chords:
        line_buffer = []  # Temporary buffer for chord-lyric pairs in the same line
        for item in group:
            if "directive" in item:
                # Skip directives in the song content
                continue
            elif "lyric" in item:
                # Add chord-lyric pair to the line buffer
                chord = item.get("chord", "")
                lyric = item["lyric"]
                if chord:
                    line_buffer.append(f"<b>[{chord}]</b> {lyric}")
                else:
                    line_buffer.append(lyric)
            elif "format" in item:
                if item["format"] == "LINEBREAK":
                    # Add the current line as a single paragraph
                    if line_buffer:
                        elements.append(Paragraph(" ".join(line_buffer), lyric_style))
                        line_buffer = []  # Clear the buffer for the next line
                elif item["format"] == "PARAGRAPHBREAK":
                    # Add the current line and create a paragraph break
                    if line_buffer:
                        elements.append(Paragraph(" ".join(line_buffer), lyric_style))
                        line_buffer = []
                    elements.append(Spacer(1, 12))  # Add a larger paragraph break

        # Add any remaining content in the line buffer
        if line_buffer:
            elements.append(Paragraph(" ".join(line_buffer), lyric_style))

    # Build the document
    doc.build(elements)
