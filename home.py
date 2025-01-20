import streamlit as st

def get_custom_css():
    return """
    <style>
    /* Previous styles remain the same until feature cards */
    
    /* Text inputs and text areas */
    .stTextArea textarea,
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 2px solid #CBD5E0 !important;
        border-radius: 6px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    
    /* Select boxes */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 2px solid #CBD5E0 !important;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #4A5568 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Feature Cards - Updated styling */
    .feature-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        margin: 1rem;
        transition: all 0.3s ease;
        position: relative;
        top: 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .feature-card:hover {
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        top: -5px;
    }
    
    .feature-card.premium {
        border: 2px solid #3182CE;
    }
    
    .feature-card .version-header {
        color: #1A202C;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .feature-card .feature-icon {
        font-size: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .feature-card ul {
        padding-left: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .feature-card ul li {
        margin-bottom: 0.75rem;
        color: #4A5568;
    }
    
    .feature-card .card-footer {
        background-color: #EBF8FF;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1.5rem;
        color: #2B6CB0;
        font-weight: 500;
    }
    
    /* Other styles remain the same */
    /* ... */
    </style>
    """

# Page configuration
st.set_page_config(
    page_title="Resume Search Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Main Header
st.markdown("""
    <div class="main-header" style="background: linear-gradient(45deg, #1a237e, #0d47a1, #1565c0, #0288d1);">
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>🎯 Smart Resume Search Engine</h1>
        <p style='font-size: 1.2rem; opacity: 0.9;'>Advanced AI-powered resume matching and analysis</p>
    </div>
""", unsafe_allow_html=True)

# Version Comparison with updated card styling
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-card">
            <h2 class="version-header">🔍 Base Version</h2>
            <div class="feature-icon">📄</div>
            <h3 style="color: #1A202C; font-size: 1.25rem; margin-top: 1.5rem;">Features:</h3>
            <ul>
                <li>Instant resume similarity search</li>
                <li>Profession-based filtering</li>
                <li>Basic match scoring</li>
                <li>Resume download capability</li>
                <li>Fast and efficient search results</li>
            </ul>
            <div class="card-footer">
                Perfect for quick resume screening and basic matching
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card premium">
            <h2 class="version-header">💎 Premium Version</h2>
            <div class="feature-icon">✨</div>
            <h3 style="color: #1A202C; font-size: 1.25rem; margin-top: 1.5rem;">Additional Features:</h3>
            <ul>
                <li>AI-powered requirement analysis</li>
                <li>Smart semantic matching</li>
                <li>Color-coded skill mapping</li>
                <li>Detailed requirement breakdown</li>
                <li>Advanced filtering options</li>
                <li>Confidence scoring</li>
            </ul>
            <div class="card-footer">
                Advanced features for detailed candidate analysis
            </div>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <p style='color: #4A5568;'>Built with ❤️ using Streamlit • Powered by Google AI • © 2024</p>
        <div style='display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;'>
            <span style='color: #718096;'>Python</span>
            <span style='color: #718096;'>•</span>
            <span style='color: #718096;'>Streamlit</span>
            <span style='color: #718096;'>•</span>
            <span style='color: #718096;'>Gemini AI</span>
        </div>
    </div>
""", unsafe_allow_html=True)