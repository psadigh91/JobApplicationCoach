"""
LinkedIn Scraper - Extract profile data from URL or PDF export
Supports URL scraping (with Playwright) and PDF fallback
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
import PyPDF2
import httpx
from bs4 import BeautifulSoup


class LinkedInScraper:
    """Scrape LinkedIn profiles via URL or parse PDF exports"""

    def __init__(self, timeout: int = 30):
        """
        Initialize scraper

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def scrape_profile(self, url: str) -> Dict:
        """
        Scrape LinkedIn profile from URL

        Args:
            url: LinkedIn profile URL

        Returns:
            Dictionary with profile data

        Note: LinkedIn actively blocks scraping. This is a best-effort implementation.
        In production, users should use PDF export fallback.
        """
        try:
            # Validate URL
            if not self._is_valid_linkedin_url(url):
                raise ValueError("Invalid LinkedIn URL")

            # Try to fetch profile page
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = await client.get(url, headers=headers, follow_redirects=True)

                if response.status_code != 200:
                    raise Exception(f"Failed to fetch profile: HTTP {response.status_code}")

                html = response.text

                # Check if we hit login wall
                if 'authwall' in html.lower() or 'login' in html.lower():
                    raise Exception("LinkedIn requires authentication - please use PDF export instead")

                # Extract profile sections
                profile_data = self._extract_profile_sections(html)
                return profile_data

        except Exception as e:
            # Return error structure
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "LinkedIn scraping failed. Please upload your LinkedIn profile as a PDF instead."
            }

    def parse_pdf_export(self, file_path: str) -> Dict:
        """
        Parse LinkedIn PDF export

        Args:
            file_path: Path to LinkedIn PDF export

        Returns:
            Dictionary with profile data
        """
        try:
            # Extract text from PDF
            text = self._extract_pdf_text(file_path)

            # Parse sections from PDF text
            profile_data = self._parse_pdf_sections(text)

            profile_data["success"] = True
            return profile_data

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "name": None,
                "headline": None,
                "summary": None,
                "experience": [],
                "education": [],
                "skills": [],
                "certifications": [],
                "recommendations": 0
            }

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Check if URL is a valid LinkedIn profile URL"""
        pattern = r'https?://(www\.)?linkedin\.com/(in|pub)/[\w-]+'
        return bool(re.match(pattern, url))

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _parse_pdf_sections(self, text: str) -> Dict:
        """Parse LinkedIn PDF export sections"""
        profile = {
            "name": self._extract_name(text),
            "headline": self._extract_headline(text),
            "summary": self._extract_summary_section(text, "Summary", "Experience"),
            "experience": self._extract_experience_section(text),
            "education": self._extract_education_section(text),
            "skills": self._extract_skills_section(text),
            "certifications": self._extract_certifications_section(text),
            "recommendations": self._count_recommendations(text)
        }
        return profile

    def _extract_profile_sections(self, html: str) -> Dict:
        """Extract profile sections from HTML (best effort)"""
        soup = BeautifulSoup(html, 'html.parser')

        profile = {
            "success": True,
            "name": None,
            "headline": None,
            "summary": None,
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "recommendations": 0
        }

        # Try to extract name
        name_tag = soup.find('h1', class_=re.compile('text-heading'))
        if name_tag:
            profile["name"] = name_tag.get_text(strip=True)

        # Try to extract headline
        headline_tag = soup.find('div', class_=re.compile('text-body'))
        if headline_tag:
            profile["headline"] = headline_tag.get_text(strip=True)

        # Note: Full extraction is complex due to LinkedIn's dynamic loading
        # This is a minimal implementation
        return profile

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from PDF text (usually first line)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Name is typically the first substantial line
            for line in lines[:5]:
                if len(line.split()) <= 5 and len(line) > 3:
                    return line
        return None

    def _extract_headline(self, text: str) -> Optional[str]:
        """Extract headline (line after name, before first section)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Headline is typically second or third line
        for i, line in enumerate(lines[1:6]):
            # Skip if it looks like a section header
            if not re.search(r'^(Experience|Education|Skills|Summary)', line, re.IGNORECASE):
                if len(line) > 10:
                    return line
        return None

    def _extract_summary_section(self, text: str, start_marker: str, end_marker: str) -> Optional[str]:
        """Extract text between two section markers"""
        pattern = f"{start_marker}(.*?){end_marker}"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_experience_section(self, text: str) -> List[Dict]:
        """Extract experience entries from LinkedIn PDF"""
        experiences = []

        # Find Experience section
        exp_match = re.search(r'Experience\s*(.*?)(?=Education|Skills|Certifications|$)', text, re.DOTALL | re.IGNORECASE)
        if not exp_match:
            return experiences

        exp_text = exp_match.group(1)

        # Split by common patterns (company names are often followed by dates)
        # Pattern: Title\nCompany · Employment Type\nDates · Duration\nLocation
        date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(Present|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})'

        # Split text into potential entries
        lines = exp_text.split('\n')
        current_entry = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line contains dates (indicates job entry)
            if re.search(date_pattern, line, re.IGNORECASE):
                if current_entry and current_entry.get('title'):
                    experiences.append(current_entry)
                current_entry = {
                    "title": "",
                    "company": "",
                    "dates": line,
                    "description": ""
                }
            elif not current_entry.get('title'):
                current_entry['title'] = line
            elif not current_entry.get('company'):
                # Company line often has · separator
                current_entry['company'] = line.split('·')[0].strip()
            elif current_entry:
                # Description lines
                if current_entry.get('description'):
                    current_entry['description'] += " " + line
                else:
                    current_entry['description'] = line

        if current_entry and current_entry.get('title'):
            experiences.append(current_entry)

        return experiences[:10]  # Limit to 10

    def _extract_education_section(self, text: str) -> List[Dict]:
        """Extract education entries"""
        education = []

        # Find Education section
        edu_match = re.search(r'Education\s*(.*?)(?=Skills|Certifications|Licenses|$)', text, re.DOTALL | re.IGNORECASE)
        if not edu_match:
            return education

        edu_text = edu_match.group(1)

        # Pattern: School\nDegree\nDates
        lines = edu_text.split('\n')
        current_entry = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for year pattern (indicates dates)
            if re.search(r'\d{4}', line):
                if current_entry.get('school'):
                    current_entry['dates'] = line
                    education.append(current_entry)
                    current_entry = {}
            elif not current_entry.get('school'):
                current_entry['school'] = line
            elif not current_entry.get('degree'):
                current_entry['degree'] = line

        if current_entry.get('school'):
            education.append(current_entry)

        return education

    def _extract_skills_section(self, text: str) -> List[str]:
        """Extract skills list"""
        skills = []

        # Find Skills section
        skills_match = re.search(r'Skills\s*(.*?)(?=Certifications|Licenses|Recommendations|$)', text, re.DOTALL | re.IGNORECASE)
        if not skills_match:
            return skills

        skills_text = skills_match.group(1)

        # Skills are usually one per line or comma-separated
        lines = skills_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 2 and len(line) < 100:
                # Remove endorsement counts
                skill = re.sub(r'\s*•\s*\d+.*$', '', line).strip()
                if skill:
                    skills.append(skill)

        return skills[:50]  # Limit to 50

    def _extract_certifications_section(self, text: str) -> List[Dict]:
        """Extract certifications"""
        certifications = []

        # Find Certifications section
        cert_match = re.search(r'(Certifications?|Licenses?)\s*(.*?)(?=Skills|Recommendations|$)', text, re.DOTALL | re.IGNORECASE)
        if not cert_match:
            return certifications

        cert_text = cert_match.group(2)

        lines = cert_text.split('\n')
        current_cert = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for issuer pattern (often has "Issued")
            if 'issued' in line.lower():
                if current_cert.get('name'):
                    certifications.append(current_cert)
                current_cert = {
                    "name": "",
                    "issuer": line.split('Issued')[0].strip(),
                    "date": line
                }
            elif not current_cert.get('name'):
                current_cert['name'] = line

        if current_cert.get('name'):
            certifications.append(current_cert)

        return certifications[:20]

    def _count_recommendations(self, text: str) -> int:
        """Count number of recommendations"""
        # Look for "Recommendations" section
        rec_match = re.search(r'Recommendations.*?(\d+)', text, re.IGNORECASE)
        if rec_match:
            try:
                return int(rec_match.group(1))
            except:
                pass
        return 0
