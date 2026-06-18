# 🚀 Resume Optimizer - Quick Start Guide

**Status:** Backend Complete ✅  
**Next:** Frontend (Session 3)

---

## 📋 Quick Setup (5 minutes)

### **1. Backend Setup:**

```bash
cd ./backend

# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env and add your ANTHROPIC_API_KEY=your_key_here

# Initialize database
python -c "from core.database import init_db; init_db()"
```

### **2. Start Backend:**

```bash
python main.py
# OR
uvicorn main:app --reload
```

**Server runs at:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

---

## 🧪 Test the API

### **Method 1: Interactive Docs (Easiest)**

1. Go to http://localhost:8000/docs
2. Try each endpoint with the built-in Swagger UI
3. Expand an endpoint → Click "Try it out" → Execute

### **Method 2: curl Commands**

**Create a session:**
```bash
curl -X POST http://localhost:8000/api/sessions
```

**Upload resume:**
```bash
curl -X POST http://localhost:8000/api/upload/resume \
  -F "session_id=YOUR_SESSION_ID" \
  -F "file=@path/to/resume.pdf"
```

**Upload job posting (paste text):**
```bash
curl -X POST http://localhost:8000/api/upload/job-posting \
  -F "session_id=YOUR_SESSION_ID" \
  -F "text=Senior Software Engineer at TechCorp. Requirements: Python, React, AWS..."
```

**Start AI analysis:**
```bash
curl -X POST http://localhost:8000/api/analyze/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID"}'
```

**Get scorecard (wait 30-60 seconds after starting):**
```bash
curl http://localhost:8000/api/analyze/YOUR_SESSION_ID/scorecard
```

### **Method 3: Python Script**

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create session
response = requests.post(f"{BASE_URL}/sessions")
session_id = response.json()["id"]
print(f"Session: {session_id}")

# Upload resume
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload/resume",
        data={"session_id": session_id},
        files={"file": f}
    )
print("Resume uploaded:", response.json())

# Upload job posting
job_text = """
Senior Software Engineer at TechCorp
Requirements:
- 5+ years Python
- React.js experience
- AWS cloud experience
"""

response = requests.post(
    f"{BASE_URL}/upload/job-posting",
    data={"session_id": session_id, "text": job_text}
)
print("Job posted:", response.json())

# Start analysis
response = requests.post(
    f"{BASE_URL}/analyze/start",
    json={"session_id": session_id}
)
print("Analysis started:", response.json())

# Wait and get scorecard
import time
time.sleep(60)  # Wait for analysis to complete

response = requests.get(f"{BASE_URL}/analyze/{session_id}/scorecard")
print("Scorecard:", response.json())
```

---

## 🎯 Full Workflow Test

### **Step-by-Step:**

1. **Create Session**
   - POST /api/sessions
   - Save the returned `session_id`

2. **Upload Files**
   - POST /api/upload/resume (PDF/DOCX)
   - POST /api/upload/job-posting (text or file)
   - Optional: POST /api/upload/cover-letter

3. **LinkedIn (Optional)**
   - POST /api/linkedin/pdf (upload LinkedIn PDF export)
   - OR POST /api/linkedin/scrape (try URL scraping)

4. **Company Research (Optional)**
   - POST /api/company/crawl
   - Wait ~10 seconds
   - GET /api/company/{session_id} (check status)
   - GET /api/company/{session_id}/pages

5. **Run Analysis**
   - POST /api/analyze/start
   - Wait 30-60 seconds (runs in background)
   - GET /api/analyze/{session_id}/scorecard

6. **View Results**
   - GET /api/analyze/{session_id}/scorecard (4D scores)
   - GET /api/analyze/{session_id}/gaps (skill gaps)
   - GET /api/analyze/{session_id}/matches (matches)
   - GET /api/analyze/{session_id}/improvements (tactical tips)

7. **Generate Resumes**
   - POST /api/resume/generate
   - Wait 30-60 seconds
   - GET /api/resume/session/{session_id} (list versions)
   - GET /api/resume/{version_id} (get specific version)
   - GET /api/resume/{version_id}/diff (see modifications)

8. **Generate Study Guide**
   - POST /api/study/generate
   - Wait 20-30 seconds
   - GET /api/study/{session_id}

9. **Export**
   - POST /api/export/pdf (with version_id)
   - POST /api/export/html (with version_id)
   - GET /api/export/download/{filename}

---

## 🔍 Troubleshooting

### **"ANTHROPIC_API_KEY not found"**
- Create `.env` file in backend directory
- Add: `ANTHROPIC_API_KEY=your_key_here`
- Get key from: https://console.anthropic.com/

### **"Database file not found"**
```bash
cd backend
python -c "from core.database import init_db; init_db()"
```

### **"Module not found" errors**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### **"Port 8000 already in use"**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# OR use different port
uvicorn main:app --port 8001
```

---

## 📊 What's Working

✅ **All 30+ API Endpoints**
- Session management
- File uploads (resume, cover letter, job posting)
- LinkedIn integration (URL + PDF)
- Company website crawling
- AI analysis (Claude API)
- Resume generation (tactical + extrapolated)
- Study guide generation
- PDF/HTML export

✅ **Data Processing**
- PDF/DOCX parsing
- Job posting parsing
- LinkedIn profile extraction
- Company website scraping

✅ **AI Features**
- 4-dimension scorecard
- Skill matching
- Gap detection
- Confidence scoring
- Tactical improvements
- Study guide generation

---

## 📁 Backend Structure

```
backend/
├── main.py                    # FastAPI app
├── core/
│   ├── database.py           # 9 SQLAlchemy models
│   ├── analyzer.py           # Claude API integration
│   ├── confidence_scorer.py  # Scoring engine
│   ├── resume_generator.py   # Resume generation
│   ├── study_guide_builder.py # Study guide
│   ├── skill_taxonomy.py     # Skill normalization
│   └── extractors/
│       ├── resume_parser.py
│       ├── linkedin_scraper.py
│       ├── company_crawler.py
│       └── job_posting_parser.py
└── api/
    ├── session.py
    ├── upload.py
    ├── linkedin.py
    ├── company.py
    ├── analyze.py
    ├── resume.py
    ├── study.py
    └── export_routes.py
```

---

## 🎯 Next: Frontend

**Session 3 will build:**
- React app (Vite + Tailwind)
- 6 wizard pages
- 10+ components
- Real-time updates
- State management

**To continue:**
"Continue Session 3: Frontend Implementation - Build React UI"

---

## 💡 Tips

1. **Use Interactive Docs:** http://localhost:8000/docs is the easiest way to test
2. **Save session IDs:** You'll need them for subsequent requests
3. **Background tasks:** Analysis and generation run in background (30-60s)
4. **Check status:** Use GET endpoints to check if background tasks completed
5. **Mock data:** If you don't have files, use the `/docs` interface to test with sample data

---

**🚀 Backend is ready! Try it out!**
