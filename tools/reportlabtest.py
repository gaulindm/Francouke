from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Define styles
styles = {
    "left": ParagraphStyle(name="LeftAlign", alignment=TA_LEFT, fontSize=12, leading=14),
    "center": ParagraphStyle(name="CenterAlign", alignment=TA_CENTER, fontSize=12, leading=14),
    "title": ParagraphStyle(name="Title", alignment=TA_CENTER, fontSize=16, leading=20, spaceAfter=20),
}

# Song content sections
chorus_lines = [
    "(A) Go-in’ up to the Spir-it in the sky.",
    "(D) That’s where I’m gon-na go when I (D//)die.",
    "(D) When I die and they (A)lay me to rest,",
    "(E7) I’m gon-na go to the place that’s the best.  (A//)",
]

song_content = [
    ("Intro", "(A)  (A// - D/ - C/)  x8"),
    ("Chorus", chorus_lines),
    (
        "Verse 1",
        [
            "(A) When I die and they lay me to (A//)rest,",
            "(A) gon-na go to the (D)place that’s the (D//)best.",
            "(D) When I lay me (A)down to die,",
            "(A) go-in’ (E7)up to the spir-it in the (A//)sky.",
        ],
    ),
    ("Chorus", chorus_lines),
    (
        "Verse 2",
        [
            "(A) Pre-pare your-(A//)self; you know it’s a must.",
            "Got-ta have a friend in (D)Je-(D///)sus,",
            "(D) so you know that (A)when you die,  (A//)",
            "(E7) He’s gon-na re-com-mend you to the spir-it in the (A//)sky.",
        ],
    ),
    ("Chorus", chorus_lines),
]

# Function to create a two-column table for the chorus
def create_chorus_table(chorus_lines):
    # First row combines "Chorus:" and the first line of lyrics
    table_data = [[Paragraph("Chorus:", styles["left"]), Paragraph(chorus_lines[0], styles["center"])]]
    
    # Add each subsequent chorus line in the second column
    for line in chorus_lines[1:]:
        table_data.append(["", Paragraph(line, styles["center"])])
    
    # Create a table with appropriate column widths
    table = Table(
        table_data,
        colWidths=[70, 430],  # 70 for "Chorus:", 430 for the lyrics
    )
    table.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to the top
            ('LEFTPADDING', (0, 0), (0, 0), 5),   # Padding for "Chorus:"
            ('RIGHTPADDING', (1, 0), (1, 0), 5),  # Padding for lyrics
        ])
    )
    return table

# Generate the PDF
def create_song_sheet(filename):
    content = []
    
    # Add title
    content.append(Paragraph("Spirit In The Sky", styles["title"]))
    content.append(Spacer(1, 10))
    
    # Add sections
    for section_title, section_content in song_content:
        if section_title.lower() == "chorus":
            # Create a two-column table for the chorus
            content.append(create_chorus_table(section_content))
        else:
            # Section heading
            content.append(Paragraph(section_title + ":", styles["left"]))
            content.append(Spacer(1, 10))
            
            # Add section content
            if isinstance(section_content, list):
                for line in section_content:
                    content.append(Paragraph(line, styles["left"]))
                    content.append(Spacer(1, 5))
            else:
                content.append(Paragraph(section_content, styles["left"]))
                content.append(Spacer(1, 10))
    
    # Generate PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    doc.build(content)

# Create the PDF
create_song_sheet("Spirit_In_The_Sky_Final.pdf")