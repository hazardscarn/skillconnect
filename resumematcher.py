import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import re

class Match(BaseModel):
    section: str = Field(description="The matched section from the resume")
    requirement: str = Field(description="The requirement this section matches")
    color: str = Field(description="The color code for this requirement")
    confidence: float = Field(description="Confidence score of the match (0-1)")

class ResumeMatches(BaseModel):
    matches: List[Match] = Field(description="List of matching sections")

class SemanticMatcher:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
        
        self.matching_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume analyzer. Your task is to identify sections in a resume that match specific job requirements.

For each requirement, find the most relevant section in the resume that demonstrates that requirement.
Only match sections that genuinely demonstrate the requirement.

Response must be in this exact JSON format:
{{
    "matches": [
        {{
            "section": "exact text from resume that matches",
            "requirement": "the matching requirement",
            "color": "color code from the requirement",
            "confidence": confidence_score
        }}
    ]
}}

Rules:
1. Only extract sections that truly match the requirements
2. Include the exact text from the resume
3. Confidence score should be between 0 and 1
4. Don't force matches - if no good match exists, don't include it
5. Multiple requirements can match the same section if relevant
6. Sections should be complete, coherent pieces of text"""),
            ("human", """Analyze this resume:
{resume_content}

Against these requirements:
{requirements}

Find matching sections and return as JSON.""")
        ])

    def find_matches(self, resume_content: str, requirements: Dict) -> str:
        """Find matching sections in resume for each requirement"""
        try:
            # Get matches from LLM
            response = self.matching_prompt | self.llm
            result = response.invoke({
                "resume_content": resume_content,
                "requirements": json.dumps(requirements, indent=2)
            })
            
            # Parse and validate the response
            content = result.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            matches = ResumeMatches(**json.loads(content))
            
            # Apply highlights to the content
            return self.apply_highlights(resume_content, matches.model_dump()['matches'])
            
        except Exception as e:
            print(f"Error in find_matches: {str(e)}")
            return resume_content
    
    def apply_highlights(self, content: str, matches: List[Dict]) -> str:
        """Apply highlights to matched sections in the content"""
        highlights = []
        
        for match in matches:
            section = match['section']
            # Find the section in the content
            section_start = content.find(section)
            if section_start != -1:
                highlights.append({
                    'start': section_start,
                    'end': section_start + len(section),
                    'text': section,
                    'color': match['color'],
                    'requirement': match['requirement'],
                    'confidence': match['confidence']
                })
        
        # Sort highlights by start position in reverse order
        highlights.sort(key=lambda x: x['start'], reverse=True)
        
        # Apply highlights
        highlighted_content = content
        for highlight in highlights:
            tooltip = f"Matches: {highlight['requirement']} (Confidence: {highlight['confidence']:.0%})"
            highlighted_text = (
                f'<span style="background-color: {highlight["color"]}80; '
                f'padding: 2px 4px; border-radius: 3px; margin: 0 2px;" '
                f'title="{tooltip}">{highlight["text"]}</span>'
            )
            highlighted_content = (
                highlighted_content[:highlight['start']] +
                highlighted_text +
                highlighted_content[highlight['end']:]
            )
        
        return highlighted_content

def test_matcher():
    """Test function for the Semantic Matcher"""
    matcher = SemanticMatcher()
    
    # Test resume
    test_resume = """
    PROFESSIONAL EXPERIENCE
    
    Senior Financial Analyst | ABC Corp (2018-Present)
    - Led financial modeling and analysis for $50M portfolio
    - Developed and maintained complex Excel models for forecasting
    - Presented quarterly financial reports to executive team
    
    Financial Analyst | XYZ Inc (2015-2018)
    - Performed financial analysis and reporting
    - Created budgets and forecasts
    
    EDUCATION
    Bachelor of Science in Finance
    University of Example, 2015
    
    SKILLS
    - Advanced Excel and financial modeling
    - Financial reporting and analysis
    - Strong presentation skills
    """
    
    # Test requirements
    test_requirements = {
        "requirements": [
            {
                "responsibility": "5+ years financial analysis experience",
                "color": "#FF6B6B"
            },
            {
                "responsibility": "Advanced Excel and modeling skills",
                "color": "#45B7D1"
            },
            {
                "responsibility": "Bachelor's degree in Finance",
                "color": "#4ECDC4"
            }
        ]
    }
    
    # Test matching
    highlighted_content = matcher.find_matches(test_resume, test_requirements)
    print("\nHighlighted Resume Content:")
    print(highlighted_content)

if __name__ == "__main__":
    test_matcher()