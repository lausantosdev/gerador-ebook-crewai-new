import pytest
from unittest.mock import MagicMock, patch
from src.crews.write_crew.write_crew import WriteChapterCrew
from src.models.book_models import Chapter

MOCK_CHAPTER_CONTENT = """# Introdução ao Python

## O que é Python?

Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.

## Por que Python?

Python é conhecida por sua sintaxe clara e legível.

## Primeiros Passos

Vamos começar com um exemplo simples:

```python
print("Olá, mundo!")
```
"""

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

Este capítulo aborda o uso do Python no mercado:

## Cases de Sucesso

Vamos analisar alguns cases de negócio.

## Impacto no Mercado

Como Python está transformando o mercado."""

MOCK_EDUCATIONAL_CONTENT = """# Aprendendo Python

Este capítulo apresenta conceitos educacionais:

## Conceitos Básicos

Aprenda os fundamentos da linguagem.

## Exercícios

Pratique com estes exercícios."""

@pytest.fixture
def write_crew():
    """Fixture que retorna uma instância de WriteChapterCrew"""
    return WriteChapterCrew(
        chapter_title="Introdução ao Python",
        topic="Python",
        chapter_description="Uma introdução gentil à linguagem Python",
        target_audience="Iniciantes em programação",
        goal="Ensinar conceitos básicos"
    )

def test_initialization(write_crew):
    """Testa a inicialização do crew"""
    assert write_crew.inputs["chapter_title"] == "Introdução ao Python"
    assert write_crew.inputs["topic"] == "Python"
    assert write_crew.inputs["chapter_description"] == "Uma introdução gentil à linguagem Python"
    assert write_crew.inputs["target_audience"] == "Iniciantes em programação"
    assert write_crew.inputs["goal"] == "Ensinar conceitos básicos"

def test_invalid_initialization():
    """Testa a inicialização com dados inválidos"""
    with pytest.raises(ValueError):
        WriteChapterCrew(
            chapter_title="",  # título vazio
            topic="Python",
            chapter_description="Descrição",
            target_audience="Iniciantes",
            goal="Ensinar"
        )

@patch('src.crews.write_crew.write_crew.Crew')
def test_successful_chapter_generation(mock_crew, write_crew):
    """Testa a geração bem-sucedida de um capítulo"""
    mock_instance = MagicMock()
    mock_instance.kickoff.return_value = {
        "title": write_crew.inputs["chapter_title"],
        "content": MOCK_CHAPTER_CONTENT
    }
    mock_crew.return_value = mock_instance
    
    chapter = write_crew.execute()
    assert isinstance(chapter, Chapter)
    assert chapter.title == write_crew.inputs["chapter_title"]
    assert len(chapter.content) > 0

@patch('src.crews.write_crew.write_crew.Crew')
def test_chapter_content_validation(mock_crew, write_crew):
    """Testa a validação do conteúdo do capítulo"""
    mock_instance = MagicMock()
    mock_instance.kickoff.return_value = {
        "title": write_crew.inputs["chapter_title"],
        "content": MOCK_CHAPTER_CONTENT
    }
    mock_crew.return_value = mock_instance
    
    chapter = write_crew.execute()
    assert "# " in chapter.content  # deve ter título principal
    assert "## " in chapter.content  # deve ter subtítulos
    assert len(chapter.content) >= 100  # tamanho mínimo

@patch('src.crews.write_crew.write_crew.Crew')
def test_markdown_structure(mock_crew, write_crew):
    """Testa a estrutura markdown do capítulo"""
    mock_instance = MagicMock()
    mock_instance.kickoff.return_value = {
        "title": write_crew.inputs["chapter_title"],
        "content": MOCK_CHAPTER_CONTENT
    }
    mock_crew.return_value = mock_instance
    
    chapter = write_crew.execute()
    lines = chapter.content.split("\n")
    
    # Deve ter título principal
    assert any(line.startswith("# ") for line in lines)
    
    # Deve ter pelo menos um subtítulo
    assert any(line.startswith("## ") for line in lines)
    
    # Deve ter parágrafos de texto
    assert any(line and not line.startswith("#") for line in lines)

@patch('src.crews.write_crew.write_crew.Crew')
def test_error_handling(mock_crew, write_crew):
    """Testa o tratamento de erros"""
    mock_instance = MagicMock()
    mock_instance.kickoff.side_effect = Exception("Erro simulado")
    mock_crew.return_value = mock_instance
    
    with pytest.raises(Exception):
        write_crew.execute()

@pytest.mark.parametrize("book_type,expected_style,mock_content", [
    ("technical", ["código", "exemplo", "prática"], MOCK_TECHNICAL_CONTENT),
    ("business", ["case", "mercado", "negócio"], MOCK_BUSINESS_CONTENT),
    ("educational", ["conceito", "aprenda", "exercício"], MOCK_EDUCATIONAL_CONTENT)
])
@patch('src.crews.write_crew.write_crew.Crew')
def test_content_style_by_book_type(mock_crew, book_type, expected_style, mock_content):
    """Testa se o estilo do conteúdo se adapta ao tipo do livro"""
    crew = WriteChapterCrew(
        chapter_title="Capítulo Teste",
        topic="Python",
        chapter_description=f"Capítulo no estilo {book_type}",
        target_audience="Público geral",
        goal="Testar estilos",
        book_type=book_type
    )
    
    mock_instance = MagicMock()
    mock_instance.kickoff.return_value = {
        "title": "Capítulo Teste",
        "content": mock_content
    }
    mock_crew.return_value = mock_instance
    
    chapter = crew.execute()
    content = chapter.content.lower()
    
    # Verifica se pelo menos uma das palavras-chave do estilo está presente
    assert any(word in content for word in expected_style)

def test_title_max_length():
    """Testa se título muito longo é rejeitado"""
    with pytest.raises(ValueError, match="Título muito longo"):
        WriteChapterCrew(
            chapter_title="A" * 201,  # título com 201 caracteres
            topic="Python",
            chapter_description="Descrição",
            target_audience="Iniciantes",
            goal="Ensinar"
        )

def test_description_max_length():
    """Testa se descrição muito longa é rejeitada"""
    with pytest.raises(ValueError, match="Descrição muito longa"):
        WriteChapterCrew(
            chapter_title="Título",
            topic="Python",
            chapter_description="A" * 1001,  # descrição com 1001 caracteres
            target_audience="Iniciantes",
            goal="Ensinar conceitos básicos de programação"  # objetivo válido com mais de 10 caracteres
        )

def test_invalid_characters_in_title():
    """Testa se caracteres especiais no título são rejeitados"""
    invalid_titles = [
        "Título/com/barras",
        "Título\\com\\backslash",
        "Título<com>tags",
        'Título"com"aspas',
        "Título*com*asterisco"
    ]
    
    for title in invalid_titles:
        with pytest.raises(ValueError, match="Caracteres inválidos no título"):
            WriteChapterCrew(
                chapter_title=title,
                topic="Python",
                chapter_description="Descrição",
                target_audience="Iniciantes",
                goal="Ensinar"
            )

def test_invalid_book_type():
    """Testa se tipo de livro inválido é rejeitado"""
    with pytest.raises(ValueError, match="Tipo de livro inválido"):
        WriteChapterCrew(
            chapter_title="Título",
            topic="Python",
            chapter_description="Descrição",
            target_audience="Iniciantes",
            goal="Ensinar",
            book_type="tipo_invalido"  # tipo que não existe
        )

def test_empty_topic():
    """Testa se tópico vazio é rejeitado"""
    with pytest.raises(ValueError, match="Tópico não pode estar vazio"):
        WriteChapterCrew(
            chapter_title="Título",
            topic="",  # tópico vazio
            chapter_description="Descrição",
            target_audience="Iniciantes",
            goal="Ensinar"
        )

def test_empty_target_audience():
    """Testa se público-alvo vazio é rejeitado"""
    with pytest.raises(ValueError, match="Público-alvo não pode estar vazio"):
        WriteChapterCrew(
            chapter_title="Título",
            topic="Python",
            chapter_description="Descrição",
            target_audience="",  # público-alvo vazio
            goal="Ensinar"
        )

def test_empty_goal():
    """Testa se objetivo vazio é rejeitado"""
    with pytest.raises(ValueError, match="Objetivo não pode estar vazio"):
        WriteChapterCrew(
            chapter_title="Título",
            topic="Python",
            chapter_description="Descrição",
            target_audience="Iniciantes",
            goal=""  # objetivo vazio
        )