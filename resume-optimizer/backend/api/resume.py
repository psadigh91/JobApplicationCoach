"""
Resume API endpoints - Generate and manage resume versions
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import (
    get_db, ResumeVersion, Session as SessionModel,
    Upload, Analysis
)
from core.resume_generator import ResumeGenerator

router = APIRouter()


class GenerateRequest(BaseModel):
    """Resume generation request"""
    session_id: str


class ResumeResponse(BaseModel):
    """Resume version response"""
    version_id: int
    session_id: str
    version_type: str
    content: dict
    generation_status: str
    approved: bool


class UpdateRequest(BaseModel):
    """Update resume content"""
    content: dict


async def generate_resumes_background(session_id: str, db: DBSession):
    """Background task to generate both resume versions"""
    try:
        # Get data
        resume_upload = db.query(Upload).filter(
            Upload.session_id == session_id,
            Upload.upload_type == "resume"
        ).first()

        job_upload = db.query(Upload).filter(
            Upload.session_id == session_id,
            Upload.upload_type == "job_posting"
        ).first()

        analysis = db.query(Analysis).filter(
            Analysis.session_id == session_id
        ).first()

        if not resume_upload or not job_upload or not analysis:
            raise ValueError("Missing required data")

        resume_data = resume_upload.structured_data or {}
        job_data = job_upload.structured_data or {}
        improvements = analysis.tactical_improvements or []

        # Generate tactical version
        generator = ResumeGenerator()
        tactical_result = await generator.generate_tactical_version(
            resume_data,
            improvements,
            job_data
        )

        # Save tactical version
        tactical_version = db.query(ResumeVersion).filter(
            ResumeVersion.session_id == session_id,
            ResumeVersion.version_type == "tactical"
        ).first()

        if not tactical_version:
            tactical_version = ResumeVersion(
                session_id=session_id,
                version_type="tactical"
            )
            db.add(tactical_version)

        tactical_version.content = tactical_result
        tactical_version.modifications = tactical_result.get('modifications', [])
        tactical_version.generation_status = "completed"
        db.commit()
        db.refresh(tactical_version)

        # Generate extrapolated version
        extrapolated_result = await generator.generate_extrapolated_version(
            resume_data,
            tactical_result,
            analysis.__dict__,
            job_data
        )

        # Save extrapolated version
        extrapolated_version = db.query(ResumeVersion).filter(
            ResumeVersion.session_id == session_id,
            ResumeVersion.version_type == "extrapolated"
        ).first()

        if not extrapolated_version:
            extrapolated_version = ResumeVersion(
                session_id=session_id,
                version_type="extrapolated"
            )
            db.add(extrapolated_version)

        extrapolated_version.content = extrapolated_result
        extrapolated_version.modifications = extrapolated_result.get('modifications', [])
        extrapolated_version.generation_status = "completed"
        db.commit()

    except Exception as e:
        # Mark as failed
        for version_type in ["tactical", "extrapolated"]:
            version = db.query(ResumeVersion).filter(
                ResumeVersion.session_id == session_id,
                ResumeVersion.version_type == version_type
            ).first()

            if version:
                version.generation_status = "failed"
                version.generation_error = str(e)
        db.commit()


@router.post("/generate", response_model=dict)
async def generate_resume_versions(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """
    Generate both tactical and extrapolated resume versions

    Runs in background. Use GET /{version_id} to check status.
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create placeholder records
    for version_type in ["tactical", "extrapolated"]:
        existing = db.query(ResumeVersion).filter(
            ResumeVersion.session_id == request.session_id,
            ResumeVersion.version_type == version_type
        ).first()

        if not existing:
            version = ResumeVersion(
                session_id=request.session_id,
                version_type=version_type,
                generation_status="processing"
            )
            db.add(version)

    db.commit()

    # Start generation
    background_tasks.add_task(generate_resumes_background, request.session_id, db)

    return {
        "status": "generation_started",
        "session_id": request.session_id,
        "message": "Both resume versions are being generated"
    }


@router.get("/{version_id}", response_model=ResumeResponse)
async def get_resume_version(version_id: int, db: DBSession = Depends(get_db)):
    """Get a specific resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    return ResumeResponse(
        version_id=version.id,
        session_id=version.session_id,
        version_type=version.version_type,
        content=version.content or {},
        generation_status=version.generation_status,
        approved=version.approved
    )


@router.get("/session/{session_id}")
async def get_session_resumes(session_id: str, db: DBSession = Depends(get_db)):
    """Get all resume versions for a session"""
    versions = db.query(ResumeVersion).filter(
        ResumeVersion.session_id == session_id
    ).all()

    return {
        "session_id": session_id,
        "versions": [
            {
                "version_id": v.id,
                "version_type": v.version_type,
                "generation_status": v.generation_status,
                "approved": v.approved,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in versions
        ]
    }


@router.put("/{version_id}", response_model=ResumeResponse)
async def update_resume_version(
    version_id: int,
    request: UpdateRequest,
    db: DBSession = Depends(get_db)
):
    """Update resume content (user edits)"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    version.content = request.content
    db.commit()
    db.refresh(version)

    return ResumeResponse(
        version_id=version.id,
        session_id=version.session_id,
        version_type=version.version_type,
        content=version.content or {},
        generation_status=version.generation_status,
        approved=version.approved
    )


@router.get("/{version_id}/diff")
async def get_resume_diff(version_id: int, db: DBSession = Depends(get_db)):
    """Get modifications/diff for a resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    return {
        "version_id": version.id,
        "version_type": version.version_type,
        "modifications": version.modifications or []
    }


@router.post("/{version_id}/approve")
async def approve_resume_version(version_id: int, db: DBSession = Depends(get_db)):
    """Approve a resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    version.approved = True
    version.approved_at = datetime.utcnow()
    db.commit()

    return {
        "status": "approved",
        "version_id": version.id,
        "version_type": version.version_type
    }


@router.delete("/{version_id}")
async def delete_resume_version(version_id: int, db: DBSession = Depends(get_db)):
    """Delete a resume version"""
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found")

    db.delete(version)
    db.commit()

    return {"status": "deleted", "version_id": version_id}
