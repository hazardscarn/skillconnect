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

class ResumeState(TypedDict):
    job_description: str
    resume_content: str
    current_stage: str
    education_score: float
    skills_score: float
    experience_score: float
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
        self.workflow.add_node("education", self.analyze_education)
        self.workflow.add_node("skills", self.analyze_skills)
        self.workflow.add_node("experience", self.analyze_experience)

        self.workflow.add_edge("education", "skills")
        self.workflow.add_edge("skills", "experience")
        self.workflow.add_edge("experience", END)

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

    def analyze_resume(self, job_description: str, resume_content: str) -> Dict:
        initial_state = ResumeState(
            job_description=job_description,
            resume_content=resume_content,
            current_stage="education",
            education_score=0.0,
            skills_score=0.0,
            experience_score=0.0,
            analysis_details={}
        )
        
        try:
            final_state = self.app.invoke(initial_state)
            
            weights = {
                "education": 0.25,
                "skills": 0.35,
                "experience": 0.40
            }
            
            total_score = (
                final_state["education_score"] * weights["education"] +
                final_state["skills_score"] * weights["skills"] +
                final_state["experience_score"] * weights["experience"]
            )

            print({
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
                    }
                },
                "summary": {
                    "education": final_state["analysis_details"]["education"]["explanation"],
                    "skills": final_state["analysis_details"]["skills"]["explanation"],
                    "experience": final_state["analysis_details"]["experience"]["explanation"]
                }
            })
            
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
                    }
                },
                "summary": {
                    "education": final_state["analysis_details"]["education"]["explanation"],
                    "skills": final_state["analysis_details"]["skills"]["explanation"],
                    "experience": final_state["analysis_details"]["experience"]["explanation"]
                }
            }
            
        except Exception as e:
            print(f"Error in analyze_resume: {str(e)}")
            print(f"Final state: {final_state}")
            raise