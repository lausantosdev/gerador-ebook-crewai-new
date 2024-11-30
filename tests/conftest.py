import pytest
import asyncio
from unittest.mock import Mock
from src.models.book_models import Chapter

# Configuração global para testes assíncronos
def pytest_configure(config):
    """Configuração global do pytest."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para testes assíncronos."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_llm():
    """Fixture que retorna um mock do LLM."""
    mock = Mock()
    mock.predict = Mock()
    return mock

@pytest.fixture
def sample_chapter_data():
    return {
        'title': 'Introdução ao Python: Conceitos Básicos para Iniciantes',
        'content': '''
        # Introdução ao Python
        
        Python é uma linguagem de programação versátil e poderosa, conhecida por sua simplicidade e legibilidade.
        Este capítulo irá introduzir os conceitos básicos da linguagem Python para iniciantes em programação.
        
        ## Tópicos Abordados
        1. O que é Python
        2. Instalação e Configuração
        3. Sintaxe Básica
        4. Tipos de Dados
        5. Estruturas de Controle
        '''
    }

@pytest.fixture
def sample_chapter(sample_chapter_data):
    return Chapter(
        title=sample_chapter_data['title'],
        content=sample_chapter_data['content']
    )

@pytest.fixture
def sample_book_data():
    return {
        "title": "Python para Iniciantes",
        "description": "Um guia completo",
        "chapters": [{
            "title": "Introdução ao Python",
            "description": "Conceitos básicos da linguagem"
        }],
        "target_audience": "Iniciantes em programação",
        "goal": "Ensinar programação básica"
    } 