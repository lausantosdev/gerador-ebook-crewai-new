import asyncio
import logging
from pathlib import Path
from src.flows.book_flow import BookFlow
from src.services.book_services import OpenAIService, PDFBookSaver
from src.core.config.settings import settings

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ebook_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def generate_ebook(
    topic: str,
    target_audience: str,
    book_type: str = "educational"
) -> None:
    """
    Gera um ebook sobre o tópico especificado.
    
    Args:
        topic: Tópico principal do livro
        target_audience: Público-alvo do livro
        book_type: Tipo do livro (educational, technical, business)
    """
    try:
        # Inicializa serviços
        openai_service = OpenAIService()
        book_saver = PDFBookSaver(output_dir=Path("output"))
        
        # Cria o fluxo
        flow = BookFlow(
            outline_generator=openai_service,
            chapter_writer=openai_service,
            book_saver=book_saver
        )
        
        # Executa a geração
        logger.info(f"Iniciando geração do ebook sobre {topic}")
        state = await flow.execute(topic, target_audience, book_type)
        
        logger.info(f"Ebook gerado com sucesso: {state.title}")
        logger.info(f"Total de capítulos: {len(state.book)}")
        logger.info(f"Arquivo salvo em: output/{state.title}.pdf")
        
    except Exception as e:
        logger.error(f"Erro na geração do ebook: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    # Exemplo de uso
    asyncio.run(generate_ebook(
        topic="Python para Iniciantes",
        target_audience="Programadores iniciantes",
        book_type="educational"
    )) 