import pytest
from pathlib import Path
from src.core.export.book_exporter import BookExporter
from src.models.book_models import BookState, Chapter, ChapterOutline

@pytest.fixture
def sample_book_state():
    """Fixture que retorna um estado de livro para teste"""
    return BookState(
        title="Python para Iniciantes",
        topic="Python",
        goal="Ensinar programação básica",
        target_audience="Iniciantes em programação",
        book=[
            Chapter(
                title="Introdução ao Python",
                content="""# Introdução ao Python

Python é uma linguagem versátil e poderosa que tem se tornado cada vez mais popular nos últimos anos.
Sua sintaxe clara e intuitiva a torna uma excelente escolha para iniciantes em programação.

## Por que Python?

Python é fácil de aprender e possui uma comunidade ativa que desenvolve bibliotecas para praticamente qualquer necessidade.
Além disso, é utilizada em diversas áreas como desenvolvimento web, ciência de dados, automação e muito mais."""
            ),
            Chapter(
                title="Variáveis e Tipos",
                content="""# Variáveis e Tipos

Em Python, variáveis são como caixas que guardam diferentes tipos de informações. É fundamental entender como elas funcionam.
Vamos explorar os principais tipos de dados e como trabalhar com eles de forma eficiente.

## Tipos Básicos

Python possui diversos tipos de dados integrados como números (int, float), texto (str), booleanos (bool) e muito mais.
Cada tipo tem suas próprias características e métodos que nos ajudam a manipular os dados de forma adequada."""
            )
        ],
        book_outline=[
            ChapterOutline(
                title="Introdução ao Python",
                description="Uma introdução à linguagem"
            ),
            ChapterOutline(
                title="Variáveis e Tipos",
                description="Conceitos básicos de variáveis"
            )
        ]
    )

def test_export_to_markdown(sample_book_state, tmp_path):
    """Testa a exportação para markdown"""
    exporter = BookExporter(sample_book_state)
    output_file = tmp_path / "book.md"
    
    exporter.export_markdown(output_file)
    
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    
    # Verifica conteúdo
    assert "# Python para Iniciantes" in content
    assert "# Introdução ao Python" in content
    assert "# Variáveis e Tipos" in content

def test_export_to_pdf(sample_book_state, tmp_path):
    """Testa a exportação para PDF"""
    exporter = BookExporter(sample_book_state)
    output_file = tmp_path / "book.pdf"
    
    exporter.export_pdf(output_file)
    
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_export_to_epub(sample_book_state, tmp_path):
    """Testa a exportação para EPUB"""
    exporter = BookExporter(sample_book_state)
    output_file = tmp_path / "book.epub"
    
    exporter.export_epub(output_file)
    
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_export_with_custom_template(sample_book_state, tmp_path):
    """Testa a exportação com template personalizado"""
    template = """
    # {title}
    
    Por: AI Author
    
    {content}
    """
    
    exporter = BookExporter(sample_book_state)
    output_file = tmp_path / "book.md"
    
    exporter.export_markdown(output_file, template=template)
    
    content = output_file.read_text(encoding='utf-8')
    assert "Por: AI Author" in content

def test_export_with_invalid_state():
    """Testa a exportação com estado inválido"""
    with pytest.raises(ValueError):
        BookExporter(None)
    
    empty_state = BookState(
        title="",
        topic="Python",
        goal="Ensinar",
        target_audience="Iniciantes"
    )
    with pytest.raises(ValueError):
        BookExporter(empty_state)

def test_export_with_invalid_path(sample_book_state):
    """Testa a exportação com caminho inválido"""
    exporter = BookExporter(sample_book_state)
    
    with pytest.raises(ValueError):
        exporter.export_markdown("")
    
    with pytest.raises(ValueError):
        exporter.export_pdf(None)
    
    with pytest.raises(ValueError):
        exporter.export_epub("invalid/path/without/extension") 