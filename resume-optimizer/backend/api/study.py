"""
Study Guide API endpoints - Generate personalized learning resources
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import List, Optional

from core.database import (
    get_db, StudyResource, Session as SessionModel,
    Analysis, Upload
)
from core.study_guide_builder import StudyGuideBuilder

router = APIRouter()


class GenerateStudyGuideRequest(BaseModel):
    """Study guide generation request"""
    session_id: str
    timeline: str = "3 months"


class ResourceRequest(BaseModel):
    """Find resources for specific skill"""
    skill: str
    resource_types: List[str] = ["video", "course", "documentation"]


class ProjectRequest(BaseModel):
    """Get project suggestions"""
    target_skills: List[str]
    difficulty: str = "intermediate"


class StudyGuideResponse(BaseModel):
    """Study guide response"""
    session_id: str
    guide_data: dict
    generation_status: str


async def generate_study_guide_background(
    session_id: str,
    timeline: str,
    db: DBSession
):
    """Background task to generate study guide"""
    try:
        # Get analysis data
        analysis = db.query(Analysis).filter(
            Analysis.session_id == session_id
        ).first()

        resume_upload = db.query(Upload).filter(
            Upload.session_id == session_id,
            Upload.upload_type == "resume"
        ).first()

        if not analysis or not resume_upload:
            raise ValueError("Missing analysis or resume data")

        # Prepare data
        gaps = analysis.gaps or []
        candidate_background = {
            "skills": resume_upload.structured_data.get('sections', {}).get('skills', []),
            "experience": resume_upload.structured_data.get('sections', {}).get('experience', []),
            "learning_speed": analysis.growth_data.get('learning_speed', 'unknown')
        }

        # Generate study guide
        builder = StudyGuideBuilder()
        guide_data = await builder.generate_study_guide(
            gaps,
            candidate_background,
            timeline
        )

        # Save to database
        # Create study resource records for each skill
        for skill_guide in guide_data.get('skills', []):
            existing = db.query(StudyResource).filter(
                StudyResource.session_id == session_id,
                StudyResource.skill_name == skill_guide['skill']
            ).first()

            if existing:
                resource = existing
            else:
                resource = StudyResource(
                    session_id=session_id,
                    skill_name=skill_guide['skill']
                )
                db.add(resource)

            resource.resource_type = "study_guide"
            resource.resource_data = skill_guide
            resource.priority = skill_guide.get('priority', 'medium')

        db.commit()

    except Exception as e:
        print(f"Error generating study guide: {e}")


@router.post("/generate", response_model=dict)
async def generate_study_guide(
    request: GenerateStudyGuideRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """
    Generate personalized study guide

    Analyzes skill gaps and creates learning path with resources.
    Runs in background.
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Start generation
    background_tasks.add_task(
        generate_study_guide_background,
        request.session_id,
        request.timeline,
        db
    )

    return {
        "status": "generation_started",
        "session_id": request.session_id,
        "timeline": request.timeline
    }


@router.get("/{session_id}", response_model=dict)
async def get_study_guide(session_id: str, db: DBSession = Depends(get_db)):
    """Get generated study guide"""
    resources = db.query(StudyResource).filter(
        StudyResource.session_id == session_id
    ).all()

    if not resources:
        raise HTTPException(status_code=404, detail="Study guide not found")

    return {
        "session_id": session_id,
        "skills": [
            {
                "skill": r.skill_name,
                "priority": r.priority,
                "guide": r.resource_data
            }
            for r in resources
        ]
    }


@router.post("/resources")
async def find_resources(request: ResourceRequest):
    """Find resources for a specific skill"""
    builder = StudyGuideBuilder()
    resources = await builder.find_resources(
        request.skill,
        request.resource_types
    )

    return {
        "skill": request.skill,
        "resources": resources
    }


@router.post("/projects")
async def suggest_projects(request: ProjectRequest):
    """Get project suggestions"""
    builder = StudyGuideBuilder()
    projects = builder.suggest_projects(
        request.target_skills,
        request.difficulty
    )

    return {
        "target_skills": request.target_skills,
        "difficulty": request.difficulty,
        "projects": projects
    }


@router.delete("/{session_id}")
async def delete_study_guide(session_id: str, db: DBSession = Depends(get_db)):
    """Delete study guide"""
    resources = db.query(StudyResource).filter(
        StudyResource.session_id == session_id
    ).all()

    for resource in resources:
        db.delete(resource)

    db.commit()

    return {"status": "deleted", "session_id": session_id}
