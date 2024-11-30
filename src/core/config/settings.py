import os
import sys
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum
from pathlib import Path
import logging
import warnings
from contextlib import redirect_stderr
import io

# Suprimir avisos do GLib
os.environ['GI_TYPELIB_WARNING'] = 'off'
os.environ['GIO_USE_VFS'] = 'local'
os.environ['GIO_USE_VOLUME_MONITOR'] = 'unix'
os.environ['GIO_EXTRA_MODULES'] = ''

# Redirecionar stderr temporariamente
with redirect_stderr(io.StringIO()):
    # Importações que podem gerar avisos do GLib
    import weasyprint
    import PIL

# Suprimir todos os avisos
warnings.filterwarnings('ignore')

# Configurar logging para suprimir avisos indesejados
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('gi').setLevel(logging.ERROR)

class OutputLanguage(str, Enum):
    """Linguagens suportadas para geração do ebook."""
    PORTUGUESE = "pt-BR"
    ENGLISH = "en-US"

class AppSettings(BaseSettings):
    """Configurações da aplicação."""
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    MODEL_NAME: str = Field(
        default="gpt-4o",
        description="Nome do modelo OpenAI a ser usado. Opções: gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-4o-realtime-preview"
    )
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="Temperatura para geração de texto")
    MAX_TOKENS: int = Field(default=3000, description="Número máximo de tokens")
    FREQUENCY_PENALTY: float = Field(default=0.0, description="Penalidade de frequência")
    PRESENCE_PENALTY: float = Field(default=0.0, description="Penalidade de presença")
    
    # Configurações de Paralelismo
    MAX_CONCURRENT_CHAPTERS: int = Field(default=3, description="Número máximo de capítulos gerados em paralelo")
    
    # Serper
    SERPER_API_KEY: str = Field(..., description="Serper API Key")
    
    # Configurações gerais
    DEFAULT_LANGUAGE: OutputLanguage = Field(default=OutputLanguage.PORTUGUESE, description="Linguagem padrão")
    
    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    OUTPUT_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "output")
    LOGS_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "logs")
    BACKUP_DIR: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.parent / "backup")
    
    # Logging
    LOG_LEVEL: int = Field(default=logging.DEBUG, description="Nível de log")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato do log"
    )
    LOG_FILE: str = Field(
        default_factory=lambda: str(Path(__file__).parent.parent.parent.parent / "logs" / "app.log")
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"
    
    def model_post_init(self, _):
        # Cria diretórios necessários
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

settings = AppSettings() 