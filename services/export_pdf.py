import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def markdown_to_pdf_bytes(markdown_text: str) -> bytes:
    """Converts a Markdown resume string into a styled PDF byte buffer using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom ATS-friendly styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    heading_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4,
        textTransform='uppercase'
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    story = []
    lines = markdown_text.split('\n')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Convert markdown bold/italics syntax to ReportLab inline XML tags
        formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
        formatted_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_line)

        # H1 (# Title)
        if stripped.startswith('# '):
            text = formatted_line[2:].strip()
            story.append(Paragraph(text, title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceBefore=2, spaceAfter=8))

        # H2 (## Section Header)
        elif stripped.startswith('## '):
            text = formatted_line[3:].strip()
            story.append(Spacer(1, 4))
            story.append(Paragraph(text, heading_style))
            story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=6))

        # H3 (### Sub-header)
        elif stripped.startswith('### '):
            text = formatted_line[4:].strip()
            style_h3 = ParagraphStyle('H3', parent=body_style, fontName='Helvetica-Bold', fontSize=11, spaceBefore=4, spaceAfter=2)
            story.append(Paragraph(text, style_h3))

        # Bullet points (* or - or •)
        elif stripped.startswith(('* ', '- ', '• ')):
            text = formatted_line[2:].strip()
            story.append(Paragraph(f"• {text}", bullet_style))

        # Standard Paragraph Text
        else:
            story.append(Paragraph(formatted_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()