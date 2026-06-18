"""
Database models for Resume Optimizer
SQLAlchemy ORM models with relationships
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

Base = declarative_base()


class Session(Base):
    """User session tracking with 24-hour expiry"""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24), index=True)
    status = Column(String, default='active')  # 'active', 'expired', 'completed'
    current_step = Column(Integer, default=1)  # Wizard step (1-6)

    # Relationships
    uploads = relationship("Upload", back_populates="session", cascade="all, delete-orphan")
    linkedin_data = relationship("LinkedInData", back_populates="session", uselist=False, cascade="all, delete-orphan")
    company_research = relationship("CompanyResearch", back_populates="session", uselist=False, cascade="all, delete-orphan")
    analysis = relationship("Analysis", back_populates="session", uselist=False, cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="session", cascade="all, delete-orphan")
    study_resources = relationship("StudyResource", back_populates="session", cascade="all, delete-orphan")
    qa_responses = relationship("QAResponse", back_populates="session", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="session", cascade="all, delete-orphan")


class Upload(Base):
    """File uploads with processing status"""
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    upload_type = Column(String)  # 'resume', 'cover_letter', 'job_posting'
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Extracted content
    raw_text = Column(Text)
    structured_data = Column(JSON)
    processing_status = Column(String, default='pending')  # 'pending', 'processing', 'completed', 'failed'
    processing_error = Column(Text, nullable=True)

    # Relationship
    session = relationship("Session", back_populates="uploads")


# Add index for session + type lookups
Index('idx_uploads_session_type', Upload.session_id, Upload.upload_type)


class LinkedInData(Base):
    """LinkedIn profile data from URL or PDF"""
    __tablename__ = "linkedin_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, index=True)
    source_type = Column(String)  # 'url_scrape', 'pdf_upload', 'manual_entry'
    linkedin_url = Column(String, nullable=True)

    # Structured profile data
    profile_data = Column(JSON)  # {name, headline, summary, experience[], education[], skills[], certifications[]}

    scraping_status = Column(String, default='pending')  # 'pending', 'success', 'failed', 'fallback_to_pdf'
    scraping_error = Column(Text, nullable=True)
    scraped_at = Column(DateTime, nullable=True)

    # Relationship
    session = relationship("Session", back_populates="linkedin_data")


class CompanyResearch(Base):
    """Company website crawl results"""
    __tablename__ = "company_research"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, index=True)
    company_name = Column(String)
    company_website = Column(String)

    # Crawled pages
    pages_crawled = Column(JSON)  # [{url, title, content, word_count, crawled_at}, ...]
    crawl_count = Column(Integer, default=0)
    crawl_status = Column(String, default='pending')  # 'pending', 'in_progress', 'completed', 'failed'
    crawl_error = Column(Text, nullable=True)

    # Extracted insights
    company_summary = Column(Text)
    company_culture = Column(JSON)  # Extracted culture keywords
    products_services = Column(JSON)  # List of products/services
    tech_stack = Column(JSON)  # Technologies mentioned

    crawled_at = Column(DateTime, nullable=True)

    # Relationship
    session = relationship("Session", back_populates="company_research")


class Analysis(Base):
    """Analysis results with 4-dimension scorecard"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, index=True)

    # 4-dimension scorecard
    scorecard = Column(JSON)  # {
    #   technical_skills: {score: 75, matches: [...], gaps: [...]},
    #   experience_level: {score: 60, matches: [...], gaps: [...]},
    #   industry_knowledge: {score: 80, matches: [...], gaps: [...]},
    #   soft_skills: {score: 70, matches: [...], gaps: [...]}
    # }

    overall_score = Column(Integer)  # 0-100

    # Gap analysis
    critical_gaps = Column(JSON)  # [{skill, importance, confidence}, ...]
    nice_to_have_gaps = Column(JSON)

    # Match analysis
    strong_matches = Column(JSON)  # [{skill, evidence, confidence, citation}, ...]
    partial_matches = Column(JSON)

    # Keywords extracted from job posting
    required_keywords = Column(JSON)  # [{keyword, frequency, importance}, ...]
    preferred_keywords = Column(JSON)

    # AI metadata
    analysis_prompt_used = Column(Text)
    model_used = Column(String, default='claude-sonnet-4.5')
    tokens_used = Column(Integer)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("Session", back_populates="analysis")


class ResumeVersion(Base):
    """Generated resume versions (tactical and extrapolated)"""
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    version_type = Column(String)  # 'tactical', 'extrapolated'

    # Content
    content = Column(JSON)  # Structured resume {sections: {contact, summary, experience[], education[], skills[]}}
    formatted_text = Column(Text)  # Plain text version
    html_content = Column(Text)  # HTML formatted version

    # Changes made
    modifications = Column(JSON)  # [{section, change_type, original, modified, confidence, citation, reason}, ...]

    # Keyword tracking
    keywords_added = Column(JSON)  # [{keyword, location, confidence}, ...]
    keywords_optimized = Column(JSON)

    # Confidence scores for changes
    high_confidence_changes = Column(Integer, default=0)  # Count >=80%
    medium_confidence_changes = Column(Integer, default=0)  # Count 60-79%
    low_confidence_changes = Column(Integer, default=0)  # Count <60% (not included)

    # User edits
    user_edited = Column(Integer, default=0)  # Boolean (0 or 1)
    user_edits = Column(JSON, nullable=True)  # Track what user changed

    created_at = Column(DateTime, default=datetime.utcnow)
    last_edited_at = Column(DateTime, nullable=True)

    # Relationship
    session = relationship("Session", back_populates="resume_versions")


# Add index for session + version type lookups
Index('idx_resume_versions_session_type', ResumeVersion.session_id, ResumeVersion.version_type)


class Citation(Base):
    """Citation tracking for all claims"""
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=True)
    study_resource_id = Column(Integer, ForeignKey("study_resources.id"), nullable=True)

    claim = Column(Text)  # The claim being made
    source_type = Column(String)  # 'resume', 'linkedin', 'cover_letter', 'company_research', 'inference'
    source_reference = Column(Text)  # Exact text or data point from source
    source_location = Column(String)  # Where in source document
    confidence = Column(Integer)  # 0-100

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="citations")


# Add index for session lookups
Index('idx_citations_session', Citation.session_id)


class StudyResource(Base):
    """Study guide resources for skill gaps"""
    __tablename__ = "study_resources"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)

    # Gap this addresses
    gap_skill = Column(String)
    gap_category = Column(String)  # 'technical_skills', 'experience_level', 'industry_knowledge', 'soft_skills'
    priority = Column(String)  # 'critical', 'important', 'nice-to-have'

    # Resource details
    resource_type = Column(String)  # 'video', 'course', 'article', 'documentation'
    title = Column(String)
    url = Column(String)
    provider = Column(String)  # 'YouTube', 'Coursera', 'LinkedIn Learning', etc.
    duration = Column(String, nullable=True)  # '2 hours', '4 weeks', etc.
    difficulty_level = Column(String)  # 'beginner', 'intermediate', 'advanced'

    # Quality indicators
    credibility_score = Column(Integer)  # 0-100
    relevance_score = Column(Integer)  # 0-100

    # Metadata
    description = Column(Text)
    estimated_time = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("Session", back_populates="study_resources")


# Add index for session + priority lookups
Index('idx_study_resources_session_priority', StudyResource.session_id, StudyResource.priority)


class QAResponse(Base):
    """Interactive Q&A responses"""
    __tablename__ = "qa_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)

    question_id = Column(String)  # Reference to question
    question_text = Column(Text)
    answer = Column(Text)
    answered_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("Session", back_populates="qa_responses")


# Database initialization and helper functions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database URL (SQLite for now, can be swapped for PostgreSQL)
DATABASE_URL = "sqlite:///./database/resume_optimizer.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def cleanup_expired_sessions():
    """Background task to delete expired sessions"""
    db = SessionLocal()
    try:
        expired = db.query(Session).filter(
            Session.expires_at < datetime.utcnow(),
            Session.status == 'active'
        ).all()

        for session in expired:
            session.status = 'expired'
            # Cascade delete will handle related records
            db.delete(session)

        db.commit()
        return len(expired)
    finally:
        db.close()
