import streamlit as st
import pandas as pd
import os

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

def display_detailed_results(analyzed_results):
    """Display detailed analysis for each resume with download option"""
    for idx, result in enumerate(analyzed_results, 1):
        with st.expander(f"📄 Resume #{idx}: {result['file_name']}", expanded=idx==1):
            # Add download button at the top
            if os.path.exists(result['file_path']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                            <strong>File:</strong> {result['file_name']}
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    with open(result['file_path'], 'rb') as file:
                        st.download_button(
                            label="📥 Download Resume",
                            data=file,
                            file_name=result['file_name'],
                            mime="application/octet-stream",
                            key=f"download_resume_{idx}"
                        )
            
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

def display_weight_controls():
    """Display and handle analysis weight controls"""
    st.sidebar.markdown("## 📊 Analysis Weights")
    
    # Initialize weights if not in session state
    if 'analysis_weights' not in st.session_state:
        st.session_state.analysis_weights = {
            "education": 0.15,
            "skills": 0.20,
            "experience": 0.20,
            "tools": 0.15,
            "industry": 0.10,
            "role": 0.15,
            "preferences": 0.05
        }
    
    # Create weight adjusters
    new_weights = {}
    total_weight = 0.0
    
    for component, weight in st.session_state.analysis_weights.items():
        new_weight = st.sidebar.number_input(
            f"{component.title()} Weight",
            min_value=0.0,
            max_value=1.0,
            value=float(weight),
            step=0.05,
            key=f"weight_{component}"
        )
        new_weights[component] = new_weight
        total_weight += new_weight
    
    # Display total and validation
    if abs(total_weight - 1.0) < 0.0001:
        st.sidebar.success(f"Total Weight: {total_weight:.2f}")
        st.session_state.analysis_weights = new_weights
        return True
    else:
        st.sidebar.error(f"Total Weight: {total_weight:.2f} (Must equal 1.0)")
        return False

def load_custom_css():
    """Load custom CSS styles"""
    return """
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
    </style>
    """