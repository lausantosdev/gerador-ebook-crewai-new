from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
from src.core.config.settings import OutputLanguage

class ChapterLength(str, Enum):
    """Tamanhos possíveis para um capítulo."""
    CURTO = "curto"
    MEDIO = "médio"
    LONGO = "longo"
    MUITO_LONGO = "muito longo"

class ChapterOutline(BaseModel):
    """Estrutura do outline de um capítulo."""
    title: str
    description: str
    topics: List[str]
    expected_length: ChapterLength

class Chapter(BaseModel):
    """Estrutura de um capítulo."""
    title: str
    content: str
    generation_time: Optional[float] = None  # tempo em segundos

class TimeMetrics(BaseModel):
    """Métricas de tempo do processo de geração."""
    start_time: datetime
    outline_generation_time: Optional[float] = None
    chapter_generation_times: Dict[str, float] = {}  # título do capítulo -> tempo em segundos
    total_generation_time: Optional[float] = None
    estimated_completion_time: Optional[datetime] = None

class Book(BaseModel):
    """Estrutura do livro."""
    title: str
    chapters: List[Chapter]
    language: OutputLanguage = OutputLanguage.PORTUGUESE

class BookState(BaseModel):
    """Estado do livro durante o processo de geração."""
    title: str
    topic: str
    goal: str
    target_audience: str
    language: OutputLanguage = OutputLanguage.PORTUGUESE
    book_outline: Optional[List[ChapterOutline]] = None
    book: Optional[List[Chapter]] = None
    output_path: Optional[str] = None
    time_metrics: TimeMetrics = TimeMetrics(start_time=datetime.now())
