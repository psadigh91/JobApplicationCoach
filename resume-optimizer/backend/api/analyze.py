"""
Analysis API endpoints - Orchestrate AI-powered analysis
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import (
    get_db, Analysis, Session as SessionModel, Upload,
    LinkedInData, CompanyResearch, QAResponse, Citation
)
from core.analyzer import Analyzer
from core.confidence_scorer import ConfidenceScorer
from core.skill_taxonomy import SkillTaxonomy

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Analysis request"""
    session_id: str


class ScorecardResponse(BaseModel):
    """Scorecard response"""
    session_id: str
    overall_score: int
    exact_match: dict
    transferable_match: dict
    growth_potential: dict
    culture_fit: dict
    recommendation: str
    analysis_status: str


class GapMatch(BaseModel):
    """Gap or match item"""
    skill: str
    evidence: Optional[str] = None
    confidence: int
    impact: Optional[str] = None


async def run_analysis_background(session_id: str, db: DBSession):
    """Background task to run full analysis"""
    try:
        # Get all data sources
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return

        # Get resume
        resume_upload = db.query(Upload).filter(
            Upload.session_id == session_id,
            Upload.upload_type == "resume"
        ).first()

        # Get job posting
        job_upload = db.query(Upload).filter(
            Upload.session_id == session_id,
            Upload.upload_type == "job_posting"
        ).first()

        # Get LinkedIn data
        linkedin = db.query(LinkedInData).filter(
            LinkedInData.session_id == session_id
        ).first()

        # Get company data
        company = db.query(CompanyResearch).filter(
            CompanyResearch.session_id == session_id
        ).first()

        # Get Q&A responses
        qa_responses = db.query(QAResponse).filter(
            QAResponse.session_id == session_id
        ).all()

        if not resume_upload or not job_upload:
            raise ValueError("Missing required data (resume or job posting)")

        # Prepare data for analysis
        resume_data = resume_upload.structured_data or {}
        job_data = job_upload.structured_data or {}
        linkedin_data = linkedin.profile_data if linkedin else {}
        company_data = company.pages_crawled if company else []
        qa_data = [{"question": qa.question, "answer": qa.answer} for qa in qa_responses]

        # Run analysis
        analyzer = Analyzer()
        analysis_result = await analyzer.analyze_candidate(
            resume_data,
            linkedin_data,
            job_data,
            company_data,
            qa_data if qa_data else None
        )

        # Save analysis to database
        existing_analysis = db.query(Analysis).filter(
            Analysis.session_id == session_id
        ).first()

        if existing_analysis:
            analysis_record = existing_analysis
        else:
            analysis_record = Analysis(session_id=session_id)
            db.add(analysis_record)

        # Store results
        analysis_record.overall_score = analysis_result.get('overall_score', 0)
        analysis_record.exact_match_score = analysis_result.get('exact_match', {}).get('score', 0)
        analysis_record.transferable_score = analysis_result.get('transferable_match', {}).get('score', 0)
        analysis_record.growth_score = analysis_result.get('growth_potential', {}).get('score', 0)
        analysis_record.culture_score = analysis_result.get('culture_fit', {}).get('score', 0)

        analysis_record.exact_match_data = analysis_result.get('exact_match', {})
        analysis_record.transferable_data = analysis_result.get('transferable_match', {})
        analysis_record.growth_data = analysis_result.get('growth_potential', {})
        analysis_record.culture_data = analysis_result.get('culture_fit', {})

        analysis_record.gaps = analysis_result.get('exact_match', {}).get('gaps', [])
        analysis_record.matches = analysis_result.get('exact_match', {}).get('matches', [])
        analysis_record.key_strengths = analysis_result.get('key_strengths', [])
        analysis_record.key_concerns = analysis_result.get('key_concerns', [])
        analysis_record.tactical_improvements = analysis_result.get('tactical_improvements', [])

        analysis_record.recommendation = analysis_result.get('recommendation', 'moderate_fit')
        analysis_record.confidence = analysis_result.get('confidence', 50)
        analysis_record.analysis_status = "completed"

        db.commit()

    except Exception as e:
        # Mark analysis as failed
        analysis_record = db.query(Analysis).filter(
            Analysis.session_id == session_id
        ).first()

        if analysis_record:
            analysis_record.analysis_status = "failed"
            analysis_record.analysis_error = str(e)
            db.commit()


@router.post("/start", response_model=ScorecardResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """
    Start AI analysis

    This orchestrates the full analysis:
    1. Loads resume, LinkedIn, job posting, company data
    2. Runs Claude API analysis for 4 dimensions
    3. Stores results in database

    Analysis runs in background and may take 30-60 seconds.
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create or update analysis record
    existing = db.query(Analysis).filter(
        Analysis.session_id == request.session_id
    ).first()

    if existing:
        analysis = existing
        analysis.analysis_status = "processing"
    else:
        analysis = Analysis(
            session_id=request.session_id,
            analysis_status="processing"
        )
        db.add(analysis)

    db.commit()
    db.refresh(analysis)

    # Start analysis in background
    background_tasks.add_task(run_analysis_background, request.session_id, db)

    return ScorecardResponse(
        session_id=analysis.session_id,
        overall_score=analysis.overall_score or 0,
        exact_match=analysis.exact_match_data or {},
        transferable_match=analysis.transferable_data or {},
        growth_potential=analysis.growth_data or {},
        culture_fit=analysis.culture_data or {},
        recommendation=analysis.recommendation or "pending",
        analysis_status=analysis.analysis_status
    )


@router.get("/{session_id}/scorecard", response_model=ScorecardResponse)
async def get_scorecard(session_id: str, db: DBSession = Depends(get_db)):
    """Get analysis scorecard"""
    analysis = db.query(Analysis).filter(
        Analysis.session_id == session_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found - run /start first")

    return ScorecardResponse(
        session_id=analysis.session_id,
        overall_score=analysis.overall_score or 0,
        exact_match=analysis.exact_match_data or {},
        transferable_match=analysis.transferable_data or {},
        growth_potential=analysis.growth_data or {},
        culture_fit=analysis.culture_data or {},
        recommendation=analysis.recommendation or "moderate_fit",
        analysis_status=analysis.analysis_status
    )


@router.get("/{session_id}/gaps")
async def get_gaps(session_id: str, db: DBSession = Depends(get_db)):
    """Get skill gaps"""
    analysis = db.query(Analysis).filter(
        Analysis.session_id == session_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "session_id": session_id,
        "gaps": analysis.gaps or [],
        "key_concerns": analysis.key_concerns or []
    }


@router.get("/{session_id}/matches")
async def get_matches(session_id: str, db: DBSession = Depends(get_db)):
    """Get skill matches"""
    analysis = db.query(Analysis).filter(
        Analysis.session_id == session_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "session_id": session_id,
        "matches": analysis.matches or [],
        "key_strengths": analysis.key_strengths or []
    }


@router.get("/{session_id}/improvements")
async def get_tactical_improvements(session_id: str, db: DBSession = Depends(get_db)):
    """Get tactical improvement suggestions"""
    analysis = db.query(Analysis).filter(
        Analysis.session_id == session_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "session_id": session_id,
        "improvements": analysis.tactical_improvements or []
    }


@router.delete("/{session_id}")
async def delete_analysis(session_id: str, db: DBSession = Depends(get_db)):
    """Delete analysis data"""
    analysis = db.query(Analysis).filter(
        Analysis.session_id == session_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.delete(analysis)
    db.commit()

    return {"status": "deleted", "session_id": session_id}
