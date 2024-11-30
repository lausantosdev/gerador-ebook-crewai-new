import pytest
from unittest.mock import MagicMock, patch
from src.models.book_models import BookOutline, ChapterOutline, Chapter

MOCK_CHAPTER_CONTENT = """# Introdução ao Python

Python é uma linguagem de programação versátil e amigável para iniciantes. Neste capítulo, vamos explorar:

1. O que é Python
2. Por que Python é uma excelente escolha para iniciantes
3. História e evolução da linguagem

## O que é Python?

Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. Foi criada por Guido van Rossum e lançada em 1991.

## Por que Python?

Python é fácil de aprender e possui uma comunidade ativa que desenvolve bibliotecas para praticamente qualquer necessidade.
Além disso, é utilizada em diversas áreas como desenvolvimento web, ciência de dados, automação e muito mais.

## História e Evolução

Python foi criada no início dos anos 90 e desde então tem evoluído constantemente.
Hoje é uma das linguagens mais populares do mundo, usada por empresas como Google, NASA, e muitas outras."""

@pytest.fixture
def mock_llm():
    """Mock do modelo de linguagem"""
    with patch('langchain_openai.ChatOpenAI') as mock_chat:
        mock_chat.return_value = MagicMock()
        mock_chat.return_value.invoke = MagicMock(return_value=MagicMock(content=MOCK_CHAPTER_CONTENT))
        yield mock_chat

@pytest.fixture
def mock_agent():
    """Mock do agente CrewAI"""
    with patch('crewai.Agent') as mock_agent:
        agent_instance = MagicMock()
        agent_instance.execute_task.return_value = MOCK_CHAPTER_CONTENT
        mock_agent.return_value = agent_instance
        yield mock_agent

@pytest.fixture
def mock_crew():
    """Mock do Crew"""
    with patch('crewai.Crew') as mock_crew:
        crew_instance = MagicMock()
        crew_instance.kickoff.return_value = {
            "title": "Introdução ao Python",
            "content": MOCK_CHAPTER_CONTENT
        }
        mock_crew.return_value = crew_instance
        yield mock_crew

@pytest.fixture
def mock_config():
    return {
        "researcher": {
            "role": "Researcher",
            "goal": "Research and analyze the topic",
            "backstory": "You are an expert researcher",
            "tools": ["web_search", "note_taking"]
        },
        "writer": {
            "role": "Writer",
            "goal": "Write book outline",
            "backstory": "You are an expert writer",
            "tools": []
        }
    }

@pytest.fixture
def mock_tasks_config():
    return {
        "research": {
            "description": "Research the topic {topic}",
            "expected_output": "Research findings",
            "agent": "researcher"
        },
        "write": {
            "description": "Write book outline based on research",
            "expected_output": "Book outline",
            "agent": "writer"
        }
    }

@pytest.fixture
def sample_chapter_data():
    """Dados de exemplo de um capítulo"""
    return {
        "title": "Introdução ao Python",
        "content": MOCK_CHAPTER_CONTENT
    }

@pytest.fixture
def sample_chapter(sample_chapter_data):
    return Chapter(**sample_chapter_data)

@pytest.fixture
def sample_book_data():
    return {
        "title": "Python para Iniciantes",
        "description": "Um guia completo de Python",
        "chapters": [
            {
                "title": "Introdução ao Python",
                "description": "Uma introdução à linguagem"
            }
        ],
        "target_audience": "Iniciantes em programação",
        "goal": "Ensinar programação básica com Python"
    }

@pytest.fixture
def sample_book(sample_book_data):
    return BookOutline(**sample_book_data)

@pytest.fixture(autouse=True)
def mock_openai():
    """Mock global do cliente OpenAI"""
    with patch('openai.OpenAI') as mock_openai, \
         patch('litellm.completion') as mock_completion:
        mock_openai.return_value = MagicMock()
        mock_completion.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=MOCK_CHAPTER_CONTENT
                    )
                )
            ]
        )
        yield mock_openai
  