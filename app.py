import streamlit as st
import pandas as pd
from resume_search import search_resumes
import os
from pathlib import Path
import plotly.express as px
from jdanalysisagent import JDAnalysisAgent
from resumematcher import SemanticMatcher
import zipfile
import io

# Page configuration
st.set_page_config(
    page_title="Smart Resume Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .requirement-tag {
        display: inline-block;
        padding: 8px 12px;
        margin: 4px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: 500;
        color: white;
    }
    .requirements-header {
        font-size: 1.2em;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .requirements-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .search-results {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .resume-content {
        font-family: 'Source Sans Pro', sans-serif;
        line-height: 1.6;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .match-confidence {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 0.8em;
        margin-left: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def create_zip_file(file_paths: list) -> bytes:
    """Create a zip file containing multiple PDFs"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
    return zip_buffer.getvalue()

def get_pdf_download_link(file_path: str, display_name: str) -> bytes:
    """Create a download link for a PDF file"""
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading file {display_name}: {str(e)}")
        return None

def get_profession_types():
    """Get list of profession types from data directory"""
    data_dir = Path("data")
    return [d.name for d in data_dir.iterdir() if d.is_dir()]

@st.cache_resource
def get_agents():
    """Initialize and cache the analysis agents"""
    return JDAnalysisAgent(), SemanticMatcher()

def display_requirements(requirements: dict):
    """Display identified requirements with their respective colors"""
    st.markdown('<div class="requirements-container">', unsafe_allow_html=True)
    st.markdown('### 🎯 Key Requirements Identified')
    
    for req in requirements["requirements"]:
        st.markdown(
            f'<div class="requirement-tag" style="background-color: {req["color"]};">'
            f'{req["responsibility"]}</div>',
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_resume_content(resume_content: str, requirements: dict, matcher: SemanticMatcher):
    """Display resume content with semantic highlighting"""
    with st.expander("View Resume Content", expanded=True):
        highlighted_content = matcher.find_matches(resume_content, requirements)
        st.markdown(
            f'<div class="resume-content">{highlighted_content}</div>',
            unsafe_allow_html=True
        )

def main():
    # Initialize agents
    jd_agent, semantic_matcher = get_agents()
    
    # Header
    st.title("🔍 Smart Resume Search Engine")
    st.markdown("---")
    
    # Main search interface
    search_query = st.text_area(
        "Enter Job Description",
        height=150,
        placeholder="Paste the job description here..."
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        profession_types = get_profession_types()
        selected_profession = st.selectbox(
            "Select Profession",
            ["All Professions"] + profession_types
        )
    with col2:
        threshold = st.slider(
            "Match Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3
        )
    with col3:
        max_results = st.slider(
            "Maximum Results",
            min_value=1,
            max_value=20,
            value=5
        )
    
    search_button = st.button("🔍 Search Resumes", type="primary")
    
    if search_button and search_query:
        # Analyze requirements
        with st.spinner("Analyzing requirements..."):
            requirements = jd_agent.analyze_jd(search_query)
            display_requirements(requirements)
        
        # Search resumes
        with st.spinner("Searching resumes..."):
            profession_filter = None if selected_profession == "All Professions" else selected_profession
            results = search_resumes(
                query=search_query,
                profession_type=profession_filter,
                match_threshold=threshold,
                match_count=max_results
            )
            
            if results:
                # Create download all button
                zip_data = create_zip_file([r['file_path'] for r in results])
                st.download_button(
                    "📥 Download All Matching Resumes",
                    data=zip_data,
                    file_name="matching_resumes.zip",
                    mime="application/zip"
                )
                
                # Display results
                for i, result in enumerate(results, 1):
                    st.markdown("---")
                    with st.container():
                        st.markdown(f"""
                        <div class="search-results">
                            <h3>Match #{i} - {result['similarity']:.1%} Match</h3>
                            <p><strong>Profession:</strong> {result['profession_type']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add download button
                        pdf_data = get_pdf_download_link(result['file_path'], result['file_name'])
                        if pdf_data:
                            st.download_button(
                                "📄 Download Resume",
                                data=pdf_data,
                                file_name=result['file_name'],
                                mime="application/pdf",
                                key=f"download_{i}"
                            )
                        
                        # Display resume content with semantic matching
                        display_resume_content(result['content'], requirements, semantic_matcher)
            
            else:
                st.error("No matching resumes found.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Built with Streamlit • Powered by Google AI • © 2024</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()