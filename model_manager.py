from typing import Dict, Optional
import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

class ModelManager:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize ModelManager with config file"""
        load_dotenv()
        
        # Load configuration
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.models_config = self.config['models']
        self.available_models = {
            model_id: config 
            for model_id, config in self.models_config.items() 
            if config['available']
        }
        
        # Get default model
        self.default_model_id = next(
            (model_id for model_id, config in self.models_config.items() 
             if config['available'] and config['default']),
            None
        )

    def get_model_names(self) -> Dict[str, str]:
        """Get dictionary of available model IDs and their display names"""
        return {
            model_id: config['name']
            for model_id, config in self.available_models.items()
        }

    def get_model_description(self, model_id: str) -> str:
        """Get description for a specific model"""
        return self.models_config[model_id].get('description', '')

    def get_model_pricing(self, model_id: str) -> Dict[str, float]:
        """Get pricing information for a specific model"""
        return self.models_config[model_id].get('pricing', {})

    def initialize_model(self, model_id: Optional[str] = None) -> any:
        """Initialize and return the specified model or default model"""
        if model_id is None:
            model_id = self.default_model_id
        
        if model_id not in self.available_models:
            raise ValueError(f"Model {model_id} is not available")
        
        config = self.models_config[model_id]
        provider = config['provider']
        
        if provider == 'google':
            return ChatGoogleGenerativeAI(
                model=config['model_id'],
                temperature=config['temperature'],
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        elif provider == 'openai':
            return ChatOpenAI(
                model=config['model_id'],
                temperature=config['temperature'],
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_default_model_id(self) -> str:
        """Get the default model ID"""
        return self.default_model_id