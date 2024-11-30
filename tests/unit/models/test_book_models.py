import pytest
from src.models.book_models import BookOutline, ChapterOutline, Chapter, BookState, OutputLanguage
from pydantic import ValidationError

class TestBookOutline:
    def test_book_outline_creation_success(self, sample_book_data):
        """Testa a criação de um BookOutline com dados válidos."""
        # Arrange
        sample_book_data.update({
            "target_audience": "Iniciantes em programação",
            "goal": "Ensinar programação básica",
            "description": "Um guia completo de Python"
        })
        
        # Act
        outline = BookOutline(**sample_book_data)

        # Assert
        assert outline.title == "Python para Iniciantes", "Título incorreto"
        assert outline.description == "Um guia completo de Python", "Descrição incorreta"
        assert len(outline.chapters) > 0, "Deve ter pelo menos um capítulo"
        assert outline.target_audience == "Iniciantes em programação", "Público-alvo incorreto"
        assert outline.goal == "Ensinar programação básica", "Objetivo incorreto"

    def test_book_outline_invalid_data(self):
        """Testa a validação de dados inválidos no BookOutline."""
        # Arrange
        invalid_data = {
            "title": "",
            "description": "Descrição",
            "chapters": [],
            "target_audience": "Iniciantes",
            "goal": "Ensinar Python"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            BookOutline(**invalid_data)
        
        error = str(exc_info.value)
        assert "title" in error or "chapters" in error, "Deveria falhar na validação do título ou capítulos"

    def test_book_outline_minimal_data(self):
        """Testa a criação de um BookOutline com dados mínimos válidos."""
        # Arrange
        minimal_data = {
            "title": "Python Básico",
            "description": "Guia básico de Python",
            "chapters": [{
                "title": "Introdução",
                "description": "Capítulo introdutório"
            }],
            "target_audience": "Iniciantes",
            "goal": "Aprender Python"
        }

        # Act
        outline = BookOutline(**minimal_data)

        # Assert
        assert outline.title == "Python Básico"
        assert outline.description == "Guia básico de Python"
        assert len(outline.chapters) == 1
        assert outline.chapters[0].title == "Introdução"

class TestChapterOutline:
    def test_chapter_outline_creation_success(self):
        """Testa a criação de um ChapterOutline com dados válidos."""
        # Arrange
        chapter_data = {
            "title": "Introdução ao Python",
            "description": "Conceitos básicos da linguagem"
        }

        # Act
        chapter = ChapterOutline(**chapter_data)

        # Assert
        assert chapter.title == "Introdução ao Python", "Título incorreto"
        assert chapter.description == "Conceitos básicos da linguagem", "Descrição incorreta"

    def test_chapter_outline_empty_fields(self):
        """Testa a validação de campos vazios no ChapterOutline."""
        # Arrange
        invalid_data = {
            "title": "",
            "description": ""
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ChapterOutline(**invalid_data)
        
        errors = exc_info.value.errors()
        error_messages = [str(err["msg"]).lower() for err in errors]
        assert any("should have at least 1 character" in msg for msg in error_messages), \
            f"Deveria validar campos vazios. Mensagens: {error_messages}"

class TestChapter:
    def test_chapter_creation_success(self):
        """Testa a criação de um Chapter com dados válidos."""
        # Arrange
        valid_data = {
            "title": "Introdução ao Python",
            "content": """# Introdução ao Python

## Conceitos Básicos
Neste capítulo vamos aprender os conceitos fundamentais da linguagem Python.
Este é um texto longo o suficiente para passar na validação de tamanho mínimo.
Vamos explorar vários aspectos importantes da programação em Python.

## Instalação e Configuração
Aprenda como instalar e configurar o Python em seu computador.
"""
        }

        # Act
        chapter = Chapter(**valid_data)

        # Assert
        assert chapter.title == valid_data["title"]
        assert chapter.content == valid_data["content"]

    def test_chapter_invalid_title(self):
        """Testa a validação de título inválido no Chapter."""
        # Arrange
        invalid_data = {
            "title": "",  # título vazio
            "content": "# Conteúdo\n\n## Seção\nTexto longo o suficiente para ser válido..."
        }

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Chapter(**invalid_data)
        assert "título deve ter" in str(exc_info.value).lower()

    def test_chapter_invalid_content(self):
        """Testa a validação de conteúdo inválido no Chapter."""
        # Arrange
        invalid_data = {
            "title": "Título Válido",
            "content": "Conteúdo sem formatação markdown"
        }

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Chapter(**invalid_data)
        error_message = str(exc_info.value).lower()
        assert "inválido ou muito curto" in error_message, \
            f"Deveria validar conteúdo inválido. Mensagem: {error_message}"

class TestBookState:
    def test_book_state_creation_success(self):
        """Testa a criação de um BookState com dados válidos."""
        # Arrange
        state_data = {
            "output_language": "pt-BR",
            "title": "Python para Iniciantes",
            "topic": "Python",
            "goal": "Ensinar programação básica",
            "target_audience": "Iniciantes em programação"
        }

        # Act
        state = BookState(**state_data)

        # Assert
        assert state.output_language == OutputLanguage.PORTUGUESE, "Idioma incorreto"
        assert state.title == "Python para Iniciantes", "Título incorreto"
        assert state.topic == "Python", "Tópico incorreto"
        assert isinstance(state.book, list), "Lista de capítulos deveria ser uma lista"
        assert isinstance(state.book_outline, list), "Outline deveria ser uma lista"

    def test_book_state_invalid_language(self):
        """Testa a validação de idioma inválido no BookState."""
        # Arrange
        invalid_data = {
            "output_language": "invalid-lang",
            "title": "Python para Iniciantes",
            "topic": "Python",
            "goal": "Ensinar programação básica",
            "target_audience": "Iniciantes em programação"
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            BookState(**invalid_data)
        
        errors = exc_info.value.errors()
        error_messages = [str(err["msg"]).lower() for err in errors]
        assert any("should be" in msg and ("pt-br" in msg or "en-us" in msg) for msg in error_messages), \
            f"Deveria validar idioma inválido. Mensagens: {error_messages}"