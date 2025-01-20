import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.database import init_connection
from typing import List, Dict, Optional
import numpy as np

def search_resumes(
    query: str,
    profession_type: Optional[str] = None,
    match_threshold: float = 0.3,
    match_count: int = 5
) -> List[Dict]:
    """
    Search for resumes based on a query string and optional profession filter.
    
    Args:
        query (str): The search query/job description
        profession_type (str, optional): Filter by profession type
        match_threshold (float): Minimum similarity threshold (0-1)
        match_count (int): Maximum number of results to return
    
    Returns:
        List[Dict]: List of matching resumes with their details and similarity scores
    """
    try:
        load_dotenv()
        
        # Initialize connections and embeddings
        conn = init_connection()
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create embedding for the query
        query_embedding = embeddings.embed_query(query)
        
        # Search for matching resumes
        response = conn.rpc(
            'match_resumes',
            {
                'query_embedding': query_embedding,
                'profession_filter': profession_type,
                'match_threshold': match_threshold,
                'match_count': match_count
            }
        ).execute()
        
        # Process results
        results = []
        for item in response.data:
            # Normalize similarity score to 0-1 range
            similarity = float(item['similarity'])
            # Add processed result
            results.append({
                'content': item['content'],
                'profession_type': item['profession_type'],
                'file_name': item['file_name'],
                'file_path': item['file_path'],
                'similarity': similarity
            })
        
        # Sort by similarity score descending
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []

def test_search():
    """Test function for resume search"""
    # Test search
    test_query = """
    Senior Financial Analyst position:
    - 5+ years of experience in financial analysis
    - Bachelor's degree in Finance or Accounting
    - Advanced Excel and financial modeling skills
    - Experience with financial reporting and forecasting
    """
    
    results = search_resumes(
        query=test_query,
        profession_type="Finance",
        match_threshold=0.3,
        match_count=3
    )
    
    print(f"\nFound {len(results)} matches:")
    for i, result in enumerate(results, 1):
        print(f"\nMatch #{i} - {result['similarity']:.1%} Match")
        print(f"Profession: {result['profession_type']}")
        print(f"File: {result['file_name']}")
        print("Content preview:", result['content'][:200], "...")

if __name__ == "__main__":
    test_search()