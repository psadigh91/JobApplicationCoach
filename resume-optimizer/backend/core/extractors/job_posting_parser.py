"""
Job Posting Parser - Extract structured data from job posting text
Identifies required vs preferred skills, responsibilities, qualifications
"""

import re
from typing import Dict, List, Set


class JobPostingParser:
    """Parse job posting text and extract structured information"""

    # Section header patterns
    SECTION_PATTERNS = {
        'responsibilities': r'(responsibilities|duties|what you\'ll do|role description|job description|about the role)',
        'required': r'(requirements?|required|qualifications?|must have|essential|you have|minimum qualifications?)',
        'preferred': r'(preferred|nice to have|bonus|plus|ideal candidate|you might also have)',
        'education': r'(education|degree|qualification)',
        'benefits': r'(benefits|perks|what we offer|compensation|package)',
        'about_company': r'(about us|who we are|our company|our mission)'
    }

    # Common skill keywords
    TECH_SKILLS = [
        'python', 'java', 'javascript', 'typescript', 'react', 'node',
        'angular', 'vue', 'sql', 'nosql', 'mongodb', 'postgresql',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git',
        'agile', 'scrum', 'ci/cd', 'rest', 'api', 'microservices'
    ]

    # Experience patterns
    EXPERIENCE_PATTERN = r'(\d+)\+?\s*(years?|yrs?)\s*(of\s*)?(experience|exp\.?)'

    def parse(self, text: str, source: str = 'paste') -> Dict:
        """
        Parse job posting text

        Args:
            text: Job posting text
            source: Source of text ('paste', 'url', 'file')

        Returns:
            Dictionary with structured job posting data
        """
        try:
            # Extract basic info
            job_title = self._extract_job_title(text)
            company = self._extract_company(text)
            location = self._extract_location(text)

            # Extract sections
            responsibilities = self._extract_section(text, 'responsibilities')
            required_section = self._extract_section(text, 'required')
            preferred_section = self._extract_section(text, 'preferred')
            benefits_section = self._extract_section(text, 'benefits')

            # Parse skills from sections
            required_skills = self._extract_skills(required_section)
            preferred_skills = self._extract_skills(preferred_section)

            # Extract experience requirements
            required_experience = self._extract_experience(required_section)

            # Extract education requirements
            education_requirements = self._extract_education(text)

            # Extract responsibilities as bullet points
            responsibilities_list = self._extract_bullets(responsibilities)

            # Extract nice-to-haves
            nice_to_have = self._extract_bullets(preferred_section)

            # Extract benefits
            benefits = self._extract_bullets(benefits_section)

            # Build keyword sets
            keywords = {
                "required": required_skills,
                "preferred": preferred_skills
            }

            return {
                "job_title": job_title,
                "company": company,
                "location": location,
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "required_experience": required_experience,
                "education_requirements": education_requirements,
                "responsibilities": responsibilities_list,
                "nice_to_have": nice_to_have,
                "benefits": benefits,
                "keywords": keywords,
                "full_text": text
            }

        except Exception as e:
            return {
                "job_title": None,
                "company": None,
                "location": None,
                "required_skills": [],
                "preferred_skills": [],
                "required_experience": None,
                "education_requirements": [],
                "responsibilities": [],
                "nice_to_have": [],
                "benefits": [],
                "keywords": {"required": [], "preferred": []},
                "full_text": text,
                "error": str(e)
            }

    def _extract_job_title(self, text: str) -> str:
        """Extract job title (usually in first few lines or marked)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Look for common job title patterns
        for line in lines[:10]:
            # Skip if it's clearly not a title
            if len(line) > 100 or len(line) < 5:
                continue

            # Common job title keywords
            if re.search(r'\b(engineer|developer|manager|analyst|designer|scientist|architect|lead|director|specialist|coordinator)\b', line, re.IGNORECASE):
                return line

        # Fallback: first substantial line
        if lines:
            return lines[0]

        return "Unknown Position"

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name"""
        # Look for "Company:" or "at Company" patterns
        match = re.search(r'(?:company|employer):\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        match = re.search(r'\bat\s+([A-Z][A-Za-z\s&.,]+?)(?:\n|$)', text)
        if match:
            return match.group(1).strip()

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract job location"""
        # Common location patterns
        patterns = [
            r'(?:location|based in|office):\s*([^\n]+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b',  # City, ST
            r'\b(Remote|Hybrid|On-site)\b'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_section(self, text: str, section_type: str) -> str:
        """Extract content of a specific section"""
        pattern = self.SECTION_PATTERNS.get(section_type)
        if not pattern:
            return ""

        # Find section header
        match = re.search(f'({pattern})\\s*:?', text, re.IGNORECASE | re.MULTILINE)
        if not match:
            return ""

        start_pos = match.end()

        # Find next section (any other section header)
        all_patterns = '|'.join(self.SECTION_PATTERNS.values())
        next_match = re.search(f'({all_patterns})\\s*:?', text[start_pos:], re.IGNORECASE | re.MULTILINE)

        if next_match:
            end_pos = start_pos + next_match.start()
            return text[start_pos:end_pos].strip()
        else:
            # Take next 500 chars if no section found
            return text[start_pos:start_pos + 500].strip()

    def _extract_skills(self, section_text: str) -> List[str]:
        """Extract skills from section text"""
        if not section_text:
            return []

        skills = set()

        # Look for tech skills
        text_lower = section_text.lower()
        for skill in self.TECH_SKILLS:
            if skill in text_lower:
                skills.add(skill.capitalize())

        # Look for bullet points (often list skills)
        bullets = self._extract_bullets(section_text)
        for bullet in bullets:
            # Extract capitalized words/phrases (often skills)
            # Pattern: Capitalized word or acronym
            matches = re.findall(r'\b[A-Z][A-Za-z+#]*(?:\.[A-Za-z]+)?\b', bullet)
            for match in matches:
                if len(match) > 1:  # Skip single letters
                    skills.add(match)

        return sorted(list(skills))[:30]  # Limit to 30 most relevant

    def _extract_experience(self, section_text: str) -> Optional[str]:
        """Extract required years of experience"""
        if not section_text:
            return None

        match = re.search(self.EXPERIENCE_PATTERN, section_text, re.IGNORECASE)
        if match:
            years = match.group(1)
            return f"{years}+ years"

        return None

    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements"""
        education = []

        # Common degree patterns
        degree_patterns = [
            r'\b(Bachelor\'?s?|B\.?S\.?|B\.?A\.?)\b.*?(?:degree|in)?\s*([A-Z][A-Za-z\s]+)?',
            r'\b(Master\'?s?|M\.?S\.?|M\.?A\.?|MBA)\b.*?(?:degree|in)?\s*([A-Z][A-Za-z\s]+)?',
            r'\b(PhD|Ph\.?D\.?|Doctorate)\b.*?(?:in)?\s*([A-Z][A-Za-z\s]+)?',
            r'\b(Associate\'?s?)\b.*?(?:degree)?'
        ]

        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                degree = match.group(0).strip()
                if degree and len(degree) < 100:
                    education.append(degree)

        return education[:5]  # Limit to 5

    def _extract_bullets(self, section_text: str) -> List[str]:
        """Extract bullet points from section"""
        if not section_text:
            return []

        bullets = []

        # Split by newlines
        lines = section_text.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Remove bullet point markers
            line = re.sub(r'^[•\-\*\d+\.)]\s*', '', line)

            # Keep lines with substance
            if len(line) > 15:
                bullets.append(line)

        return bullets[:20]  # Limit to 20 bullets
