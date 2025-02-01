import importlib.metadata

packages = [
    'streamlit',
    'python-dotenv',
    'PyPDF2',
    'python-docx',
    'docx2txt',
    'pandas',
    'pyyaml',
    'langchain-core',
    'langgraph',
    'langchain-google-genai',
    'langchain-openai',
    'pydantic',
    'langchain'
]

for package in packages:
    try:
        version = importlib.metadata.version(package)
        print(f"{package}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{package}: Not installed")