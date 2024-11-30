from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.book_models import Chapter, ChapterOutline

class IBookOutlineGenerator(ABC):
    """Interface para geração de outline do livro."""
    
    @abstractmethod
    async def generate_outline(
        self,
        topic: str,
        goal: str,
        target_audience: str
    ) -> List[ChapterOutline]:
        """Gera o outline do livro."""
        pass

class IChapterWriter(ABC):
    """Interface para escrita de capítulos."""
    
    @abstractmethod
    async def write_chapter(
        self,
        outline: ChapterOutline,
        context: Dict[str, Any]
    ) -> Chapter:
        """Escreve um capítulo do livro."""
        pass

class IBookSaver(ABC):
    """Interface para salvar o livro."""
    
    @abstractmethod
    async def save_pdf(self, state: Any, filename: str) -> None:
        """Salva o livro em PDF."""
        pass
    
    @abstractmethod
    async def save_backup(self, state: Any, filename: str) -> None:
        """Salva um backup do estado em formato markdown."""
        pass