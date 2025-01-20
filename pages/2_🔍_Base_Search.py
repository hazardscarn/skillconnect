import streamlit as st
import pandas as pd
from resume_search import search_resumes
import os
from pathlib import Path
import zipfile
import io
import re

def get_base_css():
    return """
    <style>
    /* Base styling */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Text inputs and text areas - Higher contrast */
    .stTextArea textarea,
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        border: 2px solid #4A5568 !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    
    /* Select boxes - More visible */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #1A202C !important;
        border: 2px solid #4A5568 !important;
    }
    
    /* Buttons - High contrast */
    .stButton>button {
        background-color: #4A5568 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Download buttons - Clear distinction */
    .stDownloadButton>button {
        background-color: #EDF2F7 !important;
        color: #4A5568 !important;
        border: 2px solid #4A5568 !important;
        font-weight: 600 !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #4A5568, #718096);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Search container - More visible */
    .search-container {
        background-color: #F7FAFC;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid #CBD5E0;
        margin: 1rem 0;
    }
    
    /* Results styling - Better contrast */
    .result-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #CBD5E0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Match score - High visibility */
    .match-score {
        background-color: #4A5568;
        color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Resume content section - Improved readability */
    .resume-section {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #CBD5E0;
        margin-top: 1rem;
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.6;
        color: #1A202C;
    }

    /* Slider styling - Better visibility */
    .stSlider > div > div > div {
        background-color: #4A5568 !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F8FAFC !important;
        color: #1A202C !important;
        border: 2px solid #CBD5E0 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Download section */
    .download-section {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #F7FAFC;
        border-radius: 8px;
        border: 2px solid #CBD5E0;
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
                f"\n\n{header}\n",
                content,
                flags=re.IGNORECASE
            )
        
        content = re.sub(r'([.•-]) ', r'\1\n', content)
        content = re.sub(r'(\d{4})\s*[-–]\s*(Present|\d{4})', r'\1 - \2\n', content)
        content = re.sub(r'\n+', '\n\n', content)
        
        return content.strip()
    except Exception as e:
        print(f"Error formatting content: {str(e)}")
        return content

def display_resume_content(resume_content: str):
    formatted_content = format_resume_content(resume_content)
    with st.expander("View Resume Content", expanded=False):
        st.markdown(
            f'<div class="resume-section">{formatted_content}</div>',
            unsafe_allow_html=True
        )

def main():
    st.set_page_config(
        page_title="Base Resume Search",
        page_icon="🔍",
        layout="wide",
    )

    # Apply custom styling
    st.markdown(get_base_css(), unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1 style='font-size: 2.2rem; margin-bottom: 0.5rem;'>🔍 Base Resume Search</h1>
            <p style='font-size: 1.1rem; opacity: 0.9;'>Quick and efficient resume matching</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search interface
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        search_query = st.text_area(
            "Enter Job Description",
            height=150,
            placeholder="Paste the job description here to find matching resumes..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            profession_types = get_profession_types()
            selected_profession = st.selectbox(
                "Select Profession",
                ["All Professions"] + profession_types
            )
        with col2:
            max_results = st.slider(
                "Maximum Results",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum number of resumes to return"
            )
        with col3:
            threshold = st.slider(
                "Minimum Match Score",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                help="Minimum similarity score required for a match"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        search_button = st.button("🔍 Search Resumes", type="primary", use_container_width=True)
        
        if search_button and search_query:
            with st.spinner("Searching resumes..."):
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
                                    <h3 style="margin: 0; color: #1A202C;">Match #{i}</h3>
                                    <span class="match-score">{result['similarity']:.1%} Match</span>
                                </div>
                                <p style="margin-top: 0.5rem; color: #2D3748;"><strong>Profession:</strong> {result['profession_type']}</p>
                                <p style="color: #2D3748;"><strong>File:</strong> {result['file_name']}</p>
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
                            
                            # Display resume content
                            display_resume_content(result['content'])
                
                else:
                    st.error("No matching resumes found. Try adjusting your search criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #4A5568; padding: 2rem;'>
            <p>Built with ❤️ using Streamlit • Powered by Google AI • © 2024</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()