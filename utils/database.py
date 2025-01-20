import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
from docx import Document
import io
import re
from pdfminer.high_level import extract_text as extract_text_pdf
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

def init_connection() -> Client:
    """Initialize Supabase connection"""
    # Load environment variables from .env file
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise ValueError("Supabase URL or key is missing. Please check your .env file.")

    return create_client(url, key)



def get_custom_css():
    return """
    <style>
    /* Global styles */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Text inputs and text areas */
    .stTextArea textarea,
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;  /* Darker text color */
        border: 2px solid #CBD5E0 !important;  /* Thicker, more visible border */
        border-radius: 6px !important;
        padding: 12px !important;
        font-size: 1rem !important;
    }
    
    /* Select boxes */
    .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;  /* Darker text color */
        border: 2px solid #CBD5E0 !important;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #4A5568 !important;  /* Darker background */
        color: #FFFFFF !important;  /* White text */
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background-color: #EDF2F7 !important;  /* Light background */
        color: #2D3748 !important;  /* Dark text */
        border: 2px solid #4A5568 !important;
        box-shadow: none !important;
    }
    
    /* Headers and text */
    .main-header {
        background: linear-gradient(135deg, #2D3748, #4A5568);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards and containers */
    .search-container {
        background-color: #F7FAFC;  /* Light gray background */
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 2px solid #E2E8F0;
        margin: 1rem 0;
    }
    
    .result-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Match score badge */
    .match-score {
        background-color: #4A5568;  /* Darker background */
        color: #FFFFFF;  /* White text */
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 500;
    }
    
    /* Requirements tags */
    .requirement-tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        margin: 4px;
        color: white;
        font-weight: 500;
        background-color: #4A5568;  /* Default dark color */
    }
    
    /* Resume content section */
    .resume-section {
        background-color: #F7FAFC;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #E2E8F0;
        margin-top: 1rem;
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.6;
        color: #2D3748;  /* Darker text */
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F7FAFC !important;
        color: #2D3748 !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 6px !important;
    }
    </style>
    """
