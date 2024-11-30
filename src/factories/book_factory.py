from pathlib import Path
from src.services.book_services import OpenAIService, BookSaver
from dependency_injector import containers, providers
from src.config import Config
from src.flows.book_flow import BookFlow
from src.core.config.settings import settings
from src.core.config.llm_config import get_llm
from langchain_openai import ChatOpenAI

class BookContainer(containers.DeclarativeContainer):
    """Container para injeção de dependências."""
    
    # Configurações
    config = providers.Singleton(Config)
    
    # LLM
    llm = providers.Singleton(get_llm)
    
    # Serviços
    openai_service = providers.Singleton(
        OpenAIService,
        llm=llm
    )
    
    book_saver = providers.Factory(
        BookSaver,
        output_dir=settings.OUTPUT_DIR
    )
    
    # Flow principal
    book_flow = providers.Singleton(
        BookFlow,
        outline_generator=openai_service,
        chapter_writer=openai_service,
        book_saver=book_saver
    ) 