from typing import TypedDict, Dict, Annotated,Optional
from pydantic import BaseModel, Field, field_validator
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import operator
from functools import reduce
from model_manager import ModelManager

# Pydantic models for structured outputs
class EducationDetails(BaseModel):
    """Detailed scores and explanations for education assessment"""
    degree_relevance: float = Field(description="Score for degree relevance")
    education_level: float = Field(description="Score for education level match")
    academic_achievements: float = Field(description="Score for academic achievements")
    certifications: float = Field(description="Score for relevant certifications")
    explanation: str = Field(description="Detailed explanation of education analysis")

    @field_validator('degree_relevance', 'education_level', 'academic_achievements', 'certifications')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class SkillsDetails(BaseModel):
    """Detailed scores and explanations for skills assessment"""
    technical_skills: float = Field(description="Score for technical skills match")
    soft_skills: float = Field(description="Score for soft skills match")
    tools_tech: float = Field(description="Score for tools and technologies")
    domain_expertise: float = Field(description="Score for domain expertise")
    explanation: str = Field(description="Detailed explanation of skills analysis")

    @field_validator('technical_skills', 'soft_skills', 'tools_tech', 'domain_expertise')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class ExperienceDetails(BaseModel):
    """Detailed scores and explanations for experience assessment"""
    years_experience: float = Field(description="Score for years of experience")
    role_relevance: float = Field(description="Score for role relevance")
    industry_fit: float = Field(description="Score for industry fit")
    achievements: float = Field(description="Score for achievements")
    explanation: str = Field(description="Detailed explanation of experience analysis")

    @field_validator('years_experience', 'role_relevance', 'industry_fit', 'achievements')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class ToolsMatchDetails(BaseModel):
    """Detailed scores and explanations for tools/technology assessment"""
    required_tools_proficiency: float = Field(description="Score for required tools proficiency")
    tool_experience_years: float = Field(description="Score for years of experience with tools")
    tool_diversity: float = Field(description="Score for range of tools known")
    tool_certifications: float = Field(description="Score for tool-specific certifications")
    explanation: str = Field(description="Detailed explanation of tools analysis")

    @field_validator('required_tools_proficiency', 'tool_experience_years', 'tool_diversity', 'tool_certifications')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class IndustryMatchDetails(BaseModel):
    """Detailed scores and explanations for industry fit assessment"""
    industry_experience: float = Field(description="Score for relevant industry experience")
    industry_knowledge: float = Field(description="Score for industry-specific knowledge")
    industry_projects: float = Field(description="Score for industry projects completed")
    industry_network: float = Field(description="Score for industry connections/networking")
    explanation: str = Field(description="Detailed explanation of industry analysis")

    @field_validator('industry_experience', 'industry_knowledge', 'industry_projects', 'industry_network')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class RoleMatchDetails(BaseModel):
    """Detailed scores and explanations for role requirements match"""
    role_responsibilities: float = Field(description="Score for matching role responsibilities")
    leadership_requirements: float = Field(description="Score for leadership experience if required")
    project_management: float = Field(description="Score for project management experience")
    team_collaboration: float = Field(description="Score for team collaboration experience")
    explanation: str = Field(description="Detailed explanation of role match analysis")

    @field_validator('role_responsibilities', 'leadership_requirements', 'project_management', 'team_collaboration')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

class PreferencesMatchDetails(BaseModel):
    """Detailed scores and explanations for additional preferences match"""
    work_style: float = Field(description="Score for work style compatibility")
    location_match: float = Field(description="Score for location preferences")
    culture_fit: float = Field(description="Score for cultural fit indicators")
    growth_potential: float = Field(description="Score for growth/learning potential")
    explanation: str = Field(description="Detailed explanation of preferences analysis")

    @field_validator('work_style', 'location_match', 'culture_fit', 'growth_potential')
    def validate_score(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Score must be between 0 and 100")
        return v

def max_reducer(a: float, b: float) -> float:
    """Binary reducer to take maximum of two values"""
    return max(a, b)

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Binary reducer to merge two dictionaries"""
    return {**dict1, **dict2}

class ResumeState(TypedDict):
    """State definition with proper annotations for concurrent updates"""
    job_description: str
    resume_content: str
    education_score: Annotated[float, max_reducer]
    skills_score: Annotated[float, max_reducer]
    experience_score: Annotated[float, max_reducer]
    tools_score: Annotated[float, max_reducer]
    industry_score: Annotated[float, max_reducer]
    role_score: Annotated[float, max_reducer]
    preferences_score: Annotated[float, max_reducer]
    analysis_details: Annotated[Dict, merge_dicts]
    total_input_tokens: Annotated[int, operator.add]
    total_output_tokens: Annotated[int, operator.add]
    final_analysis: dict
    weights: Dict[str, float]

class SequentialResumeAnalysisAgent:
    def __init__(self, model_id: Optional[str] = None):
        """Initialize agent with specified model or default model"""
        self.model_manager = ModelManager()
        self.model_id = model_id or self.model_manager.get_default_model_id()
        self.llm = self.model_manager.initialize_model(self.model_id)

        # Initialize workflow
        self.workflow = StateGraph(ResumeState)
        
        # Add all analysis nodes
        self.workflow.add_node("analyze_education", self.analyze_education)
        self.workflow.add_node("analyze_skills", self.analyze_skills)
        self.workflow.add_node("analyze_experience", self.analyze_experience)
        self.workflow.add_node("analyze_tools", self.analyze_tools)
        self.workflow.add_node("analyze_industry", self.analyze_industry)
        self.workflow.add_node("analyze_role", self.analyze_role)
        self.workflow.add_node("analyze_preferences", self.analyze_preferences)
        self.workflow.add_node("aggregate_results", self.aggregate_results)

        # Set up sequential execution paths
        self.workflow.add_edge(START, "analyze_education")
        self.workflow.add_edge("analyze_education", "analyze_skills")
        self.workflow.add_edge("analyze_skills", "analyze_experience")
        self.workflow.add_edge("analyze_experience", "analyze_tools")
        self.workflow.add_edge("analyze_tools", "analyze_industry")
        self.workflow.add_edge("analyze_industry", "analyze_role")
        self.workflow.add_edge("analyze_role", "analyze_preferences")
        self.workflow.add_edge("analyze_preferences", "aggregate_results")
        self.workflow.add_edge("aggregate_results", END)
        
        # Compile workflow
        self.app = self.workflow.compile()

        # Compile workflow
        self.app = self.workflow.compile()
    
    
    def get_model_info(self) -> Dict:
        """Get information about the currently used model"""
        return {
            "model_id": self.model_id,
            "name": self.model_manager.models_config[self.model_id]["name"],
            "description": self.model_manager.get_model_description(self.model_id),
            "pricing": self.model_manager.get_model_pricing(self.model_id)
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count based on word count"""
        return int(len(text.split()) * 0.9)

    def analyze_education(self, state: ResumeState):
        """Analyze educational qualifications"""
        structured_llm = self.llm.with_structured_output(EducationDetails)
        
        system_message = """You are a resume analyzer specializing in educational qualifications. 
        Analyze the resume and provide scores and detailed explanations for educational components."""
        
        human_message = """Analyze these educational qualifications:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Degree relevance to the position
           - Education level match with requirements
           - Academic achievements
           - Relevant certifications
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.degree_relevance,
            output.education_level,
            output.academic_achievements,
            output.certifications
        ]
        education_score = sum(scores) / len(scores)

        return {
            "education_score": education_score,
            "analysis_details": {"education": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_skills(self, state: ResumeState):
        """Analyze skills"""
        structured_llm = self.llm.with_structured_output(SkillsDetails)
        
        system_message = """You are a resume analyzer specializing in skills assessment."""
        
        human_message = """Analyze these skills:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Technical skills match
           - Soft skills match
           - Tools and technologies proficiency
           - Domain expertise
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.technical_skills,
            output.soft_skills,
            output.tools_tech,
            output.domain_expertise
        ]
        skills_score = sum(scores) / len(scores)

        return {
            "skills_score": skills_score,
            "analysis_details": {"skills": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_experience(self, state: ResumeState):
        """Analyze experience"""
        structured_llm = self.llm.with_structured_output(ExperienceDetails)
        
        system_message = """You are a resume analyzer specializing in work experience assessment."""
        
        human_message = """Analyze this work experience:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Years of experience relevance
           - Role relevance
           - Industry fit
           - Notable achievements
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.years_experience,
            output.role_relevance,
            output.industry_fit,
            output.achievements
        ]
        experience_score = sum(scores) / len(scores)

        return {
            "experience_score": experience_score,
            "analysis_details": {"experience": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_tools(self, state: ResumeState):
        """Analyze tools proficiency"""
        structured_llm = self.llm.with_structured_output(ToolsMatchDetails)
        
        system_message = """You are a resume analyzer specializing in tools and technology assessment."""
        
        human_message = """Analyze the tools match:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Required tools proficiency
           - Years of experience with tools
           - Range of tools known
           - Tool certifications
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.required_tools_proficiency,
            output.tool_experience_years,
            output.tool_diversity,
            output.tool_certifications
        ]
        tools_score = sum(scores) / len(scores)

        return {
            "tools_score": tools_score,
            "analysis_details": {"tools": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_industry(self, state: ResumeState):
        """Analyze industry fit"""
        structured_llm = self.llm.with_structured_output(IndustryMatchDetails)
        
        system_message = """You are a resume analyzer specializing in industry assessment."""
        
        human_message = """Analyze the industry match:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Industry experience
           - Industry knowledge
           - Industry projects
           - Industry networking
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.industry_experience,output.industry_experience,
            output.industry_knowledge,
            output.industry_projects,
            output.industry_network
        ]
        industry_score = sum(scores) / len(scores)

        return {
            "industry_score": industry_score,
            "analysis_details": {"industry": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_role(self, state: ResumeState):
        """Analyze role match"""
        structured_llm = self.llm.with_structured_output(RoleMatchDetails)
        
        system_message = """You are a resume analyzer specializing in role requirements."""
        
        human_message = """Analyze the role match:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Role responsibilities
           - Leadership requirements
           - Project management
           - Team collaboration
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.role_responsibilities,
            output.leadership_requirements,
            output.project_management,
            output.team_collaboration
        ]
        role_score = sum(scores) / len(scores)

        return {
            "role_score": role_score,
            "analysis_details": {"role": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def analyze_preferences(self, state: ResumeState):
        """Analyze preferences match"""
        structured_llm = self.llm.with_structured_output(PreferencesMatchDetails)
        
        system_message = """You are a resume analyzer specializing in preferences assessment."""
        
        human_message = """Analyze the preferences match:
        Job Description: {job_description}
        Resume Content: {resume_content}
        Provide:
        1. Scores (0-100) for:
           - Work style compatibility
           - Location preferences match
           - Cultural fit indicators
           - Growth potential
        2. A detailed explanation of your analysis"""

        formatted_message = system_message + human_message.format(
            job_description=state["job_description"],
            resume_content=state["resume_content"]
        )
        input_tokens = self.estimate_tokens(formatted_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        output_tokens = self.estimate_tokens(str(output.model_dump()))
        scores = [
            output.work_style,
            output.location_match,
            output.culture_fit,
            output.growth_potential
        ]
        preferences_score = sum(scores) / len(scores)

        return {
            "preferences_score": preferences_score,
            "analysis_details": {"preferences": output.model_dump()},
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens
        }

    def aggregate_results(self, state: ResumeState):
        """Aggregate results from all analyses"""
        # Get weights from state
        weights = state["weights"]
        
        # Calculate weighted average for total score
        weighted_sum = 0.0
        available_weight = 0.0

        for component, weight in weights.items():
            score_key = f"{component}_score"
            if score_key in state and state[score_key] is not None:
                # Convert percentage to decimal for calculation
                score = state[score_key] / 100.0  # Convert percentage to decimal
                weighted_sum += score * weight
                available_weight += weight

        # Calculate final score as percentage
        total_score = (weighted_sum / available_weight * 100) if available_weight > 0 else 0.0

        # Include weights in the final analysis
        final_analysis = {
            "total_score": total_score,
            "component_scores": {
                component: {
                    "score": state[f"{component}_score"],
                    "weight": weights[component],  # Include weight in output
                    "details": state["analysis_details"].get(component, {})
                }
                for component in weights.keys()
                if f"{component}_score" in state
            },
            "summary": {
                component: state["analysis_details"].get(component, {}).get("explanation", "")
                for component in weights.keys()
                if component in state["analysis_details"]
            },
            "weights_used": weights,  # Include the weights used in analysis
            "token_usage": {
                "input_tokens": state["total_input_tokens"],
                "output_tokens": state["total_output_tokens"]
            }
        }

        return {"final_analysis": final_analysis}

    def analyze_resume(self, job_description: str, resume_content: str, weights: Optional[Dict[str, float]] = None) -> dict:
        """Main method to analyze a resume against a job description"""
        # Use provided weights or default weights
        default_weights = {
            "education": 0.15,
            "skills": 0.20,
            "experience": 0.20,
            "tools": 0.15,
            "industry": 0.10,
            "role": 0.15,
            "preferences": 0.05
        }
        
        analysis_weights = weights if weights is not None else default_weights
        
        # Validate weights
        if abs(sum(analysis_weights.values()) - 1.0) > 0.0001:
            raise ValueError("Weights must sum to 1.0")
        
        initial_state = ResumeState(
            job_description=job_description,
            resume_content=resume_content,
            education_score=0.0,
            skills_score=0.0,
            experience_score=0.0,
            tools_score=0.0,
            industry_score=0.0,
            role_score=0.0,
            preferences_score=0.0,
            analysis_details={},
            total_input_tokens=0,
            total_output_tokens=0,
            final_analysis={},
            weights=analysis_weights  # Add the weights to the initial state
        )

        try:
            final_state = self.app.invoke(initial_state)
            return final_state["final_analysis"]
        except Exception as e:
            print(f"Error in analyze_resume: {str(e)}")
            raise
    

    def validate_weights(self, weights: Dict[str, float]) -> bool:
        """
        Validate that weights are properly formatted and sum to 1.0
        """
        required_components = {
            "education", "skills", "experience", "tools", 
            "industry", "role", "preferences"
        }
        
        # Check all components are present
        if not all(component in weights for component in required_components):
            raise ValueError("Missing required weight components")
        
        # Check all weights are between 0 and 1
        if not all(0 <= weight <= 1 for weight in weights.values()):
            raise ValueError("All weights must be between 0 and 1")
        
        # Check sum is 1.0
        if abs(sum(weights.values()) - 1.0) > 0.0001:
            raise ValueError("Weights must sum to 1.0")
        
        return True
    
# if __name__ == "__main__":
#     # Example usage
#     agent = ResumeAnalysisAgent()
    
#     # Sample job description and resume content
#     job_description = """
#     Senior Software Engineer position requiring 5+ years of Python experience,
#     strong background in machine learning, and excellent communication skills.
#     """
    
#     resume_content = """
#     Software Engineer with 6 years of Python development experience.
#     Led machine learning projects and collaborated with cross-functional teams.
#     """
    
#     # Analyze resume
#     try:
#         results = agent.analyze_resume(job_description, resume_content)
#         print("Analysis Results:")
#         print(f"Total Score: {results['total_score']:.2f}%")
#         print("\nComponent Scores:")
#         for component, data in results['component_scores'].items():
#             print(f"{component.title()}: {data['score']:.2f}%")
#     except Exception as e:
#         print(f"Error during analysis: {str(e)}")