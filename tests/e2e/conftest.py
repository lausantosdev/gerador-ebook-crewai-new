import pytest
from unittest.mock import MagicMock, patch
from langchain_openai import ChatOpenAI
from crewai import Agent
from src.models.book_models import BookOutline, Chapter
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.crews.write_crew.write_crew import WriteChapterCrew

# Mock das respostas do LLM
MOCK_OUTLINE = BookOutline(
    title="Python para Iniciantes: Um Guia Prático",
    description="Este livro foi projetado para introduzir programação usando Python de forma clara e acessível.",
    target_audience="Iniciantes em programação",
    goal="Ensinar programação básica",
    chapters=[
        {
            "title": "Introdução ao Python",
            "description": "Uma introdução gentil à linguagem Python, sua história e por que é excelente para iniciantes."
        },
        {
            "title": "Configurando seu Ambiente",
            "description": "Como instalar Python e configurar seu ambiente de desenvolvimento."
        },
        {
            "title": "Conceitos Básicos",
            "description": "Variáveis, tipos de dados e operações básicas em Python."
        }
    ]
)

MOCK_CHAPTER_CONTENT = """# Introdução ao Python

Python é uma linguagem de programação versátil e amigável para iniciantes. Neste capítulo, vamos explorar:

1. O que é Python
2. Por que Python é uma excelente escolha para iniciantes
3. História e evolução da linguagem
4. Instalação e configuração
5. Primeiros passos com Python

## O que é Python?

Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. Foi criada por Guido van Rossum e lançada em 1991.
Algumas características que tornam Python especial:

- Sintaxe clara e legível
- Grande comunidade ativa
- Vasta biblioteca padrão
- Multiplataforma (Windows, Linux, Mac)
- Gratuita e open source

## Por que Python?

Python é fácil de aprender e possui uma comunidade ativa que desenvolve bibliotecas para praticamente qualquer necessidade.
Além disso, é utilizada em diversas áreas como:

1. Desenvolvimento Web
   - Django
   - Flask
   - FastAPI

2. Ciência de Dados
   - Pandas
   - NumPy
   - Scikit-learn

3. Automação
   - Selenium
   - PyAutoGUI
   - Beautiful Soup

4. Inteligência Artificial
   - TensorFlow
   - PyTorch
   - Keras

## História e Evolução

Python foi criada no início dos anos 90 e desde então tem evoluído constantemente.
Hoje é uma das linguagens mais populares do mundo, usada por empresas como:

- Google
- NASA
- Instagram
- Spotify
- Netflix

### Versões Principais

- Python 1.0 (1994)
- Python 2.0 (2000)
- Python 3.0 (2008)
- Python 3.11 (Atual)

## Instalação e Configuração

Para começar a programar em Python, você precisa:

1. Baixar o Python
   - Acesse python.org
   - Escolha a versão mais recente
   - Siga o instalador

2. Configurar o Ambiente
   - IDE recomendada: VS Code
   - Extensões úteis
   - Terminal integrado

3. Testar a Instalação
   ```python
   print("Olá, Python!")
   ```

## Primeiros Passos

Vamos começar com alguns conceitos básicos:

1. Variáveis
   ```python
   nome = "Maria"
   idade = 25
   altura = 1.65
   ```

2. Operações Básicas
   ```python
   soma = 10 + 5
   multiplicacao = 3 * 4
   divisao = 15 / 3
   ```

3. Estruturas de Controle
   ```python
   if idade >= 18:
       print("Maior de idade")
   else:
       print("Menor de idade")
   ```

4. Loops
   ```python
   for i in range(5):
       print(f"Contagem: {i}")
   ```

### Exercícios Práticos

1. Crie um programa que calcule a média de três números
2. Faça um script que converta temperatura de Celsius para Fahrenheit
3. Desenvolva um programa que verifique se um número é par ou ímpar

## Recursos Adicionais

- Documentação oficial: docs.python.org
- Tutoriais online gratuitos
- Comunidades e fóruns
- Livros recomendados

## Próximos Passos

Após dominar os conceitos básicos, você pode:

1. Aprofundar em uma área específica
2. Trabalhar em projetos pessoais
3. Contribuir com projetos open source
4. Participar de comunidades Python

Lembre-se: a prática é fundamental para o aprendizado. Dedique tempo para experimentar e criar seus próprios programas."""

MOCK_TECHNICAL_CONTENT = """# Python para Desenvolvedores

Este capítulo aborda aspectos técnicos do Python:

```python
def exemplo_codigo():
    print("Exemplo de código Python")
    return True
```

## Exemplos Práticos

Vamos ver alguns exemplos práticos de implementação."""

MOCK_BUSINESS_CONTENT = """# Python nos Negócios

Este capítulo apresenta casos de uso do Python no mercado:

## Cases de Sucesso

- Case 1: Como o mercado financeiro usa Python
- Case 2: Python no e-commerce

## Impacto nos Negócios

Python tem revolucionado o mercado de tecnologia."""

MOCK_EDUCATIONAL_CONTENT = """# Aprenda Python

Neste capítulo você vai aprender os conceitos fundamentais:

## Exercícios Práticos

1. Primeiro exercício: variáveis
2. Segundo exercício: funções

## Conceitos Importantes

Vamos explorar cada conceito detalhadamente."""

class MockChatOpenAI:
    """Mock personalizado para o ChatOpenAI"""
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):
        return MOCK_CHAPTER_CONTENT

    def complete(self, *args, **kwargs):
        return MOCK_CHAPTER_CONTENT

    def __call__(self, *args, **kwargs):
        return self

@pytest.fixture(autouse=True)
def mock_all_llm():
    """Fixture que mocka todas as possíveis chamadas ao LLM"""
    # Mock do OutlineCrew e WriteChapterCrew
    with patch.object(OutlineCrew, 'generate_outline') as mock_outline, \
         patch.object(WriteChapterCrew, 'execute') as mock_write, \
         patch('langchain_openai.ChatOpenAI', new=MockChatOpenAI), \
         patch('openai.OpenAI', new=MockChatOpenAI), \
         patch('litellm.completion') as mock_completion:
        
        # Configurar os mocks
        async def mock_outline_response(*args, **kwargs):
            if kwargs.get('topic') == 'error':
                raise Exception("Erro simulado")
            return MOCK_OUTLINE
            
        mock_outline.side_effect = mock_outline_response
        mock_write.return_value = Chapter(
            title="Capítulo Teste",
            content=MOCK_CHAPTER_CONTENT
        )
        mock_completion.return_value = MOCK_CHAPTER_CONTENT
        
        yield mock_outline, mock_write

@pytest.fixture(autouse=True)
def mock_serper():
    """Fixture que mocka o SerperDev para todos os testes e2e"""
    with patch('crewai_tools.SerperDevTool') as mock_serper:
        mock_instance = MagicMock()
        mock_instance._run.return_value = "Resultados da pesquisa mockados"
        mock_serper.return_value = mock_instance
        yield mock_serper

@pytest.fixture(autouse=True)
def mock_agent():
    """Fixture que mocka os agentes da CrewAI"""
    with patch('crewai.Agent') as mock_agent:
        agent_instance = MagicMock()
        agent_instance.execute_task.return_value = MOCK_CHAPTER_CONTENT
        mock_agent.return_value = agent_instance
        yield mock_agent

@pytest.fixture(autouse=True)
def mock_crew():
    """Fixture que mocka o Crew"""
    with patch('crewai.Crew') as mock_crew:
        crew_instance = MagicMock()
        crew_instance.kickoff.return_value = {
            "title": "Capítulo Teste",
            "content": MOCK_CHAPTER_CONTENT
        }
        mock_crew.return_value = crew_instance
        yield mock_crew