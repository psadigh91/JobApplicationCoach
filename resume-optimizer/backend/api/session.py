"""
Session management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from core.database import get_db, Session as SessionModel

router = APIRouter()


# Request/Response models
class SessionCreate(BaseModel):
    pass  # No input needed, session created automatically


class SessionResponse(BaseModel):
    session_id: str
    status: str
    current_step: int
    created_at: datetime
    expires_at: datetime
    time_remaining: str  # Human-readable like "18h 42m"


class StepUpdate(BaseModel):
    step: int  # 1-6


@router.post("/", response_model=SessionResponse)
async def create_session(db: DBSession = Depends(get_db)):
    """Create new session with 24-hour expiry"""
    session = SessionModel()
    db.add(session)
    db.commit()
    db.refresh(session)
    
    time_remaining = session.expires_at - datetime.utcnow()
    hours = int(time_remaining.total_seconds() // 3600)
    minutes = int((time_remaining.total_seconds() % 3600) // 60)
    
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        current_step=session.current_step,
        created_at=session.created_at,
        expires_at=session.expires_at,
        time_remaining=f"{hours}h {minutes}m"
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: DBSession = Depends(get_db)):
    """Get session status and progress"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if expired
    if session.expires_at < datetime.utcnow():
        session.status = 'expired'
        db.commit()
        raise HTTPException(status_code=410, detail="Session expired")
    
    time_remaining = session.expires_at - datetime.utcnow()
    hours = int(time_remaining.total_seconds() // 3600)
    minutes = int((time_remaining.total_seconds() % 3600) // 60)
    
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        current_step=session.current_step,
        created_at=session.created_at,
        expires_at=session.expires_at,
        time_remaining=f"{hours}h {minutes}m"
    )


@router.put("/{session_id}/step")
async def update_step(
    session_id: str,
    update: StepUpdate,
    db: DBSession = Depends(get_db)
):
    """Update current wizard step"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Session expired")
    
    if update.step < 1 or update.step > 6:
        raise HTTPException(status_code=400, detail="Step must be between 1 and 6")
    
    session.current_step = update.step
    db.commit()
    
    return {"success": True, "current_step": session.current_step}


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: DBSession = Depends(get_db)):
    """Delete session immediately (user-initiated cleanup)"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"success": True, "message": "Session deleted"}


@router.post("/cleanup")
async def cleanup_expired(db: DBSession = Depends(get_db)):
    """Background task endpoint: delete expired sessions"""
    from core.database import cleanup_expired_sessions
    count = cleanup_expired_sessions()
    return {"cleaned": count, "message": f"Deleted {count} expired sessions"}
