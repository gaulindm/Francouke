from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def test_pdf():
    doc = SimpleDocTemplate("test_output.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("This is a test PDF.", styles["BodyText"])]
    doc.build(story)

test_pdf()
