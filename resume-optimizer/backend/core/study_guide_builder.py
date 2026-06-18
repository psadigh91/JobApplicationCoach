"""
Study Guide Builder - Generate personalized learning resources
Finds YouTube tutorials, courses, articles for skill gaps
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
import json
import re


class StudyGuideBuilder:
    """Build personalized study guides for skill gaps"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Claude API"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_study_guide(
        self,
        gaps: List[Dict],
        candidate_background: Dict,
        timeline: str = "3 months"
    ) -> Dict:
        """
        Generate comprehensive study guide

        Args:
            gaps: List of skill gaps from analysis
            candidate_background: Candidate's current skills/experience
            timeline: Learning timeline (default 3 months)

        Returns:
            Structured study guide with resources
        """
        prompt = self._build_study_guide_prompt(gaps, candidate_background, timeline)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.5,
            system=self._get_system_prompt(),
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
                "timeline": timeline,
                "skills": [],
                "resources": [],
                "raw_output": text
            }

    def _get_system_prompt(self) -> str:
        """System prompt for study guide generation"""
        return """You are a learning advisor helping candidates upskill efficiently. Your job is to create personalized study guides that:

1. Prioritize skills by impact (focus on required skills first)
2. Recommend high-quality, practical resources
3. Build on the candidate's existing knowledge
4. Provide realistic timelines
5. Include mix of resource types (videos, courses, docs, projects)

Resource credibility ratings:
- **High**: Official documentation, major platforms (Coursera, Udemy, Pluralsight), well-known creators
- **Medium**: Popular blogs, GitHub tutorials, community resources
- **Low**: Unknown sources, outdated content

Return JSON in this format:
{
  "timeline": "3 months",
  "total_hours_estimated": 120,
  "skills": [
    {
      "skill": "Kubernetes",
      "priority": "high|medium|low",
      "reason": "Required skill with high impact",
      "current_level": "none|beginner|intermediate",
      "target_level": "intermediate|advanced",
      "estimated_hours": 40,
      "learning_path": [
        {
          "phase": "Foundation",
          "duration": "2 weeks",
          "topics": ["Container orchestration basics", "K8s architecture"],
          "resources": [
            {
              "type": "video|course|documentation|tutorial|project",
              "title": "Kubernetes Tutorial for Beginners",
              "provider": "TechWorld with Nana",
              "url": "https://youtube.com/...",
              "duration": "3 hours",
              "credibility": "high|medium|low",
              "free": true
            }
          ]
        },
        {
          "phase": "Practice",
          "duration": "2 weeks",
          "topics": ["Deployments", "Services", "ConfigMaps"],
          "resources": [...]
        },
        {
          "phase": "Certification",
          "duration": "2 weeks",
          "topics": ["CKA exam prep"],
          "resources": [...]
        }
      ]
    }
  ],
  "weekly_plan": [
    {
      "week": 1,
      "focus": "Kubernetes foundations",
      "hours": 10,
      "deliverables": ["Complete intro course", "Set up local cluster"]
    }
  ],
  "project_suggestions": [
    {
      "name": "Deploy microservices app on K8s",
      "skills_demonstrated": ["Kubernetes", "Docker", "CI/CD"],
      "difficulty": "intermediate",
      "estimated_time": "1 week",
      "value": "Portfolio piece demonstrating deployment skills"
    }
  ]
}"""

    def _build_study_guide_prompt(
        self,
        gaps: List[Dict],
        candidate_background: Dict,
        timeline: str
    ) -> str:
        """Build prompt for study guide generation"""
        prompt = "# PERSONALIZED STUDY GUIDE REQUEST\n\n"

        prompt += f"## LEARNING TIMELINE\n{timeline}\n\n"

        prompt += "## SKILL GAPS TO ADDRESS\n"
        for gap in gaps:
            skill = gap.get('skill', 'Unknown')
            impact = gap.get('impact', 'medium')
            required = gap.get('required', False)
            prompt += f"- **{skill}** (Impact: {impact}, Required: {required})\n"
            if gap.get('closest_match'):
                prompt += f"  - Candidate has: {gap['closest_match']}\n"
        prompt += "\n"

        prompt += "## CANDIDATE BACKGROUND\n"
        skills = candidate_background.get('skills', [])
        if skills:
            prompt += f"**Current Skills:** {', '.join(skills[:20])}\n"

        experience = candidate_background.get('experience', [])
        if experience:
            prompt += f"**Experience:** {len(experience)} positions\n"

        learning_speed = candidate_background.get('learning_speed', 'unknown')
        prompt += f"**Learning Speed:** {learning_speed}\n\n"

        prompt += "Generate a personalized study guide focusing on high-impact skills. "
        prompt += "Include a mix of free and paid resources, prioritizing quality. "
        prompt += "Suggest practical projects to build portfolio. "
        prompt += "Return as JSON as specified in the system prompt."

        return prompt

    async def find_resources(
        self,
        skill: str,
        resource_types: List[str] = ["video", "course", "documentation"]
    ) -> List[Dict]:
        """
        Find specific resources for a skill

        Args:
            skill: Skill to find resources for
            resource_types: Types of resources to find

        Returns:
            List of resources
        """
        prompt = f"""Find the best learning resources for: **{skill}**

Resource types requested: {', '.join(resource_types)}

Return a JSON array of resources:
[
  {{
    "type": "video|course|documentation|tutorial",
    "title": "Resource title",
    "provider": "Provider name",
    "url": "URL (use example URLs if you don't know exact ones)",
    "duration": "Estimated time",
    "difficulty": "beginner|intermediate|advanced",
    "credibility": "high|medium|low",
    "free": true|false,
    "description": "Brief description"
  }}
]

Focus on well-known, high-quality resources. Include mix of free and paid options."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        try:
            json_match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                resources = json.loads(json_match.group(1))
            else:
                resources = json.loads(text)

            return resources

        except:
            return []

    def suggest_projects(
        self,
        target_skills: List[str],
        difficulty: str = "intermediate"
    ) -> List[Dict]:
        """
        Suggest portfolio projects

        Args:
            target_skills: Skills to demonstrate
            difficulty: Project difficulty level

        Returns:
            List of project suggestions
        """
        skills_str = ', '.join(target_skills)

        prompt = f"""Suggest 3-5 portfolio projects that demonstrate these skills: {skills_str}

Difficulty level: {difficulty}

Return JSON array:
[
  {{
    "name": "Project name",
    "description": "What the project does",
    "skills_demonstrated": ["skill1", "skill2"],
    "difficulty": "beginner|intermediate|advanced",
    "estimated_time": "1 week|2 weeks|1 month",
    "portfolio_value": "Why this impresses recruiters",
    "implementation_steps": [
      "Step 1: Set up...",
      "Step 2: Implement...",
      "Step 3: Deploy..."
    ],
    "example_repos": ["github.com/example/project"]
  }}
]

Focus on practical, impressive projects that can be completed in the given timeframe."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        try:
            json_match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                projects = json.loads(json_match.group(1))
            else:
                projects = json.loads(text)

            return projects

        except:
            return []
