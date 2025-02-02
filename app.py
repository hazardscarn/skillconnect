import streamlit as st
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import atexit

from file_utils import read_file_content, save_uploaded_file
from display_utils import (
    create_summary_table, display_file_tree, display_detailed_results,
    display_weight_controls, load_custom_css
)
from model_manager import ModelManager
from resume_analysis_agent import ResumeAnalysisAgent

# Page configuration
st.set_page_config(
    page_title="Resume Analysis System",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def initialize_agent(model_id: Optional[str] = None):
    """Initialize and cache the analysis agent"""
    model_manager = ModelManager()
    if model_id is None:
        model_id = model_manager.get_default_model_id()
    return ResumeAnalysisAgent(model_id)

def handle_file_upload():
    """Handle file uploads in sidebar"""
    # Job Posting Upload
    st.subheader("Upload Job Description")
    jd_file = st.file_uploader("Choose a job description file", 
                              type=['pdf', 'docx', 'txt'],
                              key="jd_uploader")
    
    if jd_file is not None:
        jd_dir = os.path.join(st.session_state.temp_dir, 'job_posting')
        for file in os.listdir(jd_dir):
            os.remove(os.path.join(jd_dir, file))
        
        save_uploaded_file(jd_file, jd_dir)
        st.success(f"Job Description uploaded: {jd_file.name}")

# Resume Upload
    st.subheader("Upload Resumes")
    resume_files = st.file_uploader("Choose resume files", 
                                  type=['pdf', 'docx'],
                                  accept_multiple_files=True,
                                  key="resume_uploader")
    
    if resume_files:
        resume_dir = os.path.join(st.session_state.temp_dir, 'resumes')
        for resume in resume_files:
            save_uploaded_file(resume, resume_dir)
        st.success(f"Uploaded {len(resume_files)} resume(s)")

def cleanup_temp_files():
    """Clean up temporary files when session ends"""
    if hasattr(st.session_state, 'temp_dir'):
        shutil.rmtree(st.session_state.temp_dir)

def main():
    # Load custom CSS
    st.markdown(load_custom_css(), unsafe_allow_html=True)

    # Initialize session state
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(st.session_state.temp_dir, 'job_posting'), exist_ok=True)
        os.makedirs(os.path.join(st.session_state.temp_dir, 'resumes'), exist_ok=True)

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")

        # Model Selection
        st.subheader("🤖 Model Selection")
        model_manager = ModelManager()
        model_names = model_manager.get_model_names()
        
        selected_model_id = st.selectbox(
            "Choose Analysis Model",
            options=list(model_names.keys()),
            format_func=lambda x: model_names[x],
            index=list(model_names.keys()).index(model_manager.get_default_model_id())
        )
        
        # Display model description
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <small>{model_manager.get_model_description(selected_model_id)}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Display pricing information
        pricing = model_manager.get_model_pricing(selected_model_id)
        st.markdown("""
            <div style="margin-top: 10px;">
                <small>
                    <b>Pricing (per million tokens):</b><br>
                    Input: ${:.3f}<br>
                    Output: ${:.3f}
                </small>
            </div>
        """.format(pricing['input'], pricing['output']), unsafe_allow_html=True)
        
        st.markdown("---")

        # Weight controls
        weights_valid = display_weight_controls()

        st.markdown("---")

        # File Management
        st.title("📁 File Management")
        handle_file_upload()
        
        # Display file structure
        st.subheader("Current Files")
        display_file_tree()
        
        # Clear files button
        if st.button("Clear All Files", type="secondary"):
            for dir_name in ['job_posting', 'resumes']:
                dir_path = os.path.join(st.session_state.temp_dir, dir_name)
                for file in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file))
            st.success("All files cleared!")
            st.rerun()

    # Main content area
    st.title("📊 Resume Analysis System")
    st.markdown("---")

    # Initialize analysis agent
    try:
        analysis_agent = initialize_agent(model_id=selected_model_id)
    except Exception as e:
        st.error(f"Error initializing analysis agent: {str(e)}")
        return

    # Check if files are uploaded
    jd_path = os.path.join(st.session_state.temp_dir, 'job_posting')
    resume_path = os.path.join(st.session_state.temp_dir, 'resumes')
    
    if not os.listdir(jd_path):
        st.warning("Please upload a job description first.")
        return
    
    if not os.listdir(resume_path):
        st.warning("Please upload some resumes to analyze.")
        return

    # Create columns for analyze and clear buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        analyze_clicked = st.button("🔍 Analyze Resumes", type="primary")
    with col2:
        clear_analysis = st.button("🔄 Run New Analysis", type="secondary")

    if clear_analysis:
        st.session_state.analyzed_results = None
        st.rerun()

    if analyze_clicked:
        try:
            if not weights_valid:
                st.error("Please ensure weights total exactly 1.0 before analyzing")
                return

            # Read job description
            jd_file = os.listdir(jd_path)[0]
            job_description = read_file_content(os.path.join(jd_path, jd_file))
            
            if not job_description:
                st.error("Could not read job description file.")
                return

            # Process all resumes
            analyzed_results = []
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            resume_files = os.listdir(resume_path)
            for idx, resume_file in enumerate(resume_files):
                progress_text.text(f"Analyzing resume {idx + 1} of {len(resume_files)}...")
                
                # Read resume content
                resume_content = read_file_content(os.path.join(resume_path, resume_file))
                if resume_content:
                    # Analyze resume with custom weights
                    analysis = analysis_agent.analyze_resume(
                        job_description=job_description,
                        resume_content=resume_content,
                        weights=st.session_state.analysis_weights
                    )
                    
                    # Add file information
                    analysis['file_name'] = resume_file
                    analysis['file_path'] = os.path.join(resume_path, resume_file)
                    
                    analyzed_results.append(analysis)
                
                # Update progress
                progress_bar.progress((idx + 1) / len(resume_files))
            
            progress_text.empty()
            progress_bar.empty()

            # Sort results and store in session state
            analyzed_results.sort(key=lambda x: x['total_score'], reverse=True)
            st.session_state.analyzed_results = analyzed_results

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            raise

    # Display results if available in session state
    if hasattr(st.session_state, 'analyzed_results') and st.session_state.analyzed_results:
        analyzed_results = st.session_state.analyzed_results
        
        # Display token usage
        if 'token_usage' in analyzed_results[0]:
            st.markdown("""
                <div class="token-info">
                    <h4>💰 Token Usage</h4>
                    <div>Input Tokens: {:,}</div>
                    <div>Output Tokens: {:,}</div>
                </div>
            """.format(
                analyzed_results[0]['token_usage']['input_tokens'],
                analyzed_results[0]['token_usage']['output_tokens']
            ), unsafe_allow_html=True)
        
        # Display summary table
        st.markdown("## 📊 Analysis Results")
        summary_df = create_summary_table(analyzed_results)
        st.dataframe(
            summary_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Add download button for summary
        st.download_button(
            "📥 Download Analysis Summary",
            summary_df.to_csv(index=False).encode('utf-8'),
            "resume_analysis_summary.csv",
            "text/csv",
            key="download_summary"
        )
        
        # Display detailed results
        st.markdown("## 📑 Detailed Analysis")
        display_detailed_results(analyzed_results)

# Register cleanup function
atexit.register(cleanup_temp_files)

if __name__ == "__main__":
    main()