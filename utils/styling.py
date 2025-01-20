import streamlit as st
import re

def get_base_css():
    return """
    <style>
    /* Override Streamlit's default theme */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Text Area and Input Styling */
    .stTextArea textarea,
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    
    /* Select Box Styling */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* Button Styling */
    .stButton button {
        background-color: #3B82F6 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    .stDownloadButton button {
        background-color: #FFFFFF !important;
        color: #3B82F6 !important;
        border: 1px solid #3B82F6 !important;
    }
    
    /* Container Styling */
    .search-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin: 1rem 0;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #3B82F6, #60A5FA);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Feature Cards */
    .feature-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    .getting-started-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin: 0.5rem;
    }
    
    /* Results Styling */
    .result-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .match-score {
        background-color: #EBF5FF;
        color: #3B82F6;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 500;
    }
    
    /* Requirements Section */
    .requirements-container {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin: 1rem 0;
    }
    
    .requirement-tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        margin: 4px;
        color: white;
        font-weight: 500;
    }
    
    /* Resume Content */
    .resume-section {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-top: 1rem;
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        color: #1A1A1A;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
    }
    
    /* Slider Styling */
    .stSlider {
        margin: 1rem 0;
    }
    
    .stSlider > div > div > div {
        color: #3B82F6 !important;
    }
    </style>
    """
def format_resume_content(content: str) -> str:
    """Format resume content for cleaner display"""
    try:
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Add line breaks after common section headers
        section_headers = [
            "EDUCATION", "EXPERIENCE", "SKILLS", "CERTIFICATIONS", 
            "PROJECTS", "AWARDS", "PUBLICATIONS", "SUMMARY",
            "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE"
        ]
        
        for header in section_headers:
            content = re.sub(
                rf'\b{header}\b',
                f"\n\n{header}\n",
                content,
                flags=re.IGNORECASE
            )
        
        # Add line breaks after bullet points and dates
        content = re.sub(r'([.•-]) ', r'\1\n', content)
        content = re.sub(r'(\d{4})\s*[-–]\s*(Present|\d{4})', r'\1 - \2\n', content)
        
        # Ensure proper spacing
        content = re.sub(r'\n+', '\n\n', content)
        
        return content.strip()
    except Exception as e:
        print(f"Error formatting content: {str(e)}")
        return content

def display_resume_content(resume_content: str, requirements: dict = None, matcher = None):
    """Display resume content with semantic highlighting"""
    # Format the content
    formatted_content = format_resume_content(resume_content)
    
    # Apply highlighting if in premium mode
    if requirements and matcher:
        highlighted_content = matcher.find_matches(formatted_content, requirements)
    else:
        highlighted_content = formatted_content
    
    # Display the content in an expander
    with st.expander("View Resume Content", expanded=False):
        st.markdown(
            f'<div class="resume-section">{highlighted_content}</div>',
            unsafe_allow_html=True
        )