import streamlit as st
import os
import shutil
from pathlib import Path
import pandas as pd
import tempfile
from datetime import datetime
from resume_analysis_agent import ResumeAnalysisAgent
import PyPDF2
import docx2txt
from model_manager import ModelManager

# Set up the main page
st.set_page_config(
    page_title="Resume Analysis System",
    page_icon="📊",
    layout="wide"
)

# Custom CSS to be added at the beginning of the main function
custom_css = """
<style>
.score-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 10px 0;
}

.score-label {
    font-size: 0.9em;
    color: #666;
    margin-bottom: 5px;
}

.score-value {
    font-size: 1.2em;
    font-weight: bold;
    color: #1f77b4;
}

.total-score {
    font-size: 1.5em;
    font-weight: bold;
    color: #2ecc71;
}

.explanation {
    font-size: 0.9em;
    color: #333;
    margin-top: 10px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 5px;
}

.token-info {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border: 1px solid #dee2e6;
}

.stProgress > div > div > div > div {
    background-color: #2ecc71;
}

/* File tree customization */
.file-tree {
    font-family: 'Courier New', monospace;
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e9ecef;
    margin-bottom: 15px;
}

.folder-name {
    color: #2962ff;
    font-weight: bold;
    font-size: 1.1em;
    margin: 10px 0 5px 0;
    padding-left: 5px;
    border-left: 3px solid #2962ff;
}

.file-item {
    margin-left: 20px;
    padding: 5px 0;
    display: flex;
    align-items: center;
    transition: background-color 0.2s;
}

.file-item:hover {
    background-color: #e9ecef;
    border-radius: 5px;
}

/* Upload section customization */
.upload-section {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.upload-header {
    color: #2c3e50;
    font-size: 1.2em;
    margin-bottom: 10px;
}

/* Analysis results customization */
.analysis-section {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-top: 20px;
}

.analysis-header {
    color: #2c3e50;
    font-size: 1.3em;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e9ecef;
}

/* Button customization */
.stButton button {
    border-radius: 20px;
    padding: 10px 25px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Progress bar customization */
.stProgress > div > div > div {
    border-radius: 10px;
}

/* Expander customization */
.streamlit-expanderHeader {
    background-color: #f8f9fa;
    border-radius: 5px;
    padding: 10px !important;
}

.streamlit-expanderHeader:hover {
    background-color: #e9ecef;
}
</style>
"""

def read_file_content(file_path):
    """Read content from PDF or DOCX files"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
                return content
        except Exception as e:
            st.error(f"Error reading PDF file: {str(e)}")
            return None
            
    elif file_extension == '.docx':
        try:
            content = docx2txt.process(file_path)
            return content
        except Exception as e:
            st.error(f"Error reading DOCX file: {str(e)}")
            return None
            
    elif file_extension == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            st.error(f"Error reading TXT file: {str(e)}")
            return None
    
    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None

@st.cache_resource
def initialize_agent():
    """Initialize and cache the analysis agent"""
    return ResumeAnalysisAgent()

def save_uploaded_file(uploaded_file, directory):
    """Save uploaded file to specified directory"""
    if uploaded_file is not None:
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def display_file_tree():
    """Display file structure with download buttons"""
    st.markdown("""
        <style>
            .file-tree {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .folder-name {
                color: #2962ff;
                font-weight: bold;
                font-size: 1.1em;
                margin: 10px 0 5px 0;
            }
            .file-item {
                margin-left: 20px;
                padding: 5px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display Job Posting section
    st.markdown('<div class="file-tree">', unsafe_allow_html=True)
    st.markdown('<div class="folder-name">📁 job_posting</div>', unsafe_allow_html=True)
    job_posting_path = os.path.join(st.session_state.temp_dir, 'job_posting')
    if os.path.exists(job_posting_path):
        for file in os.listdir(job_posting_path):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<div class="file-item">📄 {file}</div>', unsafe_allow_html=True)
                with col2:
                    with open(os.path.join(job_posting_path, file), 'rb') as f:
                        st.download_button(
                            label="📥",
                            data=f,
                            file_name=file,
                            mime="application/octet-stream",
                            key=f"dl_jd_{file}"
                        )

    # Display Resumes section
    st.markdown('<div class="folder-name">📁 resumes</div>', unsafe_allow_html=True)
    resumes_path = os.path.join(st.session_state.temp_dir, 'resumes')
    if os.path.exists(resumes_path):
        for file in os.listdir(resumes_path):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<div class="file-item">📄 {file}</div>', unsafe_allow_html=True)
                with col2:
                    with open(os.path.join(resumes_path, file), 'rb') as f:
                        st.download_button(
                            label="📥",
                            data=f,
                            file_name=file,
                            mime="application/octet-stream",
                            key=f"dl_resume_{file}"
                        )
    st.markdown('</div>', unsafe_allow_html=True)

def create_summary_table(analyzed_results):
    """Create summary DataFrame for displaying results"""
    summary_data = []
    for result in analyzed_results:
        summary_data.append({
            'Resume': result['file_name'],
            'Total Score': f"{result['total_score']:.1f}%",
            'Education': f"{result['component_scores']['education']['score']:.1f}%",
            'Skills': f"{result['component_scores']['skills']['score']:.1f}%",
            'Experience': f"{result['component_scores']['experience']['score']:.1f}%",
            'Tools': f"{result['component_scores']['tools']['score']:.1f}%",
            'Industry': f"{result['component_scores']['industry']['score']:.1f}%",
            'Role': f"{result['component_scores']['role']['score']:.1f}%",
            'Preferences': f"{result['component_scores']['preferences']['score']:.1f}%"
        })
    return pd.DataFrame(summary_data)

def display_detailed_results(analyzed_results):
    """Display detailed analysis for each resume"""
    for idx, result in enumerate(analyzed_results, 1):
        with st.expander(f"📄 Resume #{idx}: {result['file_name']}", expanded=idx==1):
            # Display total score
            st.markdown(f"""
                <div class="score-card">
                    <div class="score-label">Total Score</div>
                    <div class="total-score">{result['total_score']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display all component scores in two rows
            row1_cols = st.columns(4)
            row2_cols = st.columns(3)
            
            components = {
                'row1': ['education', 'skills', 'experience', 'tools'],
                'row2': ['industry', 'role', 'preferences']
            }
            
            # First row
            for i, component in enumerate(components['row1']):
                with row1_cols[i]:
                    score_data = result['component_scores'][component]
                    st.markdown(f"""
                        <div class="score-card">
                            <div class="score-label">{component.title()} Score</div>
                            <div class="score-value">{score_data['score']:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("#### Analysis")
                    st.markdown(f"""
                        <div class="explanation">
                            {score_data['details']['explanation']}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Second row
            for i, component in enumerate(components['row2']):
                with row2_cols[i]:
                    score_data = result['component_scores'][component]
                    st.markdown(f"""
                        <div class="score-card">
                            <div class="score-label">{component.title()} Score</div>
                            <div class="score-value">{score_data['score']:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("#### Analysis")
                    st.markdown(f"""
                        <div class="explanation">
                            {score_data['details']['explanation']}
                        </div>
                    """, unsafe_allow_html=True)

def main():


    st.markdown(custom_css, unsafe_allow_html=True)
    

    # Initialize session state
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(st.session_state.temp_dir, 'job_posting'), exist_ok=True)
        os.makedirs(os.path.join(st.session_state.temp_dir, 'resumes'), exist_ok=True)

    # Sidebar
    with st.sidebar:

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
            # Initialize analysis agent
        try:
            analysis_agent = ResumeAnalysisAgent(model_id=selected_model_id)
        except Exception as e:
            st.error(f"Error initializing analysis agent: {str(e)}")
            return


        st.title("📁 File Management")
        
        # Job Posting Upload
        st.subheader("Upload Job Description")
        jd_file = st.file_uploader("Choose a job description file", 
                                  type=['pdf', 'docx', 'txt'],
                                  key="jd_uploader")
        
        if jd_file is not None:
            # Clear existing job postings
            jd_dir = os.path.join(st.session_state.temp_dir, 'job_posting')
            for file in os.listdir(jd_dir):
                os.remove(os.path.join(jd_dir, file))
            
            # Save new job posting
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
        
        # Display file structure with download buttons
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

    # Check if files are uploaded
    jd_path = os.path.join(st.session_state.temp_dir, 'job_posting')
    resume_path = os.path.join(st.session_state.temp_dir, 'resumes')
    
    if not os.listdir(jd_path):
        st.warning("Please upload a job description first.")
        return
    
    if not os.listdir(resume_path):
        st.warning("Please upload some resumes to analyze.")
        return

    # Add analyze button
    if st.button("🔍 Analyze Resumes", type="primary"):
        try:
            # Read job description
            jd_file = os.listdir(jd_path)[0]  # Get the first (and should be only) JD file
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
                    # Analyze resume
                    analysis = analysis_agent.analyze_resume(
                        job_description=job_description,
                        resume_content=resume_content
                    )
                    
                    # Add file information
                    analysis['file_name'] = resume_file
                    analysis['file_path'] = os.path.join(resume_path, resume_file)
                    
                    analyzed_results.append(analysis)
                
                # Update progress
                progress_bar.progress((idx + 1) / len(resume_files))
            
            progress_text.empty()
            progress_bar.empty()

            # Sort results by total score
            analyzed_results.sort(key=lambda x: x['total_score'], reverse=True)

            # Display results
            if analyzed_results:
                st.markdown("## 📊 Analysis Results")
                
                # Display token usage if available
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
                
                # Create and display summary table
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
            
            else:
                st.warning("No resumes could be analyzed. Please check the file formats and contents.")

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            raise

# Handle file cleanup when the session ends
def cleanup_temp_files():
    if hasattr(st.session_state, 'temp_dir'):
        shutil.rmtree(st.session_state.temp_dir)

# Register cleanup function
import atexit
atexit.register(cleanup_temp_files)

if __name__ == "__main__":
    main()