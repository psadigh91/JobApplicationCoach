# 🎯 Resume Optimizer

> AI-powered resume optimization with confidence scoring and factual grounding

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**Status:** 🎉 **PRODUCTION READY** | [Live Demo](https://staging.d1yuo668y6oplm.amplifyapp.com) | [Documentation](#documentation)

---

## 🌟 Overview

Resume Optimizer is a full-stack web application that helps job seekers create tailored resumes by analyzing their background against specific job postings. The system prevents AI hallucinations through confidence scoring and citation tracking.

### **Key Features**

- ✅ **Multi-source Input:** Resume, cover letter, LinkedIn, job posting, company website
- ✅ **4-Dimension Analysis:** Technical skills, experience level, industry knowledge, soft skills
- ✅ **Dual Resume Generation:** Tactical (keyword matches) + Extrapolated (contextual inference)
- ✅ **Confidence Scoring:** ≥80% auto-included, 60-79% require approval, <60% excluded
- ✅ **Citation Tracking:** Every claim links back to source material
- ✅ **Study Guide:** Personalized learning resources for skill gaps
- ✅ **24-Hour Sessions:** Automatic data deletion for privacy

---

## 🏗️ Tech Stack

### **Frontend**
- React 18 + Vite
- Tailwind CSS
- Rich text editor (Quill/TipTap)
- Real-time API integration

### **Backend**
- Python FastAPI
- SQLAlchemy ORM
- SQLite database (swappable to PostgreSQL)
- Claude API (Anthropic)

### **Data Processing**
- PyPDF2, python-docx (resume parsing)
- BeautifulSoup4, aiohttp (web scraping)
- ReportLab (PDF export)

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### **Setup**

```bash
# 1. Clone the repository
git clone https://github.com/psadigh91/JobApplicationCoach.git
cd JobApplicationCoach

# 2. Navigate to project directory (if nested)
cd resume-optimizer  # Only if files are in subdirectory

# 3. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Start the application
./scripts/start.sh
```

### **Access**
- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### **Stop**
```bash
./scripts/stop.sh
```

---

## 📁 Project Structure

```
resume-optimizer/
├── backend/                # Python FastAPI backend
│   ├── core/              # Business logic
│   │   ├── database.py    # SQLAlchemy models
│   │   └── extractors/    # Data extraction modules
│   ├── api/               # API endpoints (8 routers)
│   └── main.py            # FastAPI app
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # 6 wizard pages
│   │   ├── context/       # State management
│   │   └── services/      # API client
│   └── package.json
├── database/              # SQLite database (auto-created)
├── uploads/               # Temporary file storage
├── scripts/               # Setup/start/stop scripts
└── docs/                  # Documentation
```

---

## 🎯 6-Step Wizard Flow

1. **Upload Inputs** - Resume, cover letter, LinkedIn, job posting, company URL
2. **Interactive Q&A** - Additional context (interview stage, recruiter insights)
3. **Review Analysis** - 4-dimension scorecard with gaps & matches
4. **Edit Resumes** - Side-by-side tactical vs extrapolated
5. **Study Guide** - Resources for skill gaps (YouTube, courses, articles)
6. **Export** - Download optimized resumes (PDF/HTML)

---

## 🔐 Anti-Hallucination Strategy

**Conservative inference with confidence scores:**
- **≥80% confidence:** Auto-included with green badge
- **60-79% confidence:** Flagged with yellow badge + requires user approval
- **<60% confidence:** Excluded entirely

**Citation requirement:** Every claim must cite source (resume, LinkedIn, cover letter, or company research)

---

## 🛠️ API Endpoints

### **Session Management** (`/api/sessions`)
- `POST /` - Create session
- `GET /{id}` - Get session status
- `PUT /{id}/step` - Update wizard step
- `DELETE /{id}` - Delete session

### **Uploads** (`/api/uploads`)
- `POST /resume` - Upload resume
- `POST /job-posting` - Upload job posting
- `POST /job-posting-url` - Scrape job from URL

### **Analysis** (`/api/analyze`)
- `POST /start` - Start AI analysis
- `GET /{session_id}/scorecard` - Get results

### **Resume Generation** (`/api/resume`)
- `POST /generate` - Generate resumes
- `GET /{version_id}` - Get resume version

See [API Documentation](http://localhost:8000/docs) for complete endpoint list.

---

## 📊 Database Schema

**9 Core Tables:**
- `sessions` - 24-hour user sessions
- `uploads` - File uploads with processing status
- `linkedin_data` - Profile data from URL/PDF
- `company_research` - Website crawl results (max 10 pages)
- `analysis_results` - 4-dimension scorecard
- `resume_versions` - Tactical + extrapolated versions
- `citations` - Source tracking for all claims
- `study_resources` - Learning resources by gap
- `qa_responses` - Interactive Q&A data

---

## 📝 Configuration

### **Environment Variables** (`.env`)
```bash
DATABASE_URL=sqlite:///./database/resume_optimizer.db
ANTHROPIC_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
SESSION_EXPIRY_HOURS=24
MAX_UPLOAD_SIZE_MB=10
MAX_CRAWL_PAGES=10
CRAWL_TIMEOUT_SECONDS=30
```

---

## 🚢 Deployment

### **Docker Deployment** (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost
```

### **AWS Deployment**

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide including:
- AWS Amplify (frontend)
- AWS Elastic Beanstalk (backend)
- RDS PostgreSQL setup

---

## 🧪 Testing

### **Backend**
```bash
cd backend
source venv/bin/activate

# Test database initialization
python -c "from core.database import init_db; init_db()"

# Start API server
python main.py

# Visit http://localhost:8000/docs for interactive API docs
```

### **Frontend**
```bash
cd frontend
npm install
npm run dev

# Visit http://localhost:5173
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[USER-GUIDE.md](USER-GUIDE.md)** - Complete user manual
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[CONTRIBUTING.md](.github/CONTRIBUTING.md)** - Contribution guidelines
- **[CODE_OF_CONDUCT.md](.github/CODE_OF_CONDUCT.md)** - Community standards
- **[SECURITY.md](.github/SECURITY.md)** - Security policy

---

## 🔒 Security & Privacy

### **Data Protection:**
- 24-hour auto-delete
- No permanent storage
- Session-based isolation
- No user accounts required
- No third-party sharing

### **Security Features:**
- Input validation
- File type restrictions
- Size limits (10MB)
- CORS configuration
- SQL injection protection

See [SECURITY.md](.github/SECURITY.md) for security policy and vulnerability reporting.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](.github/CONTRIBUTING.md) for:
- How to report bugs
- How to suggest features
- Development setup
- Code style guidelines
- Pull request process

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- UI components from [Tailwind CSS](https://tailwindcss.com/)
- Icons from [Lucide React](https://lucide.dev/)

---

## 🎯 Roadmap

### **Phase 1** (Current - v1.0) ✅
- Complete full-stack implementation
- All 6 wizard steps
- Dual resume generation
- Study guide generation
- Export functionality

### **Phase 2** (Planned)
- PostgreSQL migration
- Redis caching
- User accounts (optional)
- Resume history
- A/B testing different prompts

### **Phase 3** (Future)
- Interview prep module
- Cover letter generation
- LinkedIn optimizer
- Job board integration

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check existing [documentation](#documentation)
- Review [FAQ in User Guide](USER-GUIDE.md)

---

**⭐ Star this repo if you find it helpful!**

**Built with ❤️ using Claude Code**
