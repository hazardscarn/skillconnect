import os
import PyPDF2
import docx2txt
import streamlit as st

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

def save_uploaded_file(uploaded_file, directory):
    """Save uploaded file to specified directory"""
    if uploaded_file is not None:
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def get_file_type(file_path):
    """Get MIME type for file download"""
    extension = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain'
    }
    return mime_types.get(extension, 'application/octet-stream')