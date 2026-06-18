"""
Company API endpoints - Handle company website crawling
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

from core.database import get_db, CompanyResearch, Session as SessionModel
from core.extractors.company_crawler import CompanyCrawler

router = APIRouter()


class CrawlRequest(BaseModel):
    """Company crawl request"""
    session_id: str
    company_name: str
    company_website: str
    max_pages: int = 10


class CompanyResponse(BaseModel):
    """Company research response"""
    session_id: str
    company_name: str
    company_website: str
    crawl_status: str
    crawl_count: int
    pages: Optional[List[dict]] = None


async def crawl_company_background(
    session_id: str,
    company_website: str,
    max_pages: int,
    db: DBSession
):
    """Background task to crawl company website"""
    try:
        # Update status to in_progress
        company_data = db.query(CompanyResearch).filter(
            CompanyResearch.session_id == session_id
        ).first()

        if company_data:
            company_data.crawl_status = "in_progress"
            db.commit()

        # Perform crawl
        crawler = CompanyCrawler(max_pages=max_pages)
        pages = await crawler.crawl(company_website)

        # Update database
        if company_data:
            company_data.pages_crawled = [
                {
                    'url': p['url'],
                    'title': p['title'],
                    'content': p['content'][:1000],  # Truncate for storage
                    'word_count': p['word_count'],
                    'crawled_at': p['crawled_at']
                }
                for p in pages
            ]
            company_data.crawl_count = len(pages)
            company_data.crawl_status = "completed"
            db.commit()

    except Exception as e:
        # Update status to failed
        if company_data:
            company_data.crawl_status = "failed"
            company_data.crawl_error = str(e)
            db.commit()


@router.post("/crawl", response_model=CompanyResponse)
async def start_company_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """
    Start crawling company website

    Args:
        request: Crawl request with company details
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Company research record (crawl runs in background)
    """
    # Validate session
    session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if company research exists
    existing = db.query(CompanyResearch).filter(
        CompanyResearch.session_id == request.session_id
    ).first()

    if existing:
        # Update existing
        company_data = existing
        company_data.company_name = request.company_name
        company_data.company_website = request.company_website
        company_data.crawl_status = "pending"
    else:
        # Create new
        company_data = CompanyResearch(
            session_id=request.session_id,
            company_name=request.company_name,
            company_website=request.company_website,
            crawl_status="pending"
        )
        db.add(company_data)

    db.commit()
    db.refresh(company_data)

    # Start crawl in background
    background_tasks.add_task(
        crawl_company_background,
        request.session_id,
        request.company_website,
        request.max_pages,
        db
    )

    return CompanyResponse(
        session_id=company_data.session_id,
        company_name=company_data.company_name,
        company_website=company_data.company_website,
        crawl_status=company_data.crawl_status,
        crawl_count=company_data.crawl_count or 0
    )


@router.get("/{session_id}", response_model=CompanyResponse)
async def get_company_data(session_id: str, db: DBSession = Depends(get_db)):
    """Get company research data and crawl status"""
    company_data = db.query(CompanyResearch).filter(
        CompanyResearch.session_id == session_id
    ).first()

    if not company_data:
        raise HTTPException(status_code=404, detail="Company data not found")

    return CompanyResponse(
        session_id=company_data.session_id,
        company_name=company_data.company_name,
        company_website=company_data.company_website,
        crawl_status=company_data.crawl_status,
        crawl_count=company_data.crawl_count or 0
    )


@router.get("/{session_id}/pages")
async def get_crawled_pages(session_id: str, db: DBSession = Depends(get_db)):
    """Get all crawled pages for a session"""
    company_data = db.query(CompanyResearch).filter(
        CompanyResearch.session_id == session_id
    ).first()

    if not company_data:
        raise HTTPException(status_code=404, detail="Company data not found")

    return {
        "session_id": session_id,
        "company_name": company_data.company_name,
        "crawl_status": company_data.crawl_status,
        "pages": company_data.pages_crawled or []
    }


@router.delete("/{session_id}")
async def delete_company_data(session_id: str, db: DBSession = Depends(get_db)):
    """Delete company research data"""
    company_data = db.query(CompanyResearch).filter(
        CompanyResearch.session_id == session_id
    ).first()

    if not company_data:
        raise HTTPException(status_code=404, detail="Company data not found")

    db.delete(company_data)
    db.commit()

    return {"status": "deleted", "session_id": session_id}
