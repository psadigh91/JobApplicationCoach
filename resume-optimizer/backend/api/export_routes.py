"""
Export API endpoints - Export resumes and reports to PDF/HTML
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional
import os
import io
from datetime import datetime

from core.database import get_db, ResumeVersion, Analysis, StudyResource
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from jinja2 import Template

router = APIRouter()

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


class ExportRequest(BaseModel):
    """Export request"""
    session_id: str
    version_id: Optional[int] = None
    include_analysis: bool = False
    include_study_guide: bool = False


def generate_resume_pdf(version_id: int, db: DBSession) -> str:
    """Generate PDF for resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise ValueError("Resume version not found")

    content = version.content.get('sections', {})

    # Create PDF
    filename = f"resume_{version.version_type}_{version_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Contact info
    if content.get('contact'):
        contact = content['contact']
        story.append(Paragraph(f"<b>{contact.get('name', 'Name')}</b>", styles['Title']))
        story.append(Paragraph(
            f"{contact.get('email', '')} | {contact.get('phone', '')} | {contact.get('location', '')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 12))

    # Summary
    if content.get('summary'):
        story.append(Paragraph("<b>Professional Summary</b>", styles['Heading2']))
        story.append(Paragraph(content['summary'], styles['Normal']))
        story.append(Spacer(1, 12))

    # Experience
    if content.get('experience'):
        story.append(Paragraph("<b>Experience</b>", styles['Heading2']))
        for exp in content['experience']:
            story.append(Paragraph(
                f"<b>{exp.get('title', '')}</b> at {exp.get('company', '')}",
                styles['Heading3']
            ))
            story.append(Paragraph(exp.get('dates', ''), styles['Normal']))
            for bullet in exp.get('bullets', []):
                story.append(Paragraph(f"• {bullet}", styles['Normal']))
            story.append(Spacer(1, 6))

    # Skills
    if content.get('skills'):
        story.append(Paragraph("<b>Skills</b>", styles['Heading2']))
        story.append(Paragraph(', '.join(content['skills']), styles['Normal']))
        story.append(Spacer(1, 12))

    # Education
    if content.get('education'):
        story.append(Paragraph("<b>Education</b>", styles['Heading2']))
        for edu in content['education']:
            story.append(Paragraph(
                f"<b>{edu.get('degree', '')}</b> from {edu.get('school', '')}",
                styles['Normal']
            ))
            story.append(Paragraph(edu.get('dates', ''), styles['Normal']))
            story.append(Spacer(1, 6))

    # Build PDF
    doc.build(story)

    return filepath


def generate_html_resume(version_id: int, db: DBSession) -> str:
    """Generate HTML for resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise ValueError("Resume version not found")

    content = version.content.get('sections', {})

    # Simple HTML template
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume - {{ name }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        h2 { color: #555; border-bottom: 2px solid #333; padding-bottom: 5px; }
        .contact { color: #666; margin-bottom: 20px; }
        .job { margin-bottom: 15px; }
        .job-title { font-weight: bold; }
        ul { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>{{ name }}</h1>
    <div class="contact">{{ email }} | {{ phone }} | {{ location }}</div>

    {% if summary %}
    <h2>Professional Summary</h2>
    <p>{{ summary }}</p>
    {% endif %}

    {% if experience %}
    <h2>Experience</h2>
    {% for exp in experience %}
    <div class="job">
        <div class="job-title">{{ exp.title }} at {{ exp.company }}</div>
        <div>{{ exp.dates }}</div>
        <ul>
        {% for bullet in exp.bullets %}
            <li>{{ bullet }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endfor %}
    {% endif %}

    {% if skills %}
    <h2>Skills</h2>
    <p>{{ skills|join(', ') }}</p>
    {% endif %}

    {% if education %}
    <h2>Education</h2>
    {% for edu in education %}
    <div>
        <strong>{{ edu.degree }}</strong> from {{ edu.school }} ({{ edu.dates }})
    </div>
    {% endfor %}
    {% endif %}
</body>
</html>
"""

    template = Template(html_template)
    contact = content.get('contact', {})

    html = template.render(
        name=contact.get('name', 'Name'),
        email=contact.get('email', ''),
        phone=contact.get('phone', ''),
        location=contact.get('location', ''),
        summary=content.get('summary'),
        experience=content.get('experience', []),
        skills=content.get('skills', []),
        education=content.get('education', [])
    )

    # Save HTML
    filename = f"resume_{version.version_type}_{version_id}_{datetime.now().strftime('%Y%m%d')}.html"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, 'w') as f:
        f.write(html)

    return filepath


@router.post("/pdf")
async def export_to_pdf(request: ExportRequest, db: DBSession = Depends(get_db)):
    """Export resume to PDF"""
    if not request.version_id:
        raise HTTPException(status_code=400, detail="version_id required for PDF export")

    try:
        filepath = generate_resume_pdf(request.version_id, db)

        return {
            "status": "success",
            "format": "pdf",
            "filename": os.path.basename(filepath),
            "download_url": f"/api/export/download/{os.path.basename(filepath)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/html")
async def export_to_html(request: ExportRequest, db: DBSession = Depends(get_db)):
    """Export resume to HTML"""
    if not request.version_id:
        raise HTTPException(status_code=400, detail="version_id required for HTML export")

    try:
        filepath = generate_html_resume(request.version_id, db)

        return {
            "status": "success",
            "format": "html",
            "filename": os.path.basename(filepath),
            "download_url": f"/api/export/download/{os.path.basename(filepath)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML generation failed: {str(e)}")


@router.get("/download/{filename}")
async def download_export(filename: str):
    """Download exported file"""
    filepath = os.path.join(EXPORT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        filepath,
        media_type="application/octet-stream",
        filename=filename
    )


@router.get("/list/{session_id}")
async def list_exports(session_id: str):
    """List all exports for a session"""
    # List files matching session pattern
    files = [
        f for f in os.listdir(EXPORT_DIR)
        if session_id in f
    ]

    return {
        "session_id": session_id,
        "exports": [
            {
                "filename": f,
                "download_url": f"/api/export/download/{f}",
                "created": datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(EXPORT_DIR, f))
                ).isoformat()
            }
            for f in files
        ]
    }
