"""
Upload API endpoints - Handle resume, cover letter, and job posting uploads
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from datetime import datetime

from core.database import get_db, Upload, Session as SessionModel
from core.extractors.resume_parser import ResumeParser
from core.extractors.job_posting_parser import JobPostingParser

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_RESUME_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
ALLOWED_TEXT_TYPES = ["text/plain"]


class UploadResponse(BaseModel):
    """Upload response model"""
    upload_id: int
    file_name: str
    upload_type: str
    processing_status: str
    structured_data: Optional[dict] = None


@router.post("/resume", response_model=UploadResponse)
async def upload_resume(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    """
    Upload and parse resume (PDF or DOCX)

    Args:
        session_id: Session ID
        file: Resume file
        db: Database session
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    if file.content_type not in ALLOWED_RESUME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_RESUME_TYPES)}"
        )

    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_resume_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Create upload record
    upload = Upload(
        session_id=session_id,
        upload_type="resume",
        file_name=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        processing_status="processing"
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    # Parse resume
    try:
        parser = ResumeParser()
        parsed_data = parser.parse(file_path, file.content_type)

        # Update upload with parsed data
        upload.raw_text = parsed_data.get("raw_text", "")
        upload.structured_data = parsed_data
        upload.processing_status = "completed"
        db.commit()
        db.refresh(upload)

    except Exception as e:
        upload.processing_status = "failed"
        upload.processing_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    return UploadResponse(
        upload_id=upload.id,
        file_name=upload.file_name,
        upload_type=upload.upload_type,
        processing_status=upload.processing_status,
        structured_data=upload.structured_data
    )


@router.post("/cover-letter", response_model=UploadResponse)
async def upload_cover_letter(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db)
):
    """Upload cover letter (PDF, DOCX, or TXT)"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Allow text files for cover letters
    allowed_types = ALLOWED_RESUME_TYPES + ALLOWED_TEXT_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_cover_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(content)

    # Create upload record
    upload = Upload(
        session_id=session_id,
        upload_type="cover_letter",
        file_name=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        processing_status="completed"
    )

    # Extract text based on type
    try:
        if file.content_type == "text/plain":
            upload.raw_text = content.decode('utf-8')
        else:
            parser = ResumeParser()
            parsed = parser.parse(file_path, file.content_type)
            upload.raw_text = parsed.get("raw_text", "")

        db.add(upload)
        db.commit()
        db.refresh(upload)

    except Exception as e:
        upload.processing_status = "failed"
        upload.processing_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process cover letter: {str(e)}")

    return UploadResponse(
        upload_id=upload.id,
        file_name=upload.file_name,
        upload_type=upload.upload_type,
        processing_status=upload.processing_status,
        structured_data={"raw_text": upload.raw_text}
    )


@router.post("/job-posting", response_model=UploadResponse)
async def upload_job_posting(
    session_id: str = Form(...),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: DBSession = Depends(get_db)
):
    """
    Upload job posting (pasted text or file)

    Args:
        session_id: Session ID
        text: Pasted job posting text
        file: Job posting file (optional)
        db: Database session
    """
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not text and not file:
        raise HTTPException(status_code=400, detail="Must provide either text or file")

    job_text = ""
    file_path = None
    file_name = "pasted_text.txt"

    # Handle file upload
    if file:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Save file
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, f"{session_id}_job_{file.filename}")
        file_name = file.filename

        with open(file_path, "wb") as f:
            f.write(content)

        # Extract text
        if file.content_type == "text/plain":
            job_text = content.decode('utf-8')
        else:
            parser = ResumeParser()
            parsed = parser.parse(file_path, file.content_type)
            job_text = parsed.get("raw_text", "")
    else:
        # Handle pasted text
        job_text = text

    # Parse job posting
    try:
        parser = JobPostingParser()
        parsed_job = parser.parse(job_text, source='paste' if not file else 'file')

        # Create upload record
        upload = Upload(
            session_id=session_id,
            upload_type="job_posting",
            file_name=file_name,
            file_path=file_path,
            file_size=len(job_text.encode('utf-8')),
            mime_type="text/plain",
            raw_text=job_text,
            structured_data=parsed_job,
            processing_status="completed"
        )

        db.add(upload)
        db.commit()
        db.refresh(upload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse job posting: {str(e)}")

    return UploadResponse(
        upload_id=upload.id,
        file_name=upload.file_name,
        upload_type=upload.upload_type,
        processing_status=upload.processing_status,
        structured_data=upload.structured_data
    )


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(upload_id: int, db: DBSession = Depends(get_db)):
    """Get upload details by ID"""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    return UploadResponse(
        upload_id=upload.id,
        file_name=upload.file_name,
        upload_type=upload.upload_type,
        processing_status=upload.processing_status,
        structured_data=upload.structured_data
    )


@router.delete("/{upload_id}")
async def delete_upload(upload_id: int, db: DBSession = Depends(get_db)):
    """Delete an upload and its file"""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Delete file if exists
    if upload.file_path and os.path.exists(upload.file_path):
        try:
            os.remove(upload.file_path)
        except Exception as e:
            print(f"Failed to delete file: {e}")

    # Delete database record
    db.delete(upload)
    db.commit()

    return {"status": "deleted", "upload_id": upload_id}


@router.get("/session/{session_id}")
async def get_session_uploads(session_id: str, db: DBSession = Depends(get_db)):
    """Get all uploads for a session"""
    uploads = db.query(Upload).filter(Upload.session_id == session_id).all()

    return {
        "session_id": session_id,
        "uploads": [
            {
                "upload_id": u.id,
                "upload_type": u.upload_type,
                "file_name": u.file_name,
                "processing_status": u.processing_status,
                "uploaded_at": u.uploaded_at.isoformat()
            }
            for u in uploads
        ]
    }
