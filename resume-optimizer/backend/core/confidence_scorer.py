"""
Confidence Scorer - Calculate 0-100 confidence scores for analysis findings
Uses exact match, semantic similarity, and inference rules
"""

from typing import Dict, List, Optional
import re


class ConfidenceScorer:
    """Calculate confidence scores for analysis findings"""

    # Confidence modifiers
    EXACT_MATCH_CONFIDENCE = 95
    SEMANTIC_MATCH_CONFIDENCE = 75
    INFERRED_MATCH_CONFIDENCE = 50
    NO_EVIDENCE_CONFIDENCE = 20

    # Transferability confidence by relationship
    TRANSFERABILITY_SCORES = {
        'identical': 95,      # React === React
        'version': 90,        # Python 2 → Python 3
        'direct': 85,         # React → React Native
        'adjacent': 70,       # React → Vue
        'same_family': 60,    # Java → Kotlin
        'similar_domain': 45, # Frontend → Backend (same language)
        'distant': 25         # Unrelated skills
    }

    def score_exact_match(
        self,
        required_skill: str,
        candidate_skills: List[str],
        evidence_text: Optional[str] = None
    ) -> Dict:
        """
        Score confidence for exact skill match

        Args:
            required_skill: Required skill from job posting
            candidate_skills: List of candidate's skills
            evidence_text: Optional text evidence (resume/LinkedIn)

        Returns:
            Dictionary with confidence score and reasoning
        """
        required_lower = required_skill.lower().strip()

        # Check for exact matches
        for skill in candidate_skills:
            skill_lower = skill.lower().strip()

            # Exact match
            if skill_lower == required_lower:
                return {
                    'confidence': self.EXACT_MATCH_CONFIDENCE,
                    'match_type': 'exact',
                    'matched_skill': skill,
                    'reasoning': f"Exact match found: '{skill}'"
                }

            # Case-insensitive substring match
            if required_lower in skill_lower or skill_lower in required_lower:
                return {
                    'confidence': self.EXACT_MATCH_CONFIDENCE - 5,
                    'match_type': 'substring',
                    'matched_skill': skill,
                    'reasoning': f"Strong match: '{skill}' matches '{required_skill}'"
                }

        # Check evidence text if provided
        if evidence_text:
            if self._skill_mentioned_in_text(required_skill, evidence_text):
                return {
                    'confidence': self.SEMANTIC_MATCH_CONFIDENCE,
                    'match_type': 'text_evidence',
                    'matched_skill': required_skill,
                    'reasoning': f"'{required_skill}' found in resume/profile text"
                }

        # No match found
        return {
            'confidence': self.NO_EVIDENCE_CONFIDENCE,
            'match_type': 'none',
            'matched_skill': None,
            'reasoning': f"No evidence of '{required_skill}' found"
        }

    def score_transferable_match(
        self,
        required_skill: str,
        candidate_skills: List[str]
    ) -> Dict:
        """
        Score confidence for transferable skill match

        Args:
            required_skill: Required skill
            candidate_skills: Candidate's skills

        Returns:
            Confidence score with transferability analysis
        """
        required_lower = required_skill.lower().strip()

        # Check for transferable skills
        best_match = None
        best_confidence = 0

        for candidate_skill in candidate_skills:
            candidate_lower = candidate_skill.lower().strip()

            # Determine transferability relationship
            relationship = self._determine_skill_relationship(required_lower, candidate_lower)
            confidence = self.TRANSFERABILITY_SCORES.get(relationship, 20)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = {
                    'confidence': confidence,
                    'from_skill': candidate_skill,
                    'to_skill': required_skill,
                    'relationship': relationship,
                    'reasoning': self._explain_transferability(candidate_skill, required_skill, relationship)
                }

        if best_match:
            return best_match

        return {
            'confidence': 15,
            'from_skill': None,
            'to_skill': required_skill,
            'relationship': 'none',
            'reasoning': f"No transferable skills found for '{required_skill}'"
        }

    def score_growth_potential(
        self,
        candidate_profile: Dict,
        missing_skills: List[str],
        evidence: List[str]
    ) -> Dict:
        """
        Score growth potential based on learning history

        Args:
            candidate_profile: Full candidate data
            missing_skills: Skills candidate lacks
            evidence: Evidence of learning ability

        Returns:
            Growth potential score with reasoning
        """
        base_score = 50
        modifiers = []

        # Check for self-taught skills
        if evidence:
            self_taught_count = sum(1 for e in evidence if 'self-taught' in e.lower() or 'learned' in e.lower())
            if self_taught_count > 0:
                base_score += 15
                modifiers.append(f"+15: {self_taught_count} self-taught skills")

        # Check for diverse skill set (indicates adaptability)
        all_skills = candidate_profile.get('resume_data', {}).get('sections', {}).get('skills', [])
        if len(all_skills) > 15:
            base_score += 10
            modifiers.append("+10: Broad skill set (15+ skills)")

        # Check for recent learning (education, certifications)
        recent_learning = self._check_recent_learning(candidate_profile)
        if recent_learning:
            base_score += 10
            modifiers.append("+10: Recent learning activity")

        # Penalize if missing many required skills
        if len(missing_skills) > 5:
            base_score -= 15
            modifiers.append(f"-15: Many missing skills ({len(missing_skills)})")

        # Cap at 100
        final_score = min(100, max(0, base_score))

        return {
            'confidence': 70,  # We're moderately confident in growth assessments
            'score': final_score,
            'modifiers': modifiers,
            'reasoning': f"Growth potential score: {final_score}/100. " + " ".join(modifiers)
        }

    def score_culture_fit(
        self,
        company_values: List[str],
        candidate_evidence: List[str]
    ) -> Dict:
        """
        Score culture fit confidence

        Args:
            company_values: Company values/culture keywords
            candidate_evidence: Evidence from resume/LinkedIn

        Returns:
            Culture fit confidence score
        """
        if not company_values:
            return {
                'confidence': 30,
                'score': 50,
                'reasoning': "Insufficient company culture data for assessment"
            }

        matches = []
        for value in company_values:
            for evidence in candidate_evidence:
                if value.lower() in evidence.lower():
                    matches.append((value, evidence))

        match_ratio = len(matches) / len(company_values) if company_values else 0
        score = int(match_ratio * 100)

        # Confidence is higher when we have clear matches or clear misses
        confidence = 50 + (abs(score - 50) * 0.6)  # Higher confidence at extremes

        return {
            'confidence': int(confidence),
            'score': score,
            'matches': matches,
            'reasoning': f"Found {len(matches)}/{len(company_values)} culture value matches"
        }

    def _skill_mentioned_in_text(self, skill: str, text: str) -> bool:
        """Check if skill is mentioned in text"""
        skill_lower = skill.lower()
        text_lower = text.lower()

        # Exact word boundary match
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        return bool(re.search(pattern, text_lower))

    def _determine_skill_relationship(self, skill1: str, skill2: str) -> str:
        """
        Determine relationship between two skills

        Returns: 'identical', 'version', 'direct', 'adjacent', 'same_family', 'similar_domain', 'distant'
        """
        # Identical (accounting for common variations)
        if self._normalize_skill(skill1) == self._normalize_skill(skill2):
            return 'identical'

        # Version differences (Python 2/3, React 16/17)
        if self._is_version_variant(skill1, skill2):
            return 'version'

        # Direct relationships (React → React Native)
        if self._is_direct_relationship(skill1, skill2):
            return 'direct'

        # Adjacent (React → Vue, Python → Java)
        if self._is_adjacent_skill(skill1, skill2):
            return 'adjacent'

        # Same family (AWS → Azure, PostgreSQL → MySQL)
        if self._is_same_family(skill1, skill2):
            return 'same_family'

        # Similar domain (Frontend → Backend)
        if self._is_similar_domain(skill1, skill2):
            return 'similar_domain'

        return 'distant'

    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        # Remove common variations
        normalized = skill.lower().strip()
        normalized = normalized.replace('.js', 'js')
        normalized = normalized.replace('-', '')
        normalized = normalized.replace(' ', '')
        return normalized

    def _is_version_variant(self, skill1: str, skill2: str) -> bool:
        """Check if skills are version variants"""
        # Remove version numbers
        base1 = re.sub(r'\d+', '', skill1).strip()
        base2 = re.sub(r'\d+', '', skill2).strip()
        return self._normalize_skill(base1) == self._normalize_skill(base2)

    def _is_direct_relationship(self, skill1: str, skill2: str) -> bool:
        """Check for direct skill relationships"""
        direct_pairs = [
            ('react', 'react native'),
            ('javascript', 'typescript'),
            ('python', 'django'),
            ('python', 'flask'),
            ('java', 'spring'),
            ('node', 'express')
        ]

        norm1 = self._normalize_skill(skill1)
        norm2 = self._normalize_skill(skill2)

        for pair in direct_pairs:
            if (norm1 in pair and norm2 in pair):
                return True

        return False

    def _is_adjacent_skill(self, skill1: str, skill2: str) -> bool:
        """Check for adjacent skills"""
        adjacent_groups = [
            ['react', 'vue', 'angular', 'svelte'],
            ['python', 'java', 'javascript', 'ruby', 'go'],
            ['aws', 'azure', 'gcp'],
            ['postgresql', 'mysql', 'mongodb'],
            ['docker', 'kubernetes']
        ]

        norm1 = self._normalize_skill(skill1)
        norm2 = self._normalize_skill(skill2)

        for group in adjacent_groups:
            if any(norm1 in s or s in norm1 for s in group) and \
               any(norm2 in s or s in norm2 for s in group):
                return True

        return False

    def _is_same_family(self, skill1: str, skill2: str) -> bool:
        """Check if skills are in same family"""
        families = [
            ['sql', 'database', 'postgresql', 'mysql', 'oracle'],
            ['cloud', 'aws', 'azure', 'gcp'],
            ['frontend', 'react', 'vue', 'angular', 'html', 'css'],
            ['backend', 'node', 'express', 'django', 'flask', 'spring']
        ]

        norm1 = self._normalize_skill(skill1)
        norm2 = self._normalize_skill(skill2)

        for family in families:
            in_family_1 = any(norm1 in s or s in norm1 for s in family)
            in_family_2 = any(norm2 in s or s in norm2 for s in family)
            if in_family_1 and in_family_2:
                return True

        return False

    def _is_similar_domain(self, skill1: str, skill2: str) -> bool:
        """Check if skills are in similar domains"""
        # Both are programming languages
        languages = ['python', 'java', 'javascript', 'ruby', 'go', 'rust', 'c++', 'c#']
        norm1 = self._normalize_skill(skill1)
        norm2 = self._normalize_skill(skill2)

        lang1 = any(lang in norm1 for lang in languages)
        lang2 = any(lang in norm2 for lang in languages)

        return lang1 and lang2

    def _explain_transferability(self, from_skill: str, to_skill: str, relationship: str) -> str:
        """Explain why skills are transferable"""
        explanations = {
            'identical': f"'{from_skill}' is the same as '{to_skill}'",
            'version': f"'{from_skill}' is a version variant of '{to_skill}' - highly transferable",
            'direct': f"'{from_skill}' directly relates to '{to_skill}' - strong transferability",
            'adjacent': f"'{from_skill}' is adjacent to '{to_skill}' - good transferability",
            'same_family': f"'{from_skill}' is in the same family as '{to_skill}' - moderate transferability",
            'similar_domain': f"'{from_skill}' is in a similar domain to '{to_skill}' - some transferability",
            'distant': f"'{from_skill}' is distantly related to '{to_skill}' - limited transferability"
        }
        return explanations.get(relationship, "Unknown relationship")

    def _check_recent_learning(self, candidate_profile: Dict) -> bool:
        """Check for recent learning activity"""
        # Check certifications
        certs = candidate_profile.get('resume_data', {}).get('sections', {}).get('certifications', [])
        if certs:
            # If any certification mentions recent years (2023, 2024, 2025, 2026)
            recent_years = ['2023', '2024', '2025', '2026']
            for cert in certs:
                if any(year in str(cert) for year in recent_years):
                    return True

        return False
