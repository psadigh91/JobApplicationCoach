# 📖 User Guide - Resume Optimizer

Complete guide to using the Resume Optimizer application.

---

## 🎯 Overview

Resume Optimizer is an AI-powered tool that helps you create tailored resumes by:
- Analyzing your background against job requirements
- Providing 4-dimension confidence scoring
- Generating optimized resume versions
- Creating personalized study guides for skill gaps

**Key Features:**
- ✅ Multi-source input (resume, LinkedIn, company website)
- ✅ AI analysis with confidence scoring
- ✅ Dual resume generation (tactical + extrapolated)
- ✅ Personalized learning resources
- ✅ PDF/HTML export
- ✅ Privacy-first (24-hour auto-delete)

---

## 🚀 Getting Started

### **Step 1: Access the Application**

Visit http://localhost:5173 (or your deployed URL)

You'll see a welcome screen with a 6-step wizard.

### **Step 2: Upload Your Materials**

The wizard will guide you through each step automatically.

---

## 📝 Step-by-Step Walkthrough

### **Step 1: Upload Files** (Required)

**Required Uploads:**

1. **Resume** (PDF or DOCX, max 10MB)
   - Drag and drop or click to browse
   - System extracts: contact info, experience, education, skills, certifications
   - Processing takes 5-10 seconds

2. **Job Posting** (Text or File)
   - **Option A:** Paste job description text
   - **Option B:** Upload job posting file (PDF, DOCX, TXT)
   - System extracts: required skills, preferred skills, responsibilities

**Optional Enhancements:**

3. **LinkedIn Profile** (2 methods)
   - **Method A:** Enter LinkedIn URL (may require PDF fallback)
   - **Method B:** Upload LinkedIn PDF export (more reliable)
   - **How to get PDF:** LinkedIn profile → More → Save to PDF

4. **Company Website**
   - Enter company name and website URL
   - System crawls up to 10 pages (about, careers, culture)
   - Takes 10-20 seconds

5. **Cover Letter** (Optional)
   - Upload your cover letter (PDF, DOCX, or TXT)
   - Helps AI understand your motivations

**What Happens:**
- Files are processed in real-time
- You'll see status updates (pending → processing → completed)
- Green checkmarks appear when complete

**Tips:**
- Use clear, well-formatted resumes
- Paste full job descriptions for better analysis
- LinkedIn PDF export is more reliable than URL scraping
- Company website analysis improves culture fit scoring

---

### **Step 2: Answer Questions** (Optional)

**5 Quick Questions:**

1. Years of professional experience
2. Short-term career goals (1-2 years)
3. Top 3 strengths
4. Learning preference (courses, docs, projects, etc.)
5. Availability to start

**Purpose:**
- Improves analysis accuracy
- Personalizes recommendations
- Helps with growth potential scoring

**You Can:**
- Answer all questions (recommended)
- Answer some questions
- Skip this step entirely

**What Happens:**
- Click "Submit & Start Analysis"
- AI analysis begins (30-60 seconds)
- Progress indicator shows status

---

### **Step 3: View Analysis** (Results)

**4-Dimension Scorecard:**

1. **Exact Match (0-100)**
   - Skills explicitly in both resume and job posting
   - Example: "Python" in both
   - Higher = more direct matches

2. **Transferable Match (0-100)**
   - Adjacent skills that transfer to the role
   - Example: React → Vue, AWS → Azure
   - Shows your adaptability

3. **Growth Potential (0-100)**
   - How quickly you can learn missing skills
   - Based on learning history and background
   - Example: Self-taught Python → Can learn Go

4. **Culture Fit (0-100)**
   - Alignment with company values and mission
   - Based on company website and your profile
   - Example: "Innovation" mentioned in both

**Overall Score:**
- Weighted average of 4 dimensions
- Color-coded recommendation:
  - Green: Strong Fit (80-100)
  - Yellow: Moderate Fit (60-79)
  - Gray: Needs Review (<60)

**Detailed Views:**

**Strengths (Green):**
- Skills you have that match requirements
- Evidence from resume/LinkedIn
- Confidence score per skill

**Growth Opportunities (Yellow):**
- Missing required skills
- Impact level (high/medium/low)
- Suggestions for improvement

**Transferable Skills (Blue):**
- Skills that translate to requirements
- Transferability rating
- Learning curve estimate

**What to Do:**
- Review your scores
- Note which gaps are "high impact"
- Check if transferable skills make sense
- Click "Generate Optimized Resumes"

---

### **Step 4: Review Resumes** (2 Versions)

You get **two resume versions:**

#### **Tactical Version** (Use Immediately)

**What It Is:**
- 100% truthful improvements
- Keywords optimized for ATS
- Bullets reordered for impact
- Metrics highlighted

**Changes Include:**
- Rewriting bullets for clarity
- Adding relevant keywords
- Highlighting quantifiable results
- Improving formatting

**Example:**
- Before: "Built web applications"
- After: "Built scalable web applications using React and Node.js, serving 1M+ users"

**When to Use:**
- Apply to jobs immediately
- All claims are verifiable
- No interview red flags

#### **Extrapolated Version** (Future Use)

**What It Is:**
- 3-month growth projection
- Skills marked "(Learning)" or "(In Progress)"
- Planned projects included
- Study guide aligned

**Changes Include:**
- Adding "Kubernetes (Learning)"
- Planned certifications
- Side projects you'll build
- Future contributions

**Warnings Included:**
- "This resume includes projected skills"
- "Be prepared to discuss learning timeline"
- "Use after completing study guide"

**When to Use:**
- After studying for 2-3 months
- When asked about future skills
- For aspirational roles

**Features:**

- **Side-by-Side Comparison:** Toggle between versions
- **Modifications List:** See what changed and why
- **Full Preview:** View complete resume
- **Skills Highlight:** Color-coded (existing vs learning)

**Tips:**
- Save both versions
- Use tactical for immediate applications
- Work on study guide before using extrapolated
- Be honest about "(In Progress)" skills in interviews

---

### **Step 5: Study Guide** (Close Skill Gaps)

**Personalized Learning Path:**

For each high-impact skill gap, you get:

**1. Learning Phases:**
- **Foundation** (2 weeks): Core concepts
- **Practice** (2 weeks): Hands-on projects
- **Certification** (2 weeks): Exam prep (optional)

**2. Curated Resources:**
- **Videos:** YouTube tutorials (free)
- **Courses:** Udemy, Coursera, Pluralsight
- **Documentation:** Official docs
- **Tutorials:** Step-by-step guides

**3. Resource Details:**
- Provider name
- Duration estimate
- Free/Paid indicator
- Credibility rating (High/Medium/Low)

**4. Project Suggestions:**
- Portfolio projects to build
- Demonstrates the skill
- Implementation steps
- Example repos

**5. Timeline:**
- Total estimated hours
- Weekly breakdown
- Priority level

**Example Study Path for "Kubernetes":**

**Foundation (2 weeks, 10 hours):**
- Video: "Kubernetes Tutorial for Beginners" (TechWorld with Nana, Free, High credibility)
- Course: "Kubernetes Fundamentals" (Pluralsight, Paid)

**Practice (2 weeks, 15 hours):**
- Tutorial: "Deploy Node.js App to K8s"
- Project: "Build microservices deployment"

**Certification (2 weeks, 15 hours):**
- Course: "CKA Exam Prep" (Udemy)
- Practice tests

**Total:** 40 hours over 6 weeks

**Tips:**
- Start with high-priority gaps
- Follow the phases in order
- Build the suggested projects
- Add projects to GitHub
- Update resume as you learn

---

### **Step 6: Export** (Download Files)

**Export Options:**

**1. Tactical Resume**
- Export as PDF (for applications)
- Export as HTML (for web portfolio)

**2. Extrapolated Resume**
- Export as PDF (for future use)
- Export as HTML

**How to Export:**
1. Click "Export as PDF" or "Export as HTML"
2. Wait 5-10 seconds for generation
3. File appears in "Ready to Download"
4. Click download button
5. File saves to your computer

**File Names:**
- `resume_tactical_123_20260617.pdf`
- `resume_extrapolated_456_20260617.html`

**Tips for Using Exports:**

**PDF (Recommended for Applications):**
- Upload to job boards
- Email to recruiters
- Print for interviews
- ATS-friendly format

**HTML (For Online Portfolio):**
- Host on personal website
- Share via link
- Customize further
- SEO-friendly

**Usage Tips:**

✅ **DO:**
- Save both versions
- Use tactical for applications NOW
- Complete study guide before using extrapolated
- Keep versions updated
- Customize per job

❌ **DON'T:**
- Use extrapolated without learning first
- Lie about "(In Progress)" skills
- Send generic resume to every job
- Forget to proofread

---

## 🔒 Privacy & Data

### **What We Store:**
- Uploaded files (resume, cover letter, job posting)
- Extracted data (skills, experience, education)
- Analysis results
- Generated resumes

### **What We DON'T Store:**
- Credit card information (not collected)
- Permanent user accounts
- Login credentials
- Personal identifiers beyond session

### **Auto-Delete Policy:**
- All data deleted after **24 hours**
- No recovery after deletion
- Sessions expire automatically
- No long-term storage

### **Security:**
- Files processed locally
- API calls encrypted (HTTPS)
- No data shared with third parties
- Claude API used for analysis only

**Recommendation:** Download your resumes before 24 hours!

---

## 💡 Tips for Best Results

### **Resume Upload:**
- ✅ Use clear, well-formatted resumes
- ✅ Include contact information
- ✅ List all relevant skills
- ✅ Quantify achievements (numbers, percentages)
- ❌ Don't use fancy fonts or graphics
- ❌ Avoid tables or complex layouts

### **Job Posting:**
- ✅ Paste complete job description
- ✅ Include responsibilities and requirements
- ✅ Copy from original source
- ❌ Don't summarize or edit
- ❌ Avoid truncated descriptions

### **LinkedIn:**
- ✅ Use PDF export (more reliable)
- ✅ Ensure profile is up-to-date
- ✅ Include recommendations section
- ❌ Don't use outdated exports

### **Analysis:**
- ✅ Review all 4 dimensions
- ✅ Focus on high-impact gaps
- ✅ Understand transferable skills
- ❌ Don't ignore low scores

### **Resume Usage:**
- ✅ Customize per application
- ✅ Proofread carefully
- ✅ Match keywords to job posting
- ❌ Don't send same resume to all jobs
- ❌ Don't fabricate skills

### **Study Guide:**
- ✅ Start immediately
- ✅ Follow phases in order
- ✅ Build portfolio projects
- ✅ Update resume as you learn
- ❌ Don't skip fundamentals
- ❌ Don't add skills before learning

---

## ❓ FAQs

**Q: How long does analysis take?**
A: 30-60 seconds for most resumes.

**Q: Can I edit the generated resumes?**
A: Yes! Download and edit in Word/Google Docs.

**Q: Is my data secure?**
A: Yes. Auto-deleted after 24 hours. No permanent storage.

**Q: Can I use this for multiple jobs?**
A: Yes! Start a new session for each job.

**Q: What if LinkedIn scraping fails?**
A: Use the PDF export method (more reliable).

**Q: Is the extrapolated version truthful?**
A: Partially. It includes future projections marked "(Learning)".

**Q: How accurate is the analysis?**
A: Based on AI (Claude), confidence-scored, but review carefully.

**Q: Can I reuse my resumes after 24 hours?**
A: Download them first! They're deleted automatically.

**Q: What file formats are supported?**
A: PDF and DOCX for uploads. PDF and HTML for exports.

**Q: Do I need all optional uploads?**
A: No. Resume + job posting are sufficient.

---

## 🎯 Success Checklist

**Before Applying:**
- [ ] Generated tactical resume
- [ ] Reviewed all modifications
- [ ] Proofread for errors
- [ ] Customized for specific job
- [ ] Downloaded PDF version
- [ ] Prepared to discuss all claims

**After Analysis:**
- [ ] Noted high-impact skill gaps
- [ ] Reviewed study guide
- [ ] Started learning top priority skill
- [ ] Built at least one portfolio project
- [ ] Updated LinkedIn profile
- [ ] Prepared interview talking points

**For Extrapolated Resume:**
- [ ] Completed 50%+ of study guide
- [ ] Built planned projects
- [ ] Can discuss learning progress
- [ ] Set realistic timelines
- [ ] Ready to demonstrate skills

---

## 📞 Need Help?

**If something isn't working:**
1. Refresh the page
2. Check file formats (PDF/DOCX only)
3. Verify file size (<10MB)
4. Try LinkedIn PDF export instead of URL
5. Check internet connection
6. Wait for background tasks to complete

**For bugs or issues:**
- Check browser console (F12)
- Try different browser
- Clear browser cache
- Restart the session

---

**🎉 Good luck with your job search!**
