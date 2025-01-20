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
import re

def get_premium_css():
    return """
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Improved visibility for text inputs */
    .stTextArea textarea,
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #000000 !important;  /* Pure black text */
        border: 2px solid #2C5282 !important;  /* Darker border */
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1.1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Enhanced selectbox visibility */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #2C5282 !important;
        border-radius: 8px !important;
    }
    
    /* High contrast buttons */
    .stButton>button {
        background-color: #2C5282 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #1A365D !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Distinctive download buttons */
    .stDownloadButton>button {
        background-color: #FFFFFF !important;
        color: #2C5282 !important;
        border: 2px solid #2C5282 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stDownloadButton>button:hover {
        background-color: #EBF8FF !important;
    }
    
    /* Premium header with improved visibility */
    .main-header {
        background: linear-gradient(135deg, #1A365D, #2C5282);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Enhanced search container */
    .search-container {
        background-color: #F8FAFC;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #2C5282;
        margin: 1.5rem 0;
    }
    
    /* Improved result cards */
    .result-card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 12px;
        border: 2px solid #2C5282;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced match score badge */
    .match-score {
        background-color: #2C5282;
        color: #FFFFFF;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Requirements section with better visibility */
    .requirements-container {
        background-color: #F8FAFC;
        padding: 1.8rem;
        border-radius: 12px;
        border: 2px solid #2C5282;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced requirement tags */
    .requirement-tag {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 6px;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Improved resume content section */
    .resume-section {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #2C5282;
        margin-top: 1.5rem;
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.8;
        color: #000000;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Enhanced slider styling */
    .stSlider > div > div > div {
        background-color: #2C5282 !important;
    }
    
    .stSlider > div > div > div > div {
        color: #000000 !important;
    }

    /* Improved expander styling */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #2C5282 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    /* Text color enhancements */
    p, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    /* Label color improvements */
    .stMarkdown div {
        color: #000000 !important;
    }
    </style>
    """

def create_zip_file(file_paths: list) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
    return zip_buffer.getvalue()

def get_pdf_download_link(file_path: str, display_name: str) -> bytes:
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error reading file {display_name}: {str(e)}")
        return None

def get_profession_types():
    data_dir = Path("data")
    return [d.name for d in data_dir.iterdir() if d.is_dir()]

def format_resume_content(content: str) -> str:
    try:
        content = ' '.join(content.split())
        section_headers = [
            "EDUCATION", "EXPERIENCE", "SKILLS", "CERTIFICATIONS", 
            "PROJECTS", "AWARDS", "PUBLICATIONS", "SUMMARY",
            "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE"
        ]
        
        for header in section_headers:
            content = re.sub(
                rf'\b{header}\b',
                f"\n\n**{header}**\n",  # Added bold markdown
                content,
                flags=re.IGNORECASE
            )
        
        content = re.sub(r'([.•-]) ', r'\1\n', content)
        content = re.sub(r'(\d{4})\s*[-–]\s*(Present|\d{4})', r'**\1 - \2**\n', content)  # Added bold for dates
        content = re.sub(r'\n+', '\n\n', content)
        
        return content.strip()
    except Exception as e:
        print(f"Error formatting content: {str(e)}")
        return content

def display_resume_content(resume_content: str, requirements: dict = None, matcher = None):
    formatted_content = format_resume_content(resume_content)
    
    if requirements and matcher:
        highlighted_content = matcher.find_matches(formatted_content, requirements)
    else:
        highlighted_content = formatted_content
    
    with st.expander("📄 View Resume Content", expanded=False):
        st.markdown(
            f'<div class="resume-section">{highlighted_content}</div>',
            unsafe_allow_html=True
        )

def get_agents():
    try:
        jd_agent = JDAnalysisAgent()
        semantic_matcher = SemanticMatcher()
        return jd_agent, semantic_matcher
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None

def display_requirements(requirements: dict):
    """Display identified requirements with their respective colors"""
    st.markdown("""
        <div class="requirements-container">
            <h3 class="section-header" style="color: #2D3748 !important;">
                🎯 Key Requirements Identified
            </h3>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
    """, unsafe_allow_html=True)
    
    for req in requirements["requirements"]:
        st.markdown(
            f'<div class="requirement-tag" style="background-color: {req["color"]};">'
            f'{req["responsibility"]}</div>',
            unsafe_allow_html=True
        )
        
def main():
    st.set_page_config(
        page_title="Premium Resume Search",
        page_icon="💎",
        layout="wide",
    )

    # Apply custom styling
    st.markdown(get_premium_css(), unsafe_allow_html=True)

    # Initialize agents
    jd_agent, semantic_matcher = get_agents()
    
    # Premium Header
    st.markdown("""
        <div class="main-header">
            <h1 style='font-size: 2.5rem; margin-bottom: 0.8rem;'>💎 Premium Resume Search</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Advanced AI-powered matching and analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main search interface
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Job Description Input
        search_query = st.text_area(
            "📝 Enter Job Description",
            height=150,
            placeholder="Paste the job description here to analyze requirements and find matching resumes...",
            key="jd_input"
        )
        
        # Search Controls
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            profession_types = get_profession_types()
            selected_profession = st.selectbox(
                "👔 Select Profession",
                ["All Professions"] + profession_types
            )
        with col2:
            max_results = st.slider(
                "📊 Maximum Results",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum number of resumes to return"
            )
        with col3:
            threshold = st.slider(
                "🎯 Minimum Match Score",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                help="Minimum similarity score required for a match"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Search Button
        search_button = st.button("🔍 Search Resumes", type="primary", use_container_width=True)
        
        if search_button and search_query:
            # Analyze requirements
            with st.spinner("Analyzing job requirements..."):
                requirements = jd_agent.analyze_jd(search_query)
                display_requirements(requirements)
            
            # Search resumes
            with st.spinner("Searching and analyzing resumes..."):
                profession_filter = None if selected_profession == "All Professions" else selected_profession
                results = search_resumes(
                    query=search_query,
                    profession_type=profession_filter,
                    match_threshold=threshold,
                    match_count=max_results
                )
                
                if results:
                    # Create similarity chart
                    chart_data = pd.DataFrame([
                        {'Resume': r['file_name'], 'Match Score': r['similarity']}
                        for r in results
                    ])
                    
                    fig = px.bar(
                        chart_data,
                        x='Resume',
                        y='Match Score',
                        title='Match Scores',
                        color='Match Score',
                        color_continuous_scale='blues',
                        range_y=[0, 1]
                    )
                    fig.update_layout(
                        height=300,
                        margin=dict(t=30, b=30, l=30, r=30)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download all button
                    st.markdown('<div class="download-section">', unsafe_allow_html=True)
                    zip_data = create_zip_file([r['file_path'] for r in results])
                    st.download_button(
                        "📥 Download All Matching Resumes",
                        data=zip_data,
                        file_name="matching_resumes.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display results
                    for i, result in enumerate(results, 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="result-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <h3 style="margin: 0;">Match #{i}</h3>
                                    <span class="match-score">{result['similarity']:.1%} Match</span>
                                </div>
                                <p style="margin-top: 0.5rem;"><strong>Profession:</strong> {result['profession_type']}</p>
                                <p><strong>File:</strong> {result['file_name']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Individual download button
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
                    st.error("No matching resumes found. Try adjusting your search criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <p style='color: #2C5282; font-size: 1.1rem;'>Built with ❤️ using Streamlit • Powered by Google AI • © 2024</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()