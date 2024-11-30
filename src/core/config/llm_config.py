from langchain_openai import ChatOpenAI
from src.core.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_llm():
    """
    Retorna uma instância configurada do LLM.
    Modelos disponíveis: gpt-4o, gpt-4o-mini, gpt-4, gpt-4-turbo, gpt-4o-realtime-preview
    """
    model_name = "gpt-4o"
    logger.info(f"Configurando LLM com modelo: {model_name}")
    
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=settings.OPENAI_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )
    
    logger.debug(f"LLM configurado com modelo: {llm.model_name}")
    return llm 