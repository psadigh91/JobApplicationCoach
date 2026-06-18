"""
Skill Taxonomy - Normalize and categorize skills
Handles skill variations (React = React.js = ReactJS)
Maps transferable skills
"""

from typing import Dict, List, Set, Optional
import re


class SkillTaxonomy:
    """Skill normalization and taxonomy system"""

    # Canonical skill names with their variations
    SKILL_VARIATIONS = {
        'Python': ['python', 'python3', 'python 3', 'py'],
        'JavaScript': ['javascript', 'js', 'ecmascript', 'es6', 'es2015', 'node.js', 'nodejs'],
        'TypeScript': ['typescript', 'ts'],
        'React': ['react', 'react.js', 'reactjs', 'react js'],
        'React Native': ['react native', 'react-native', 'reactnative', 'rn'],
        'Vue': ['vue', 'vue.js', 'vuejs', 'vue js'],
        'Angular': ['angular', 'angularjs', 'angular.js', 'angular 2+'],
        'Node.js': ['node', 'node.js', 'nodejs', 'node js'],
        'Express': ['express', 'express.js', 'expressjs'],
        'Django': ['django'],
        'Flask': ['flask'],
        'FastAPI': ['fastapi', 'fast api'],
        'Spring': ['spring', 'spring boot', 'springboot'],
        'Java': ['java', 'java se', 'java ee'],
        'C++': ['c++', 'cpp', 'c plus plus'],
        'C#': ['c#', 'csharp', 'c sharp'],
        'Go': ['go', 'golang'],
        'Rust': ['rust'],
        'Ruby': ['ruby'],
        'Ruby on Rails': ['ruby on rails', 'rails', 'ror'],
        'PHP': ['php'],
        'Swift': ['swift'],
        'Kotlin': ['kotlin'],
        'SQL': ['sql', 'structured query language'],
        'PostgreSQL': ['postgresql', 'postgres', 'psql'],
        'MySQL': ['mysql', 'my sql'],
        'MongoDB': ['mongodb', 'mongo'],
        'Redis': ['redis'],
        'Docker': ['docker'],
        'Kubernetes': ['kubernetes', 'k8s', 'k8'],
        'AWS': ['aws', 'amazon web services'],
        'Azure': ['azure', 'microsoft azure'],
        'GCP': ['gcp', 'google cloud', 'google cloud platform'],
        'Git': ['git', 'github', 'gitlab', 'version control'],
        'CI/CD': ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment'],
        'REST API': ['rest', 'rest api', 'restful', 'rest apis'],
        'GraphQL': ['graphql', 'graph ql'],
        'Microservices': ['microservices', 'micro services', 'microservice architecture'],
        'Agile': ['agile', 'agile methodology', 'agile development'],
        'Scrum': ['scrum'],
        'Machine Learning': ['machine learning', 'ml'],
        'Deep Learning': ['deep learning', 'dl'],
        'TensorFlow': ['tensorflow', 'tensor flow'],
        'PyTorch': ['pytorch', 'torch'],
        'HTML': ['html', 'html5'],
        'CSS': ['css', 'css3'],
        'Sass': ['sass', 'scss'],
        'Tailwind': ['tailwind', 'tailwind css', 'tailwindcss'],
        'Bootstrap': ['bootstrap'],
        'Jest': ['jest'],
        'Pytest': ['pytest', 'py.test'],
        'JUnit': ['junit'],
        'Linux': ['linux', 'unix'],
        'Bash': ['bash', 'shell scripting', 'shell'],
    }

    # Skill categories
    SKILL_CATEGORIES = {
        'Programming Languages': [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#',
            'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin'
        ],
        'Frontend Frameworks': [
            'React', 'Vue', 'Angular', 'Svelte'
        ],
        'Backend Frameworks': [
            'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
            'Spring', 'Ruby on Rails'
        ],
        'Databases': [
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQL'
        ],
        'DevOps & Cloud': [
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD'
        ],
        'Version Control': [
            'Git', 'GitHub', 'GitLab'
        ],
        'Testing': [
            'Jest', 'Pytest', 'JUnit', 'Unit Testing', 'Integration Testing'
        ],
        'Methodologies': [
            'Agile', 'Scrum', 'REST API', 'GraphQL', 'Microservices'
        ],
        'AI/ML': [
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch'
        ],
        'Frontend Technologies': [
            'HTML', 'CSS', 'Sass', 'Tailwind', 'Bootstrap'
        ]
    }

    # Transferable skill mappings
    TRANSFERABLE_SKILLS = {
        'React': ['Vue', 'Angular', 'Svelte'],
        'Vue': ['React', 'Angular'],
        'Angular': ['React', 'Vue'],
        'Python': ['Ruby', 'JavaScript', 'Go'],
        'Java': ['C#', 'Kotlin', 'Go'],
        'JavaScript': ['TypeScript', 'Python'],
        'AWS': ['Azure', 'GCP'],
        'Azure': ['AWS', 'GCP'],
        'GCP': ['AWS', 'Azure'],
        'PostgreSQL': ['MySQL', 'SQL'],
        'MySQL': ['PostgreSQL', 'SQL'],
        'MongoDB': ['Redis', 'DynamoDB'],
        'Django': ['Flask', 'FastAPI', 'Ruby on Rails'],
        'Flask': ['Django', 'FastAPI', 'Express'],
        'Express': ['Flask', 'FastAPI'],
        'Docker': ['Kubernetes', 'Container technologies'],
    }

    def __init__(self):
        """Initialize skill taxonomy"""
        # Build reverse mapping (variation -> canonical)
        self.variation_to_canonical = {}
        for canonical, variations in self.SKILL_VARIATIONS.items():
            for variation in variations:
                self.variation_to_canonical[variation.lower()] = canonical

    def normalize_skill(self, skill: str) -> str:
        """
        Normalize a skill name to its canonical form

        Args:
            skill: Skill name (any variation)

        Returns:
            Canonical skill name
        """
        skill_lower = skill.lower().strip()

        # Check direct mapping
        if skill_lower in self.variation_to_canonical:
            return self.variation_to_canonical[skill_lower]

        # Check if it contains a known variation
        for variation, canonical in self.variation_to_canonical.items():
            if variation in skill_lower or skill_lower in variation:
                return canonical

        # Return original if no match (keep first letter capitalized)
        return skill.strip().capitalize()

    def normalize_skill_list(self, skills: List[str]) -> List[str]:
        """
        Normalize a list of skills

        Args:
            skills: List of skill names

        Returns:
            List of canonical skill names (deduplicated)
        """
        normalized = set()
        for skill in skills:
            canonical = self.normalize_skill(skill)
            normalized.add(canonical)

        return sorted(list(normalized))

    def categorize_skill(self, skill: str) -> Optional[str]:
        """
        Get category for a skill

        Args:
            skill: Skill name

        Returns:
            Category name or None
        """
        canonical = self.normalize_skill(skill)

        for category, skills in self.SKILL_CATEGORIES.items():
            if canonical in skills:
                return category

        return None

    def categorize_skill_list(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of skills

        Args:
            skills: List of skill names

        Returns:
            Dictionary mapping category -> skills
        """
        categorized = {category: [] for category in self.SKILL_CATEGORIES.keys()}
        categorized['Other'] = []

        for skill in skills:
            canonical = self.normalize_skill(skill)
            category = self.categorize_skill(canonical)

            if category:
                categorized[category].append(canonical)
            else:
                categorized['Other'].append(canonical)

        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}

    def find_transferable_skills(
        self,
        candidate_skills: List[str],
        required_skill: str
    ) -> List[Dict]:
        """
        Find transferable skills from candidate's skill set

        Args:
            candidate_skills: Skills candidate has
            required_skill: Required skill they lack

        Returns:
            List of transferable skills with relationship info
        """
        required_canonical = self.normalize_skill(required_skill)
        candidate_canonical = self.normalize_skill_list(candidate_skills)

        transferable = []

        # Check if candidate has the exact skill
        if required_canonical in candidate_canonical:
            return [{
                'from_skill': required_canonical,
                'to_skill': required_canonical,
                'relationship': 'exact_match',
                'transferability': 'perfect'
            }]

        # Check direct transferable mappings
        if required_canonical in self.TRANSFERABLE_SKILLS:
            for candidate_skill in candidate_canonical:
                if candidate_skill in self.TRANSFERABLE_SKILLS[required_canonical]:
                    transferable.append({
                        'from_skill': candidate_skill,
                        'to_skill': required_canonical,
                        'relationship': 'direct_transfer',
                        'transferability': 'high'
                    })

        # Check reverse mappings (candidate skill transfers to required)
        for candidate_skill in candidate_canonical:
            if candidate_skill in self.TRANSFERABLE_SKILLS:
                if required_canonical in self.TRANSFERABLE_SKILLS[candidate_skill]:
                    transferable.append({
                        'from_skill': candidate_skill,
                        'to_skill': required_canonical,
                        'relationship': 'adjacent_skill',
                        'transferability': 'medium-high'
                    })

        # Check if in same category
        if not transferable:
            required_category = self.categorize_skill(required_canonical)
            for candidate_skill in candidate_canonical:
                candidate_category = self.categorize_skill(candidate_skill)
                if required_category and candidate_category == required_category:
                    transferable.append({
                        'from_skill': candidate_skill,
                        'to_skill': required_canonical,
                        'relationship': 'same_category',
                        'transferability': 'medium',
                        'category': required_category
                    })

        return transferable

    def compare_skill_sets(
        self,
        candidate_skills: List[str],
        required_skills: List[str]
    ) -> Dict:
        """
        Compare candidate and required skill sets

        Args:
            candidate_skills: Candidate's skills
            required_skills: Required skills

        Returns:
            Comparison with matches, gaps, and transferable skills
        """
        candidate_normalized = set(self.normalize_skill_list(candidate_skills))
        required_normalized = set(self.normalize_skill_list(required_skills))

        # Exact matches
        exact_matches = candidate_normalized.intersection(required_normalized)

        # Gaps (missing required skills)
        gaps = required_normalized - candidate_normalized

        # For each gap, find transferable skills
        transferable_map = {}
        for gap_skill in gaps:
            transferable = self.find_transferable_skills(
                list(candidate_normalized),
                gap_skill
            )
            if transferable:
                transferable_map[gap_skill] = transferable

        # Extra skills (candidate has but not required)
        extra_skills = candidate_normalized - required_normalized

        return {
            'exact_matches': sorted(list(exact_matches)),
            'gaps': sorted(list(gaps)),
            'transferable_skills': transferable_map,
            'extra_skills': sorted(list(extra_skills)),
            'match_percentage': len(exact_matches) / len(required_normalized) * 100 if required_normalized else 0
        }

    def suggest_skill_keywords(self, skill: str) -> List[str]:
        """
        Get all keyword variations for a skill (useful for resume optimization)

        Args:
            skill: Skill name

        Returns:
            List of keyword variations
        """
        canonical = self.normalize_skill(skill)

        # Find all variations for this canonical name
        for canon, variations in self.SKILL_VARIATIONS.items():
            if canon == canonical:
                return variations

        return [skill.lower()]
