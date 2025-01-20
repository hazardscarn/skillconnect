import os
from pathlib import Path
from typing import List, Dict
from pdfminer.high_level import extract_text as extract_text_pdf
import io
from pdf2image import convert_from_bytes
import pytesseract
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time
from utils import init_connection
from pprint import pprint
import yaml

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file using pdfminer with OCR fallback.
    This mirrors the functionality in utils.py but works with local files.
    """
    try:
        # First try pdfminer for text extraction
        with open(file_path, 'rb') as file:
            file_content = file.read()
            
        # Try pdfminer first
        text = extract_text_pdf(io.BytesIO(file_content))
        
        # If pdfminer doesn't extract meaningful text, fallback to OCR
        if not text.strip():
            print(f"No text extracted from {file_path} using pdfminer, falling back to OCR...")
            images = convert_from_bytes(file_content)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
                
        return text.strip()
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return ""

def get_resume_files(root_dir: str) -> List[Dict[str, str]]:
    """
    Get all PDF files from the data directory with their profession type.
    Returns a list of dicts with file path and profession type.
    """
    resume_files = []
    for profession_dir in Path(root_dir).glob('*'):
        if profession_dir.is_dir():
            profession_type = profession_dir.name
            for pdf_file in profession_dir.glob('*.pdf'):
                resume_files.append({
                    'file_path': str(pdf_file),
                    'profession_type': profession_type,
                    'file_name': pdf_file.name
                })
    return resume_files

def main():
    # Load environment variables
    load_dotenv()
    
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    # # Initialize connections and embeddings
    # conn = init_connection()
    # embeddings = GoogleGenerativeAIEmbeddings(
    #     model="models/text-embedding-004",
    #     google_api_key=os.getenv("GOOGLE_API_KEY")
    # )
    
    # Get all resume files
    data_dir = config["resume_dir"]
    resume_files = get_resume_files(data_dir)
    
    print(f"Found {len(resume_files)} resume files to process")
    
    # Process each resume
    for resume in resume_files:
        try:
            # Extract text from PDF using improved method
            text_content = extract_text_from_pdf(resume['file_path'])
            
            if not text_content:
                print(f"Skipping {resume['file_path']} - No content extracted")
                continue
            pprint(text_content)
            # Create embedding
            embedding = embeddings.embed_query(text_content)
            
            # Prepare data for insertion
            data = {
                'content': text_content,
                'profession_type': resume['profession_type'],
                'file_name': resume['file_name'],
                'file_path': resume['file_path'],
                'embedding': embedding
            }
            
            print(f"Inserting resume: {resume['file_name']} ({resume['profession_type']})")
            
            # Insert into Supabase
            conn.table("resumes").insert(data).execute()
            
            # Rate limiting to avoid overwhelming the API
            time.sleep(5)
            
        except Exception as e:
            print(f"Error processing {resume['file_path']}: {str(e)}")
            continue

if __name__ == "__main__":
    main()