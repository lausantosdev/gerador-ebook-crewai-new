import pytest
from src.core.parsers.markdown_parser import parse_markdown_to_book_outline
from src.models.book_models import BookOutline

def test_parse_markdown_to_book_outline():
    """Testa a conversão de markdown para BookOutline"""
    # Arrange
    markdown = """**Python para Iniciantes**

Um guia completo para aprender Python do zero.

## Capítulo 1: Introdução ao Python
Neste capítulo vamos conhecer a linguagem Python e seu ecossistema.

## Capítulo 2: Variáveis e Tipos de Dados
Aprenda sobre os tipos básicos de dados em Python e como trabalhar com variáveis."""

    # Act
    result = parse_markdown_to_book_outline(markdown)
    outline = BookOutline(**result)

    # Assert
    assert outline.title == "Python para Iniciantes"
    assert outline.description == "Um guia completo para aprender Python do zero."
    assert len(outline.chapters) == 2
    assert outline.chapters[0].title == "Introdução ao Python"
    assert outline.chapters[1].title == "Variáveis e Tipos de Dados"

def test_parse_markdown_alternative_format():
    """Testa a conversão de markdown em formato alternativo"""
    # Arrange
    markdown = """**Guia Python**

Um guia prático de Python.

## Fundamentos
Conceitos fundamentais da linguagem.

## Estruturas de Dados
Principais estruturas de dados.

## Conclusão
Fechamento do guia."""

    # Act
    result = parse_markdown_to_book_outline(markdown)
    outline = BookOutline(**result)

    # Assert
    assert outline.title == "Guia Python"
    assert outline.description == "Um guia prático de Python."
    assert len(outline.chapters) == 2  # Não deve incluir a conclusão
    assert outline.chapters[0].title == "Fundamentos"
    assert outline.chapters[1].title == "Estruturas de Dados"

def test_parse_markdown_invalid_input():
    """Testa a conversão com input inválido"""
    # Arrange
    markdown = "Texto sem formato adequado"

    # Act
    result = parse_markdown_to_book_outline(markdown)

    # Assert
    assert result["title"] == "Sem título"
    assert result["description"] == "Sem descrição"
    assert len(result["chapters"]) == 1  # Deve ter um capítulo padrão
    assert result["chapters"][0]["title"] == "Introdução"