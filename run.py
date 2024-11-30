import asyncio
import logging
import sys
import traceback
import os
from src.core.config.settings import settings
from src.core.config.llm_config import get_llm
from src.factories.book_factory import BookContainer

# Força o uso de UTF-8 no Windows silenciosamente
if sys.platform.startswith('win'):
    os.system('chcp 65001 > NUL')

# Redirecionar stderr para devnull
sys.stderr = open(os.devnull, 'w')

def setup_logging():
    # Configuração do handler de arquivo para todos os logs
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))

    # Configuração do handler de console apenas para INFO e ERROR
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    # Formatter simples para o console, sem timestamp
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    # Configuração do logger root
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        handlers=[file_handler, console_handler]
    )

    # Desabilitar logs de bibliotecas externas
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('weasyprint').setLevel(logging.WARNING)
    logging.getLogger('fontTools').setLevel(logging.WARNING)
    logging.getLogger('gi').setLevel(logging.ERROR)

def print_banner():
    print("\n" + "="*50)
    print("🚀 Gerador de Ebook - Iniciando...")
    print("="*50 + "\n")

def get_user_input(prompt: str) -> str:
    """Função auxiliar para coletar input do usuário com tratamento de erro."""
    try:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️ Por favor, insira um valor válido.")
        return get_user_input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ Erro ao ler entrada: {e}")
        return get_user_input(prompt)

async def main():
    # Configura logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🔄 Iniciando aplicação...")
    
    try:
        logger.info("🔍 Verificando configurações...")
        logger.debug(f"Diretório de logs: {settings.LOGS_DIR}")
        logger.debug(f"Diretório de saída: {settings.OUTPUT_DIR}")
        
        print_banner()
        
        # Inicializa o container de dependências
        logger.info("🔧 Inicializando container de dependências...")
        container = BookContainer()
        
        # Obtém o flow principal
        logger.info("📚 Inicializando flow principal...")
        book_flow = container.book_flow()
        
        # Exibe informação do modelo
        print(f"\n🤖 Utilizando modelo: gpt-4o\n")
        
        # Coleta inputs do usuário
        print("📚 Por favor, forneça as informações para gerar o ebook:\n")
        topic = get_user_input("Qual o tema do livro? ")
        target_audience = get_user_input("Qual o público-alvo? ")
        book_type = get_user_input("Qual o tipo do livro? ")
        
        print("\n🔄 Iniciando geração do ebook...\n")
        
        # Executa o flow
        result = await book_flow.execute(topic, target_audience, book_type)
        
        print("\n✅ Livro gerado com sucesso!")
        print(f"📁 Arquivo salvo em: {result.output_path}")
        
    except Exception as e:
        logger.error("❌ Erro durante a execução do programa:")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem do erro: {str(e)}")
        logger.error("Traceback completo:")
        for line in traceback.format_exc().split('\n'):
            logger.error(line)
        
        print("\n❌ Ocorreu um erro durante a geração do ebook.")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Detalhes: {str(e)}")
        print("\nPara mais detalhes, verifique o arquivo de log em:")
        print(f"{settings.LOG_FILE}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(0) 