import os
from pathlib import Path
from src.core.config.settings import settings

class Config:
    """Configurações da aplicação."""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.output_dir = settings.OUTPUT_DIR
        self.language = settings.DEFAULT_LANGUAGE
        self.model_name = settings.MODEL_NAME
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS