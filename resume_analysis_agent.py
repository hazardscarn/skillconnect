from typing import TypedDict, Dict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv

# Pydantic models for structured outputs
class EducationDetails(BaseModel):
    """Detailed scores and explanations for education assessment"""
    degree_relevance: float = Field(..., ge=0, le=100, description="Score for degree relevance")
    education_level: float = Field(..., ge=0, le=100, description="Score for education level match")
    academic_achievements: float = Field(..., ge=0, le=100, description="Score for academic achievements")
    certifications: float = Field(..., ge=0, le=100, description="Score for relevant certifications")
    explanation: str = Field(..., description="Detailed explanation of education analysis")

class SkillsDetails(BaseModel):
    """Detailed scores and explanations for skills assessment"""
    technical_skills: float = Field(..., ge=0, le=100, description="Score for technical skills match")
    soft_skills: float = Field(..., ge=0, le=100, description="Score for soft skills match")
    tools_tech: float = Field(..., ge=0, le=100, description="Score for tools and technologies")
    domain_expertise: float = Field(..., ge=0, le=100, description="Score for domain expertise")
    explanation: str = Field(..., description="Detailed explanation of skills analysis")

class ExperienceDetails(BaseModel):
    """Detailed scores and explanations for experience assessment"""
    years_experience: float = Field(..., ge=0, le=100, description="Score for years of experience")
    role_relevance: float = Field(..., ge=0, le=100, description="Score for role relevance")
    industry_fit: float = Field(..., ge=0, le=100, description="Score for industry fit")
    achievements: float = Field(..., ge=0, le=100, description="Score for achievements")
    explanation: str = Field(..., description="Detailed explanation of experience analysis")

class ToolsMatchDetails(BaseModel):
    """Detailed scores and explanations for tools/technology assessment"""
    required_tools_proficiency: float = Field(..., ge=0, le=100, description="Score for required tools proficiency")
    tool_experience_years: float = Field(..., ge=0, le=100, description="Score for years of experience with tools")
    tool_diversity: float = Field(..., ge=0, le=100, description="Score for range of tools known")
    tool_certifications: float = Field(..., ge=0, le=100, description="Score for tool-specific certifications")
    explanation: str = Field(..., description="Detailed explanation of tools analysis")

class IndustryMatchDetails(BaseModel):
    """Detailed scores and explanations for industry fit assessment"""
    industry_experience: float = Field(..., ge=0, le=100, description="Score for relevant industry experience")
    industry_knowledge: float = Field(..., ge=0, le=100, description="Score for industry-specific knowledge")
    industry_projects: float = Field(..., ge=0, le=100, description="Score for industry projects completed")
    industry_network: float = Field(..., ge=0, le=100, description="Score for industry connections/networking")
    explanation: str = Field(..., description="Detailed explanation of industry analysis")

class RoleMatchDetails(BaseModel):
    """Detailed scores and explanations for role requirements match"""
    role_responsibilities: float = Field(..., ge=0, le=100, description="Score for matching role responsibilities")
    leadership_requirements: float = Field(..., ge=0, le=100, description="Score for leadership experience if required")
    project_management: float = Field(..., ge=0, le=100, description="Score for project management experience")
    team_collaboration: float = Field(..., ge=0, le=100, description="Score for team collaboration experience")
    explanation: str = Field(..., description="Detailed explanation of role match analysis")

class PreferencesMatchDetails(BaseModel):
    """Detailed scores and explanations for additional preferences match"""
    work_style: float = Field(..., ge=0, le=100, description="Score for work style compatibility")
    location_match: float = Field(..., ge=0, le=100, description="Score for location preferences")
    culture_fit: float = Field(..., ge=0, le=100, description="Score for cultural fit indicators")
    growth_potential: float = Field(..., ge=0, le=100, description="Score for growth/learning potential")
    explanation: str = Field(..., description="Detailed explanation of preferences analysis")

# Extended ResumeState to include new components
class ResumeState(TypedDict):
    job_description: str
    resume_content: str
    current_stage: str
    education_score: float
    skills_score: float
    experience_score: float
    tools_score: float
    industry_score: float
    role_score: float
    preferences_score: float
    analysis_details: Dict

class ResumeAnalysisAgent:
    def __init__(self):
        load_dotenv()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        self.workflow = StateGraph(ResumeState)
        
        # Add all analysis nodes
        self.workflow.add_node("education", self.analyze_education)
        self.workflow.add_node("skills", self.analyze_skills)
        self.workflow.add_node("experience", self.analyze_experience)
        self.workflow.add_node("tools", self.analyze_tools)
        self.workflow.add_node("industry", self.analyze_industry)
        self.workflow.add_node("role", self.analyze_role)
        self.workflow.add_node("preferences", self.analyze_preferences)

        # Define workflow sequence
        self.workflow.add_edge("education", "skills")
        self.workflow.add_edge("skills", "experience")
        self.workflow.add_edge("experience", "tools")
        self.workflow.add_edge("tools", "industry")
        self.workflow.add_edge("industry", "role")
        self.workflow.add_edge("role", "preferences")
        self.workflow.add_edge("preferences", END)

        self.workflow.set_entry_point("education")
        self.app = self.workflow.compile()

    def analyze_education(self, state: ResumeState) -> ResumeState:
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.degree_relevance,
            output.education_level,
            output.academic_achievements,
            output.certifications
        ]
        state["education_score"] = sum(scores) / len(scores)
        state["analysis_details"]["education"] = output.model_dump()
        return state

    def analyze_skills(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(SkillsDetails)
        
        system_message = """You are a resume analyzer specializing in skills assessment.
        Analyze the resume and provide scores and detailed explanations for skill components."""
        
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.technical_skills,
            output.soft_skills,
            output.tools_tech,
            output.domain_expertise
        ]
        state["skills_score"] = sum(scores) / len(scores)
        state["analysis_details"]["skills"] = output.model_dump()
        return state

    def analyze_experience(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(ExperienceDetails)
        
        system_message = """You are a resume analyzer specializing in work experience assessment.
        Analyze the resume and provide scores and detailed explanations for experience components."""
        
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.years_experience,
            output.role_relevance,
            output.industry_fit,
            output.achievements
        ]
        state["experience_score"] = sum(scores) / len(scores)
        state["analysis_details"]["experience"] = output.model_dump()
        return state

    def analyze_tools(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(ToolsMatchDetails)
        
        system_message = """You are a resume analyzer specializing in tools and technology assessment.
        Analyze the resume and provide scores and detailed explanations for tools/technology proficiency."""
        
        human_message = """Analyze the tools and technology match:

        Job Description: {job_description}
        
        Resume Content: {resume_content}
        
        Provide:
        1. Scores (0-100) for:
           - Required tools proficiency
           - Years of experience with tools
           - Range of tools known
           - Tool-specific certifications
        2. A detailed explanation of your analysis"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.required_tools_proficiency,
            output.tool_experience_years,
            output.tool_diversity,
            output.tool_certifications
        ]
        state["tools_score"] = sum(scores) / len(scores)
        state["analysis_details"]["tools"] = output.model_dump()
        return state

    def analyze_industry(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(IndustryMatchDetails)
        
        system_message = """You are a resume analyzer specializing in industry fit assessment.
        Analyze the resume and provide scores and detailed explanations for industry match."""
        
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.industry_experience,
            output.industry_knowledge,
            output.industry_projects,
            output.industry_network
        ]
        state["industry_score"] = sum(scores) / len(scores)
        state["analysis_details"]["industry"] = output.model_dump()
        return state

    def analyze_role(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(RoleMatchDetails)
        
        system_message = """You are a resume analyzer specializing in role requirements assessment.
        Analyze the resume and provide scores and detailed explanations for role match."""
        
        human_message = """Analyze the role match:

        Job Description: {job_description}
        
        Resume Content: {resume_content}
        
        Provide:
        1. Scores (0-100) for:
           - Role responsibilities match
           - Leadership requirements
           - Project management experience
           - Team collaboration
        2. A detailed explanation of your analysis"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.role_responsibilities,
            output.leadership_requirements,
            output.project_management,
            output.team_collaboration
        ]
        state["role_score"] = sum(scores) / len(scores)
        state["analysis_details"]["role"] = output.model_dump()
        return state

    def analyze_preferences(self, state: ResumeState) -> ResumeState:
        structured_llm = self.llm.with_structured_output(PreferencesMatchDetails)
        
        system_message = """You are a resume analyzer specializing in additional preferences assessment.
        Analyze the resume and provide scores and detailed explanations for preferences match."""
        
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

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])

        result = prompt | structured_llm
        output = result.invoke({
            "job_description": state["job_description"],
            "resume_content": state["resume_content"]
        })

        scores = [
            output.work_style,
            output.location_match,
            output.culture_fit,
            output.growth_potential
        ]
        state["preferences_score"] = sum(scores) / len(scores)
        state["analysis_details"]["preferences"] = output.model_dump()
        return state

    def analyze_resume(self, job_description: str, resume_content: str) -> Dict:
        initial_state = ResumeState(
            job_description=job_description,
            resume_content=resume_content,
            current_stage="education",
            education_score=0.0,
            skills_score=0.0,
            experience_score=0.0,
            tools_score=0.0,
            industry_score=0.0,
            role_score=0.0,
            preferences_score=0.0,
            analysis_details={}
        )
        
        try:
            final_state = self.app.invoke(initial_state)
            
            weights = {
                "education": 0.15,
                "skills": 0.20,
                "experience": 0.20,
                "tools": 0.15,
                "industry": 0.10,
                "role": 0.15,
                "preferences": 0.05
            }
            
            total_score = (
                final_state["education_score"] * weights["education"] +
                final_state["skills_score"] * weights["skills"] +
                final_state["experience_score"] * weights["experience"] +
                final_state["tools_score"] * weights["tools"] +
                final_state["industry_score"] * weights["industry"] +
                final_state["role_score"] * weights["role"] +
                final_state["preferences_score"] * weights["preferences"]
            )

            return {
                "total_score": total_score,
                "component_scores": {
                    "education": {
                        "score": final_state["education_score"],
                        "details": final_state["analysis_details"]["education"]
                    },
                    "skills": {
                        "score": final_state["skills_score"],
                        "details": final_state["analysis_details"]["skills"]
                    },
                    "experience": {
                        "score": final_state["experience_score"],
                        "details": final_state["analysis_details"]["experience"]
                    },
                    "tools": {
                        "score": final_state["tools_score"],
                        "details": final_state["analysis_details"]["tools"]
                    },
                    "industry": {
                        "score": final_state["industry_score"],
                        "details": final_state["analysis_details"]["industry"]
                    },
                    "role": {
                        "score": final_state["role_score"],
                        "details": final_state["analysis_details"]["role"]
                    },
                    "preferences": {
                        "score": final_state["preferences_score"],
                        "details": final_state["analysis_details"]["preferences"]
                    }
                },
                "summary": {
                    "education": final_state["analysis_details"]["education"]["explanation"],
                    "skills": final_state["analysis_details"]["skills"]["explanation"],
                    "experience": final_state["analysis_details"]["experience"]["explanation"],
                    "tools": final_state["analysis_details"]["tools"]["explanation"],
                    "industry": final_state["analysis_details"]["industry"]["explanation"],
                    "role": final_state["analysis_details"]["role"]["explanation"],
                    "preferences": final_state["analysis_details"]["preferences"]["explanation"]
                }
            }
            
        except Exception as e:
            print(f"Error in analyze_resume: {str(e)}")
            raise




