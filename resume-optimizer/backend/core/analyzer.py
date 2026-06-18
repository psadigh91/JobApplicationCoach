"""
Analyzer - Core AI analysis engine using Claude API
Generates 4-dimension scorecard with gap/match detection
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
import json


class Analyzer:
    """AI-powered resume analysis using Claude API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize analyzer with Claude API

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_candidate(
        self,
        resume_data: Dict,
        linkedin_data: Dict,
        job_posting: Dict,
        company_data: List[Dict],
        qa_responses: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Perform comprehensive 4-dimension analysis

        Args:
            resume_data: Parsed resume data
            linkedin_data: LinkedIn profile data
            job_posting: Parsed job posting
            company_data: Crawled company pages
            qa_responses: Optional Q&A responses from user

        Returns:
            Dictionary with 4-dimension scorecard and detailed findings
        """
        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            resume_data, linkedin_data, job_posting, company_data, qa_responses
        )

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,  # Lower temperature for more consistent analysis
            system=self._get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        analysis_text = response.content[0].text

        # Extract structured data from response
        try:
            # Claude should return JSON-formatted analysis
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback: parse from text
            analysis = self._parse_analysis_text(analysis_text)

        return analysis

    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude"""
        return """You are an expert career advisor and resume analyst. Your job is to analyze a candidate's qualifications against a job posting using a 4-dimension framework:

1. **EXACT MATCH (0-100)**: Skills/experience explicitly mentioned in both resume and job posting
2. **TRANSFERABLE MATCH (0-100)**: Adjacent skills that transfer to the role (e.g., React → Vue, AWS → Azure)
3. **GROWTH POTENTIAL (0-100)**: How quickly the candidate can learn missing skills based on their background
4. **CULTURE FIT (0-100)**: Alignment with company values, mission, and work style

For each dimension:
- Calculate a 0-100 score
- Provide specific examples with citations
- List gaps (what's missing) and matches (what's there)
- Rate confidence (0-100) for each finding

Return your analysis as a JSON object with this structure:
{
  "exact_match": {
    "score": 85,
    "matches": [{"skill": "Python", "evidence": "5 years Python at Google", "citation": "resume_page_1"}],
    "gaps": [{"skill": "Kubernetes", "required": true, "impact": "high"}]
  },
  "transferable_match": {
    "score": 70,
    "matches": [{"from_skill": "React", "to_skill": "Vue", "transferability": "high"}],
    "gaps": [{"skill": "GraphQL", "closest_match": "REST APIs", "learning_curve": "medium"}]
  },
  "growth_potential": {
    "score": 80,
    "learning_speed": "fast",
    "evidence": ["Quick learner demonstrated by...", "Self-taught X, Y, Z"],
    "concerns": []
  },
  "culture_fit": {
    "score": 75,
    "matches": ["Values innovation", "Collaborative team player"],
    "gaps": ["No mention of remote work experience"],
    "company_values": ["Innovation", "Collaboration", "Customer-first"]
  },
  "overall_score": 78,
  "recommendation": "strong_fit|moderate_fit|weak_fit",
  "key_strengths": ["...", "..."],
  "key_concerns": ["...", "..."],
  "tactical_improvements": ["Add Kubernetes projects", "Highlight Vue transferability"],
  "confidence": 85
}

Be specific, cite sources, and focus on actionable insights."""

    def _build_analysis_prompt(
        self,
        resume_data: Dict,
        linkedin_data: Dict,
        job_posting: Dict,
        company_data: List[Dict],
        qa_responses: Optional[List[Dict]]
    ) -> str:
        """Build analysis prompt from all data sources"""

        prompt = "# CANDIDATE ANALYSIS REQUEST\n\n"

        # Resume data
        prompt += "## RESUME DATA\n"
        if resume_data.get('sections'):
            sections = resume_data['sections']
            if sections.get('contact'):
                prompt += f"**Name:** {sections['contact'].get('name', 'Unknown')}\n\n"

            if sections.get('summary'):
                prompt += f"**Summary:** {sections['summary']}\n\n"

            if sections.get('experience'):
                prompt += "**Experience:**\n"
                for exp in sections['experience'][:5]:  # Top 5
                    prompt += f"- {exp.get('title')} at {exp.get('company')} ({exp.get('dates')})\n"
                    for bullet in exp.get('bullets', [])[:3]:  # Top 3 bullets
                        prompt += f"  - {bullet}\n"
                prompt += "\n"

            if sections.get('skills'):
                prompt += f"**Skills:** {', '.join(sections['skills'][:30])}\n\n"

            if sections.get('education'):
                prompt += "**Education:**\n"
                for edu in sections['education']:
                    prompt += f"- {edu.get('degree')} from {edu.get('school')} ({edu.get('dates')})\n"
                prompt += "\n"

        # LinkedIn data
        if linkedin_data and linkedin_data.get('success'):
            prompt += "## LINKEDIN PROFILE\n"
            if linkedin_data.get('headline'):
                prompt += f"**Headline:** {linkedin_data['headline']}\n\n"
            if linkedin_data.get('summary'):
                prompt += f"**Summary:** {linkedin_data['summary'][:500]}\n\n"
            if linkedin_data.get('skills'):
                prompt += f"**LinkedIn Skills:** {', '.join(linkedin_data['skills'][:20])}\n\n"

        # Job posting
        prompt += "## JOB POSTING\n"
        prompt += f"**Title:** {job_posting.get('job_title', 'Unknown')}\n"
        prompt += f"**Company:** {job_posting.get('company', 'Unknown')}\n"
        prompt += f"**Location:** {job_posting.get('location', 'Unknown')}\n\n"

        if job_posting.get('required_skills'):
            prompt += f"**Required Skills:** {', '.join(job_posting['required_skills'])}\n\n"

        if job_posting.get('preferred_skills'):
            prompt += f"**Preferred Skills:** {', '.join(job_posting['preferred_skills'])}\n\n"

        if job_posting.get('responsibilities'):
            prompt += "**Key Responsibilities:**\n"
            for resp in job_posting['responsibilities'][:5]:
                prompt += f"- {resp}\n"
            prompt += "\n"

        if job_posting.get('required_experience'):
            prompt += f"**Experience Required:** {job_posting['required_experience']}\n\n"

        # Company data
        if company_data:
            prompt += "## COMPANY INFORMATION\n"
            for page in company_data[:3]:  # Top 3 pages
                prompt += f"**{page.get('title', 'Company Page')}** ({page.get('url')})\n"
                content = page.get('content', '')
                prompt += f"{content[:500]}...\n\n"

        # Q&A responses
        if qa_responses:
            prompt += "## CANDIDATE Q&A RESPONSES\n"
            for qa in qa_responses:
                prompt += f"**Q:** {qa.get('question')}\n"
                prompt += f"**A:** {qa.get('answer')}\n\n"

        prompt += "\n---\n\n"
        prompt += "Please analyze this candidate against the job posting using the 4-dimension framework. "
        prompt += "Return your analysis as a JSON object as specified in the system prompt."

        return prompt

    def _parse_analysis_text(self, text: str) -> Dict:
        """Fallback parser if Claude doesn't return JSON"""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Return structured fallback
        return {
            "exact_match": {"score": 50, "matches": [], "gaps": []},
            "transferable_match": {"score": 50, "matches": [], "gaps": []},
            "growth_potential": {"score": 50, "learning_speed": "unknown", "evidence": [], "concerns": []},
            "culture_fit": {"score": 50, "matches": [], "gaps": [], "company_values": []},
            "overall_score": 50,
            "recommendation": "moderate_fit",
            "key_strengths": [],
            "key_concerns": ["Analysis parsing failed - review required"],
            "tactical_improvements": [],
            "confidence": 30,
            "raw_analysis": text
        }

    async def generate_tactical_improvements(
        self,
        analysis: Dict,
        resume_data: Dict,
        job_posting: Dict
    ) -> List[Dict]:
        """
        Generate specific tactical resume improvements

        Args:
            analysis: Analysis results
            resume_data: Original resume data
            job_posting: Job posting data

        Returns:
            List of tactical improvements with before/after examples
        """
        prompt = f"""Based on this analysis:

{json.dumps(analysis, indent=2)}

Generate 5-10 tactical improvements for the resume. For each improvement:
1. Identify the specific section/bullet to modify
2. Show the BEFORE version (original text)
3. Show the AFTER version (improved text)
4. Explain WHY this change helps (which gap it addresses)

Return as JSON array:
[
  {{
    "section": "Experience",
    "subsection": "Software Engineer at Google",
    "before": "Built web applications",
    "after": "Built scalable web applications using React and Node.js, serving 1M+ users",
    "rationale": "Addresses exact match gap for React (required skill) and adds impact metrics",
    "priority": "high|medium|low",
    "dimension": "exact_match|transferable|growth|culture"
  }}
]
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        try:
            # Parse JSON response
            json_match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                improvements = json.loads(json_match.group(1))
            else:
                improvements = json.loads(text)

            return improvements

        except:
            return []
