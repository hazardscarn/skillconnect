import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import re

class Requirement(BaseModel):
    responsibility: str = Field(description="The specific job responsibility or requirement")
    color: str = Field(description="The hex color code for highlighting this requirement")

class Requirements(BaseModel):
    requirements: List[Requirement] = Field(description="List of job requirements with their colors")

class JDAnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1  # Reduced temperature for more consistent output
        )
        
        # Predefined colors for different types of responsibilities
        self.colors = [
            "#FF6B6B",  # Red - Experience
            "#4ECDC4",  # Teal - Education
            "#45B7D1",  # Blue - Technical Skills
            "#96CEB4",  # Green - Domain Knowledge
            "#FFD93D",  # Yellow - Soft Skills
        ]
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a requirements analyzer. Your task is to extract 4-5 key requirements from a job description.
IMPORTANT: You must respond ONLY with a JSON object in the EXACT format shown below.
Do not include any other text or explanations.

Required JSON Format:
{{
    "requirements": [
        {{
            "responsibility": "requirement text (max 10 words)",
            "color": "color_code"
        }}
    ]
}}

Rules:
1. Extract exactly 4-5 key requirements
2. Each requirement must be under 10 words
3. Assign these specific colors based on requirement type:
   - Experience requirements: "#FF6B6B"
   - Education requirements: "#4ECDC4"
   - Technical skills: "#45B7D1"
   - Domain knowledge: "#96CEB4"
   - Soft skills: "#FFD93D"
4. ONLY output valid JSON, nothing else"""),
            ("human", "Extract 4-5 key requirements from this job description as JSON: {job_description}")
        ])
        
    def analyze_jd(self, job_description: str) -> Dict:
        """Analyze job description and return structured requirements with colors"""
        try:
            # Get response from LLM
            response = self.analysis_prompt | self.llm
            result = response.invoke({"job_description": job_description})
            
            # Extract content and clean any potential prefixes/suffixes
            content = result.content
            # Try to find JSON content between curly braces
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            # Parse and validate JSON
            parsed_result = json.loads(content)
            validated_reqs = Requirements(**parsed_result)
            
            # Ensure we have 4-5 requirements
            if len(validated_reqs.requirements) < 4:
                raise ValueError("Not enough requirements extracted")
                
            return validated_reqs.model_dump()
            
        except Exception as e:
            print(f"Error in analyze_jd: {str(e)}")
            # Return default requirements using all colors
            return {
                "requirements": [
                    {
                        "responsibility": "5+ years relevant experience",
                        "color": "#FF6B6B"
                    },
                    {
                        "responsibility": "Bachelor's degree required",
                        "color": "#4ECDC4"
                    },
                    {
                        "responsibility": "Technical expertise needed",
                        "color": "#45B7D1"
                    },
                    {
                        "responsibility": "Domain knowledge required",
                        "color": "#96CEB4"
                    }
                ]
            }
            
    def highlight_matches(self, resume_content: str, requirements: Dict) -> str:
        """Highlight matching requirements in resume content with corresponding colors"""
        highlighted_content = resume_content
        highlights = []
        
        try:
            # Preprocess resume content for better matching
            processed_content = resume_content.lower()
            
            for req in requirements["requirements"]:
                responsibility = req["responsibility"].lower()
                color = req["color"]
                
                # Create variations of the requirement
                base_words = [word for word in responsibility.split() if len(word) > 3]
                
                # Add years variations if present
                years_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)'
                years_match = re.search(years_pattern, responsibility)
                if years_match:
                    base_words.append(years_match.group(1))
                
                # Create patterns for matching
                patterns = [
                    r'\b' + re.escape(word) + r'\b' for word in base_words
                ]
                
                # Find matches
                for pattern in patterns:
                    for match in re.finditer(pattern, processed_content):
                        start, end = match.span()
                        original_text = resume_content[start:end]
                        highlights.append({
                            'start': start,
                            'end': end,
                            'text': original_text,
                            'color': color,
                            'requirement': responsibility
                        })
            
            # Sort and apply highlights
            highlights.sort(key=lambda x: x['start'], reverse=True)
            
            for highlight in highlights:
                highlighted_text = (
                    f'<span style="background-color: {highlight["color"]}80; '
                    f'padding: 2px 4px; border-radius: 3px; margin: 0 2px;" '
                    f'title="{highlight["requirement"]}">{highlight["text"]}</span>'
                )
                highlighted_content = (
                    highlighted_content[:highlight['start']] +
                    highlighted_text +
                    highlighted_content[highlight['end']:]
                )
            
        except Exception as e:
            print(f"Error in highlight_matches: {str(e)}")
            return resume_content
        
        return highlighted_content

def test_agent():
    """Test function for the JD Analysis Agent"""
    agent = JDAnalysisAgent()
    
    # Test job description
    test_jd = """
    Senior Financial Analyst Position
    
    Requirements:
    - 5+ years of experience in financial analysis
    - Bachelor's degree in Finance or Accounting required
    - Advanced Excel and financial modeling skills
    - Strong knowledge of financial reporting and forecasting
    - Excellent communication and presentation abilities
    """
    
    # Analyze JD
    requirements = agent.analyze_jd(test_jd)
    print("\nAnalyzed Requirements:")
    print(json.dumps(requirements, indent=2))
    
    # Test resume content
    test_resume = """
    Experienced Financial Analyst with 7 years of expertise in financial modeling
    and analysis. Bachelor's degree in Finance from XYZ University.
    Advanced proficiency in Excel and financial forecasting.
    Strong communication skills with proven ability to present complex financial concepts.
    """
    
    # Test highlighting
    highlighted_content = agent.highlight_matches(test_resume, requirements)
    print("\nHighlighted Resume Content:")
    print(highlighted_content)

if __name__ == "__main__":
    test_agent()