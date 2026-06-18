"""
LinkedIn API endpoints - Handle LinkedIn profile scraping and PDF uploads
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os

from core.database import get_db, LinkedInData, Session as SessionModel
from core.extractors.linkedin_scraper import LinkedInScraper

router = APIRouter()

UPLOAD_DIR = "uploads"


class LinkedInScrapeRequest(BaseModel):
    """Request to scrape LinkedIn URL"""
    session_id: str
    linkedin_url: str


class LinkedInResponse(BaseModel):
    """LinkedIn data response"""
    session_id: str
    source_type: str
    scraping_status: str
    profile_data: Optional[dict] = None
    error: Optional[str] = None


@router.post("/scrape", response_model=LinkedInResponse)
async def scrape_linkedin_profile(
    request: LinkedInScrapeRequest,
    db: DBSession = Depends(get_db)
):
    """
    Scrape LinkedIn profile from URL

    Args:
        request: Scrape request with session_id and URL
        db: Database session

    Note: LinkedIn scraping often fails due to authentication requirements.
    Falls back to PDF upload if scraping fails.
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if LinkedIn data already exists
    existing = db.query(LinkedInData).filter(
        LinkedInData.session_id == request.session_id
    ).first()

    if existing:
        # Update existing record
        linkedin_data = existing
    else:
        # Create new record
        linkedin_data = LinkedInData(
            session_id=request.session_id,
            source_type="url_scrape",
            linkedin_url=request.linkedin_url,
            scraping_status="processing"
        )
        db.add(linkedin_data)
        db.commit()
        db.refresh(linkedin_data)

    # Attempt to scrape
    try:
        scraper = LinkedInScraper()
        profile_data = await scraper.scrape_profile(request.linkedin_url)

        if profile_data.get("success"):
            linkedin_data.profile_data = profile_data
            linkedin_data.scraping_status = "success"
            linkedin_data.scraping_error = None
        else:
            # Scraping failed
            linkedin_data.scraping_status = "fallback_to_pdf"
            linkedin_data.scraping_error = profile_data.get("error", "Unknown error")
            linkedin_data.profile_data = {
                "fallback_message": profile_data.get("fallback_message")
            }

        db.commit()
        db.refresh(linkedin_data)

    except Exception as e:
        linkedin_data.scraping_status = "failed"
        linkedin_data.scraping_error = str(e)
        db.commit()

    return LinkedInResponse(
        session_id=linkedin_data.session_id,
        source_type=linkedin_data.source_type,
        scraping_status=linkedin_data.scraping_status,
        profile_data=linkedin_data.profile_data,
        error=linkedin_data.scraping_error
    )


@router.post("/pdf", response_model=LinkedInResponse)
async def upload_linkedin_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    """
    Upload LinkedIn profile PDF export

    Args:
        session_id: Session ID
        file: LinkedIn PDF export
        db: Database session
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Must be a PDF file")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_linkedin.pdf")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Check if record exists
    existing = db.query(LinkedInData).filter(
        LinkedInData.session_id == session_id
    ).first()

    if existing:
        linkedin_data = existing
        linkedin_data.source_type = "pdf_upload"
    else:
        linkedin_data = LinkedInData(
            session_id=session_id,
            source_type="pdf_upload"
        )
        db.add(linkedin_data)

    # Parse PDF
    try:
        scraper = LinkedInScraper()
        profile_data = scraper.parse_pdf_export(file_path)

        linkedin_data.profile_data = profile_data
        linkedin_data.scraping_status = "success" if profile_data.get("success") else "failed"

        if not profile_data.get("success"):
            linkedin_data.scraping_error = profile_data.get("error")

        db.commit()
        db.refresh(linkedin_data)

    except Exception as e:
        linkedin_data.scraping_status = "failed"
        linkedin_data.scraping_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to parse LinkedIn PDF: {str(e)}")

    return LinkedInResponse(
        session_id=linkedin_data.session_id,
        source_type=linkedin_data.source_type,
        scraping_status=linkedin_data.scraping_status,
        profile_data=linkedin_data.profile_data,
        error=linkedin_data.scraping_error
    )


@router.get("/{session_id}", response_model=LinkedInResponse)
async def get_linkedin_data(session_id: str, db: DBSession = Depends(get_db)):
    """Get LinkedIn data for a session"""
    linkedin_data = db.query(LinkedInData).filter(
        LinkedInData.session_id == session_id
    ).first()

    if not linkedin_data:
        raise HTTPException(status_code=404, detail="LinkedIn data not found")

    return LinkedInResponse(
        session_id=linkedin_data.session_id,
        source_type=linkedin_data.source_type,
        scraping_status=linkedin_data.scraping_status,
        profile_data=linkedin_data.profile_data,
        error=linkedin_data.scraping_error
    )


@router.delete("/{session_id}")
async def delete_linkedin_data(session_id: str, db: DBSession = Depends(get_db)):
    """Delete LinkedIn data for a session"""
    linkedin_data = db.query(LinkedInData).filter(
        LinkedInData.session_id == session_id
    ).first()

    if not linkedin_data:
        raise HTTPException(status_code=404, detail="LinkedIn data not found")

    db.delete(linkedin_data)
    db.commit()

    return {"status": "deleted", "session_id": session_id}


@router.get("/{session_id}/instructions")
async def get_pdf_instructions():
    """Get instructions for exporting LinkedIn profile as PDF"""
    instructions = {
        "title": "How to Export Your LinkedIn Profile as a PDF",
        "steps": [
            "1. Go to your LinkedIn profile page",
            "2. Click 'More' in your profile section",
            "3. Select 'Save to PDF'",
            "4. Your profile will download as a PDF",
            "5. Upload that PDF file here"
        ],
        "tips": [
            "Make sure your profile is up to date before exporting",
            "The PDF export includes all public sections of your profile",
            "This is the most reliable way to import LinkedIn data"
        ],
        "alternative": "If scraping fails, we'll automatically prompt you to use the PDF method"
    }
    return instructions
