"""
Resume Generator - Generate tactical and extrapolated resume versions
Uses Claude API to apply improvements while maintaining truthfulness
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
import json
import re


class ResumeGenerator:
    """Generate optimized resume versions with AI assistance"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Claude API"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_tactical_version(
        self,
        resume_data: Dict,
        improvements: List[Dict],
        job_posting: Dict
    ) -> Dict:
        """
        Generate tactical resume version (truthful improvements only)

        Args:
            resume_data: Original parsed resume
            improvements: List of tactical improvements from analyzer
            job_posting: Target job posting

        Returns:
            Dictionary with tactical resume content and modifications
        """
        prompt = self._build_tactical_prompt(resume_data, improvements, job_posting)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.4,
            system=self._get_tactical_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Parse response
        try:
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(text)

            return result

        except json.JSONDecodeError:
            # Fallback: return text as-is
            return {
                "version_type": "tactical",
                "sections": {},
                "modifications": [],
                "raw_output": text
            }

    async def generate_extrapolated_version(
        self,
        resume_data: Dict,
        tactical_version: Dict,
        analysis: Dict,
        job_posting: Dict
    ) -> Dict:
        """
        Generate extrapolated version (with growth projections)

        Args:
            resume_data: Original resume
            tactical_version: Tactical resume version
            analysis: Gap analysis
            job_posting: Target job

        Returns:
            Dictionary with extrapolated resume and modifications
        """
        prompt = self._build_extrapolated_prompt(
            resume_data, tactical_version, analysis, job_posting
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.5,  # Slightly higher for creative extrapolation
            system=self._get_extrapolated_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Parse response
        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(text)

            return result

        except json.JSONDecodeError:
            return {
                "version_type": "extrapolated",
                "sections": {},
                "modifications": [],
                "warnings": ["Failed to parse extrapolated version"],
                "raw_output": text
            }

    def _get_tactical_system_prompt(self) -> str:
        """System prompt for tactical improvements"""
        return """You are a professional resume writer. Your job is to make TACTICAL improvements to a resume - improvements that are 100% truthful and verifiable.

TACTICAL improvements include:
- Reordering bullet points to highlight relevant experience
- Adding specific metrics/numbers that are present in the original resume but not prominent
- Rewriting bullets to emphasize transferable skills
- Adding relevant keywords from the job posting (only if the candidate actually has that experience)
- Improving clarity and impact of existing statements
- Restructuring sections for better flow

NEVER:
- Add skills the candidate doesn't have
- Exaggerate experience or accomplishments
- Fabricate projects, roles, or achievements
- Stretch the truth in any way

Your output should be a JSON object with:
{
  "version_type": "tactical",
  "sections": {
    "contact": {...},
    "summary": "improved summary text",
    "experience": [
      {
        "title": "...",
        "company": "...",
        "dates": "...",
        "bullets": ["improved bullet 1", "improved bullet 2"]
      }
    ],
    "education": [...],
    "skills": [...],
    "certifications": [...]
  },
  "modifications": [
    {
      "section": "Experience",
      "subsection": "Software Engineer at Google",
      "change_type": "rewrite|reorder|add_metric|add_keyword",
      "before": "original text",
      "after": "improved text",
      "rationale": "why this helps",
      "truthful": true
    }
  ]
}"""

    def _get_extrapolated_system_prompt(self) -> str:
        """System prompt for extrapolated version"""
        return """You are a career coach helping candidates prepare for growth. Your job is to create an EXTRAPOLATED resume - showing how the candidate's current trajectory could develop with focused learning.

EXTRAPOLATED improvements include:
- Adding "In Progress" or "Currently Learning" skills that are realistic given their background
- Projecting side projects they could build in the next 2-3 months
- Suggesting certifications they could obtain quickly
- Showing how existing skills could be applied to new domains
- Adding realistic future contributions based on their learning plan

GUIDELINES:
- All extrapolations must be achievable within 3 months with focused effort
- Mark extrapolated items clearly with "(In Progress)", "(Learning)", or "(Planned)"
- Base extrapolations on their existing skill trajectory
- Include a confidence score (0-100) for each extrapolation

Your output should be JSON:
{
  "version_type": "extrapolated",
  "sections": {
    "summary": "enhanced summary with growth trajectory",
    "experience": [...],
    "skills": ["existing skill", "new skill (In Progress)", ...],
    "projects": [
      {
        "name": "Project name",
        "status": "planned|in_progress|completed",
        "description": "...",
        "skills_demonstrated": ["..."]
      }
    ],
    "certifications": ["existing", "planned certification (In Progress)"]
  },
  "modifications": [
    {
      "section": "Skills",
      "change_type": "extrapolation",
      "added": "Kubernetes (Learning)",
      "basis": "Strong Docker experience + high growth potential",
      "confidence": 85,
      "timeline": "2-3 months",
      "learning_plan": "Complete Kubernetes certification course"
    }
  ],
  "warnings": [
    "This resume includes projected skills and planned projects",
    "All extrapolated items are marked with (In Progress) or (Learning)",
    "Candidate should be prepared to discuss learning timeline in interviews"
  ]
}"""

    def _build_tactical_prompt(
        self,
        resume_data: Dict,
        improvements: List[Dict],
        job_posting: Dict
    ) -> str:
        """Build prompt for tactical improvements"""
        prompt = "# TACTICAL RESUME IMPROVEMENT REQUEST\n\n"

        prompt += "## CURRENT RESUME\n"
        prompt += json.dumps(resume_data.get('sections', {}), indent=2)
        prompt += "\n\n"

        prompt += "## TARGET JOB\n"
        prompt += f"**Title:** {job_posting.get('job_title')}\n"
        prompt += f"**Required Skills:** {', '.join(job_posting.get('required_skills', []))}\n"
        prompt += f"**Key Responsibilities:** {', '.join(job_posting.get('responsibilities', [])[:5])}\n\n"

        prompt += "## SUGGESTED IMPROVEMENTS\n"
        for imp in improvements[:10]:  # Top 10
            prompt += f"- **{imp.get('section')}**: {imp.get('rationale')}\n"
            if imp.get('before'):
                prompt += f"  - Before: {imp['before']}\n"
            if imp.get('after'):
                prompt += f"  - After: {imp['after']}\n"
        prompt += "\n"

        prompt += "Apply these tactical improvements to generate an optimized resume. "
        prompt += "Remember: only make changes that are 100% truthful and verifiable. "
        prompt += "Return the result as JSON as specified in the system prompt."

        return prompt

    def _build_extrapolated_prompt(
        self,
        resume_data: Dict,
        tactical_version: Dict,
        analysis: Dict,
        job_posting: Dict
    ) -> str:
        """Build prompt for extrapolated version"""
        prompt = "# EXTRAPOLATED RESUME REQUEST\n\n"

        prompt += "## TACTICAL RESUME (CURRENT STATE)\n"
        prompt += json.dumps(tactical_version.get('sections', {}), indent=2)
        prompt += "\n\n"

        prompt += "## GAP ANALYSIS\n"

        # Exact match gaps
        exact_gaps = analysis.get('exact_match', {}).get('gaps', [])
        if exact_gaps:
            prompt += "**Missing Required Skills:**\n"
            for gap in exact_gaps[:10]:
                prompt += f"- {gap.get('skill')} (Impact: {gap.get('impact', 'unknown')})\n"
            prompt += "\n"

        # Transferable gaps
        transfer_gaps = analysis.get('transferable_match', {}).get('gaps', [])
        if transfer_gaps:
            prompt += "**Transferable Skill Gaps:**\n"
            for gap in transfer_gaps[:5]:
                prompt += f"- Need: {gap.get('skill')} | Has: {gap.get('closest_match')} | Learning curve: {gap.get('learning_curve')}\n"
            prompt += "\n"

        # Growth potential evidence
        growth = analysis.get('growth_potential', {})
        prompt += f"**Growth Potential:** {growth.get('score', 50)}/100\n"
        prompt += f"**Learning Speed:** {growth.get('learning_speed', 'unknown')}\n"
        if growth.get('evidence'):
            prompt += "**Evidence:** " + ", ".join(growth['evidence'][:3]) + "\n"
        prompt += "\n"

        prompt += "## TARGET JOB\n"
        prompt += f"**Title:** {job_posting.get('job_title')}\n"
        prompt += f"**Required Skills:** {', '.join(job_posting.get('required_skills', []))}\n\n"

        prompt += "Generate an extrapolated resume showing realistic 3-month growth trajectory. "
        prompt += "Mark all extrapolated items clearly and include confidence scores. "
        prompt += "Return as JSON as specified in the system prompt."

        return prompt

    def compute_diff(self, original: Dict, modified: Dict) -> List[Dict]:
        """
        Compute differences between original and modified resume

        Args:
            original: Original resume sections
            modified: Modified resume sections

        Returns:
            List of differences with before/after
        """
        diffs = []

        # Compare each section
        for section_name in modified.get('sections', {}).keys():
            original_section = original.get('sections', {}).get(section_name)
            modified_section = modified.get('sections', {}).get(section_name)

            if original_section != modified_section:
                diffs.append({
                    'section': section_name,
                    'before': original_section,
                    'after': modified_section,
                    'change_detected': True
                })

        return diffs
