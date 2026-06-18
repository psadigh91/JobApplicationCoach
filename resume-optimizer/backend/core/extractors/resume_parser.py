"""
Resume Parser - Extract structured data from PDF/DOCX resumes
Supports PDF (PyPDF2) and DOCX (python-docx) formats
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
import PyPDF2
from docx import Document


class ResumeParser:
    """Parse resumes and extract structured information"""

    # Common section headers (case-insensitive regex patterns)
    SECTION_PATTERNS = {
        'contact': r'(contact|personal\s+information)',
        'summary': r'(summary|objective|profile|about|professional\s+summary)',
        'experience': r'(experience|work\s+history|employment|professional\s+experience)',
        'education': r'(education|academic|qualification)',
        'skills': r'(skills|technical\s+skills|competencies|expertise)',
        'certifications': r'(certifications?|licenses?|credentials)'
    }

    # Email regex
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Phone regex (US and international formats)
    PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    # Date patterns
    DATE_PATTERN = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|(\d{1,2}/\d{4})|(\d{4})\s*-\s*(Present|Current|Now|\d{4})'

    def parse(self, file_path: str, mime_type: str) -> Dict:
        """
        Parse resume file and return structured data

        Args:
            file_path: Path to resume file
            mime_type: MIME type ('application/pdf' or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        Returns:
            Dictionary with structured resume data
        """
        try:
            # Extract raw text based on file type
            if mime_type == 'application/pdf':
                raw_text = self._extract_text_pdf(file_path)
            elif 'wordprocessingml' in mime_type or mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                raw_text = self._extract_text_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")

            # Parse sections
            sections = self._parse_sections(raw_text)

            # Calculate metadata
            word_count = len(raw_text.split())
            format_detected = 'pdf' if mime_type == 'application/pdf' else 'docx'

            # Simple confidence score based on sections found
            sections_found = sum(1 for v in sections.values() if v)
            parsing_confidence = min(100, int((sections_found / 6) * 100))

            return {
                "raw_text": raw_text,
                "sections": sections,
                "metadata": {
                    "word_count": word_count,
                    "format_detected": format_detected,
                    "parsing_confidence": parsing_confidence
                }
            }
        except Exception as e:
            return {
                "raw_text": "",
                "sections": {},
                "metadata": {
                    "word_count": 0,
                    "format_detected": "unknown",
                    "parsing_confidence": 0,
                    "error": str(e)
                }
            }

    def _extract_text_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
        return text.strip()

    def _extract_text_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
        return text.strip()

    def _parse_sections(self, raw_text: str) -> Dict:
        """Parse raw text into structured sections"""
        sections = {
            "contact": self._extract_contact_info(raw_text),
            "summary": self._extract_summary(raw_text),
            "experience": self._extract_experience(raw_text),
            "education": self._extract_education(raw_text),
            "skills": self._extract_skills(raw_text),
            "certifications": self._extract_certifications(raw_text)
        }
        return sections

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text"""
        contact = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None
        }

        # Extract email
        email_match = re.search(self.EMAIL_PATTERN, text)
        if email_match:
            contact["email"] = email_match.group()

        # Extract phone
        phone_match = re.search(self.PHONE_PATTERN, text)
        if phone_match:
            contact["phone"] = phone_match.group()

        # Extract name (assume first line or first line before email)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Name is usually in the first few lines
            for line in lines[:5]:
                # Skip lines that look like section headers
                if not re.search(r'(experience|education|skills|summary|profile)', line, re.IGNORECASE):
                    if len(line.split()) <= 5 and len(line) > 3:  # Reasonable name length
                        contact["name"] = line
                        break

        # Extract location (city, state pattern)
        location_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b'
        location_match = re.search(location_pattern, text)
        if location_match:
            contact["location"] = location_match.group()

        return contact

    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract professional summary/objective"""
        pattern = self.SECTION_PATTERNS['summary']
        section = self._extract_section_content(text, pattern)
        return section if section else None

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience entries"""
        pattern = self.SECTION_PATTERNS['experience']
        section_text = self._extract_section_content(text, pattern)

        if not section_text:
            return []

        experiences = []

        # Split by date patterns (indicates new job entry)
        date_splits = re.split(f'({self.DATE_PATTERN})', section_text, flags=re.IGNORECASE)

        # Reconstruct entries
        current_entry = []
        for part in date_splits:
            if part and part.strip():
                current_entry.append(part.strip())
                # If we have enough content, save as entry
                if len(current_entry) >= 3:
                    entry_text = ' '.join(current_entry)
                    lines = entry_text.split('\n')

                    experience = {
                        "title": lines[0] if len(lines) > 0 else "",
                        "company": lines[1] if len(lines) > 1 else "",
                        "dates": self._find_dates_in_text(' '.join(lines[:3])),
                        "bullets": [line.strip() for line in lines[2:] if line.strip() and len(line.strip()) > 10]
                    }
                    experiences.append(experience)
                    current_entry = []

        return experiences[:10]  # Limit to 10 most recent

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education entries"""
        pattern = self.SECTION_PATTERNS['education']
        section_text = self._extract_section_content(text, pattern)

        if not section_text:
            return []

        education = []

        # Common degree patterns
        degree_pattern = r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|Associate|Doctorate)'

        lines = section_text.split('\n')
        current_entry = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line contains a degree
            if re.search(degree_pattern, line, re.IGNORECASE):
                if current_entry:
                    education.append(current_entry)
                current_entry = {
                    "degree": line,
                    "school": "",
                    "dates": ""
                }
            elif current_entry and not current_entry.get("school"):
                current_entry["school"] = line
            elif current_entry:
                dates = self._find_dates_in_text(line)
                if dates:
                    current_entry["dates"] = dates

        if current_entry:
            education.append(current_entry)

        return education

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills list"""
        pattern = self.SECTION_PATTERNS['skills']
        section_text = self._extract_section_content(text, pattern)

        if not section_text:
            return []

        skills = []

        # Skills are often comma-separated or bullet-pointed
        lines = section_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet points
            line = re.sub(r'^[•\-\*]\s*', '', line)

            # Split by commas or semicolons
            if ',' in line or ';' in line:
                parts = re.split(r'[,;]', line)
                skills.extend([p.strip() for p in parts if p.strip()])
            else:
                skills.append(line)

        return skills[:50]  # Limit to 50 skills

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        pattern = self.SECTION_PATTERNS['certifications']
        section_text = self._extract_section_content(text, pattern)

        if not section_text:
            return []

        certifications = []
        lines = section_text.split('\n')

        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                # Remove bullet points
                line = re.sub(r'^[•\-\*]\s*', '', line)
                certifications.append(line)

        return certifications[:20]  # Limit to 20

    def _extract_section_content(self, text: str, section_pattern: str) -> str:
        """Extract content between section header and next section"""
        # Find section start
        match = re.search(f'^{section_pattern}\\s*$', text, re.MULTILINE | re.IGNORECASE)
        if not match:
            # Try with colon
            match = re.search(f'^{section_pattern}\\s*:', text, re.MULTILINE | re.IGNORECASE)

        if not match:
            return ""

        start_pos = match.end()

        # Find next section (any other section header)
        all_patterns = '|'.join(self.SECTION_PATTERNS.values())
        next_section = re.search(f'^({all_patterns})\\s*:?\\s*$', text[start_pos:], re.MULTILINE | re.IGNORECASE)

        if next_section:
            end_pos = start_pos + next_section.start()
            return text[start_pos:end_pos].strip()
        else:
            return text[start_pos:].strip()

    def _find_dates_in_text(self, text: str) -> str:
        """Find and return date ranges in text"""
        matches = re.findall(self.DATE_PATTERN, text, re.IGNORECASE)
        if matches:
            # Flatten tuple results and join
            dates = []
            for match in matches[:2]:  # Take first 2 date matches
                if isinstance(match, tuple):
                    dates.extend([m for m in match if m])
                else:
                    dates.append(match)
            return ' - '.join(dates[:2])
        return ""
