import streamlit as st
import pandas as pd
from resume_search import search_resumes
from resume_analysis_agent import ResumeAnalysisAgent
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Resume Analysis System",
    page_icon="📊",
    layout="wide"
)

# Custom CSS with additional styling
st.markdown("""
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
    .score-breakdown {
        margin-top: 10px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .category-header {
        font-size: 1.1em;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 15px;
    }
    .stProgress > div > div > div > div {
        background-color: #2ecc71;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .token-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    .cost-breakdown {
        margin-top: 10px;
    }
    .model-cost {
        background-color: white;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .model-name {
        color: #2c3e50;
        font-weight: 500;
    }
    .cost-value {
        color: #2ecc71;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_agent():
    """Initialize and cache the analysis agent"""
    return ResumeAnalysisAgent()

def calculate_cost(input_tokens: int, output_tokens: int, model_pricing: dict) -> float:
    """Calculate cost for a specific model's pricing"""
    input_cost = (input_tokens * model_pricing["input"]) / 1_000_000
    output_cost = (output_tokens * model_pricing["output"]) / 1_000_000
    return input_cost + output_cost

def display_token_analysis(token_usage):
    """Display token counts and costs for all models"""
    MODEL_PRICING = {
        "gemini-flash-1.5": {"input": 0.075, "output": 0.3},
        "gemini-pro-1.5": {"input": 3.5, "output": 10.5},
        "gpt4-O-mini": {"input": 0.15, "output": 0.6},
        "gpt4-O": {"input": 5.0, "output": 15.0}
    }
    
    input_tokens = token_usage["input_tokens"]
    output_tokens = token_usage["output_tokens"]
    
    st.markdown("""
        <div class="token-info">
            <h4>💰 Token Usage & Cost Analysis</h4>
            <div>Input Tokens: {:,}</div>
            <div>Output Tokens: {:,}</div>
            <div class="cost-breakdown">
                <h5>Cost by Model:</h5>
                <div class="model-cost">
                    <span class="model-name">Gemini Flash 1.5</span>
                    <span class="cost-value">${:.4f}</span>
                </div>
                <div class="model-cost">
                    <span class="model-name">Gemini Pro 1.5</span>
                    <span class="cost-value">${:.4f}</span>
                </div>
                <div class="model-cost">
                    <span class="model-name">GPT-4 O Mini</span>
                    <span class="cost-value">${:.4f}</span>
                </div>
                <div class="model-cost">
                    <span class="model-name">GPT-4 O</span>
                    <span class="cost-value">${:.4f}</span>
                </div>
            </div>
        </div>
    """.format(
        input_tokens,
        output_tokens,
        calculate_cost(input_tokens, output_tokens, MODEL_PRICING["gemini-flash-1.5"]),
        calculate_cost(input_tokens, output_tokens, MODEL_PRICING["gemini-pro-1.5"]),
        calculate_cost(input_tokens, output_tokens, MODEL_PRICING["gpt4-O-mini"]),
        calculate_cost(input_tokens, output_tokens, MODEL_PRICING["gpt4-O"])
    ), unsafe_allow_html=True)

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
            'Preferences': f"{result['component_scores']['preferences']['score']:.1f}%",
            'Initial Match': f"{result['similarity']:.1%}"
        })
    
    return pd.DataFrame(summary_data)

def display_component_details(details, component_name):
    """Display detailed breakdown of a component's scores"""
    # Display explanation
    if 'explanation' in details:
        st.markdown("#### Analysis")
        st.markdown(f"""
            <div class="explanation">
                {details['explanation']}
            </div>
        """, unsafe_allow_html=True)
    
    # Display score breakdown
    st.markdown("#### Score Breakdown")
    for key, value in details.items():
        if key != 'explanation' and isinstance(value, (int, float)):
            st.markdown(f"""
                <div class="score-breakdown">
                    <b>{key.replace('_', ' ').title()}:</b> {value:.1f}%
                </div>
            """, unsafe_allow_html=True)

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
            
            # First row: Education, Skills, Experience, Tools
            with row1_cols[0]:
                education = result['component_scores']['education']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Education Score</div>
                        <div class="score-value">{education['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(education['details'], "Education")
            
            with row1_cols[1]:
                skills = result['component_scores']['skills']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Skills Score</div>
                        <div class="score-value">{skills['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(skills['details'], "Skills")
            
            with row1_cols[2]:
                experience = result['component_scores']['experience']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Experience Score</div>
                        <div class="score-value">{experience['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(experience['details'], "Experience")
            
            with row1_cols[3]:
                tools = result['component_scores']['tools']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Tools Score</div>
                        <div class="score-value">{tools['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(tools['details'], "Tools")
            
            # Second row: Industry, Role, Preferences
            with row2_cols[0]:
                industry = result['component_scores']['industry']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Industry Score</div>
                        <div class="score-value">{industry['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(industry['details'], "Industry")
            
            with row2_cols[1]:
                role = result['component_scores']['role']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Role Score</div>
                        <div class="score-value">{role['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(role['details'], "Role")
            
            with row2_cols[2]:
                preferences = result['component_scores']['preferences']
                st.markdown(f"""
                    <div class="score-card">
                        <div class="score-label">Preferences Score</div>
                        <div class="score-value">{preferences['score']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                display_component_details(preferences['details'], "Preferences")
            
            # Add download button for resume
            if os.path.exists(result['file_path']):
                with open(result['file_path'], 'rb') as file:
                    st.download_button(
                        "📥 Download Resume",
                        file,
                        result['file_name'],
                        "application/pdf",
                        key=f"download_{idx}"
                    )

def main():
    st.title("📊 Enhanced Resume Analysis System")
    st.markdown("---")
    
    # Initialize analysis agent
    try:
        analysis_agent = initialize_agent()
    except Exception as e:
        st.error(f"Error initializing analysis agent: {str(e)}")
        return
    
    # Job Description Input
    job_description = st.text_area(
        "Enter Job Description",
        height=150,
        help="Paste the complete job description here"
    )
    
    # Search Parameters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get profession types from data directory
        try:
            profession_types = ["All Professions"] + [
                d.name for d in Path("data").iterdir() if d.is_dir()
            ]
        except Exception as e:
            st.error(f"Error loading profession types: {str(e)}")
            profession_types = ["All Professions"]
            
        selected_profession = st.selectbox(
            "Select Profession",
            profession_types
        )
    
    with col2:
        threshold = st.slider(
            "Minimum Match Score",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            help="Set minimum similarity threshold for initial matching"
        )
    
    with col3:
        max_results = st.slider(
            "Maximum Results",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of resumes to analyze"
        )
    
    with col4:
        analysis_depth = st.select_slider(
            "Analysis Depth",
            options=["Basic", "Standard", "Detailed"],
            value="Standard",
            help="Control the depth of analysis and scoring"
        )
    
    if st.button("🔍 Analyze Resumes", type="primary"):
        if not job_description:
            st.warning("Please enter a job description")
            return
            
        with st.spinner("🔍 Searching for matching resumes..."):
            try:
                # Initial resume search
                results = search_resumes(
                    query=job_description,
                    profession_type=None if selected_profession == "All Professions" else selected_profession,
                    match_threshold=threshold,
                    match_count=max_results
                )
                
                if not results:
                    st.warning("No matching resumes found. Try adjusting the search parameters.")
                    return
                
                # Perform detailed analysis
                analyzed_results = []
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                for idx, result in enumerate(results):
                    progress_text.text(f"Analyzing resume {idx + 1} of {len(results)}...")
                    
                    # Analyze resume
                    analysis = analysis_agent.analyze_resume(
                        job_description=job_description,
                        resume_content=result['content']
                    )
                    
                    # Combine results
                    analyzed_result = {**result, **analysis}
                    analyzed_results.append(analyzed_result)
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / len(results))
                
                progress_text.empty()
                progress_bar.empty()
                
                # Sort results by total score
                analyzed_results.sort(key=lambda x: x['total_score'], reverse=True)
                if analyzed_results:
                    display_token_analysis(analyzed_results[0]["token_usage"])

                # Display results
                st.markdown("## 📊 Analysis Results")
                
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
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
                raise

if __name__ == "__main__":
    main()