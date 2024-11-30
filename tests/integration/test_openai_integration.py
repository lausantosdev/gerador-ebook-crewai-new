import pytest
from src.services.book_services import OpenAIService
from src.models.book_models import Chapter, ChapterOutline, ChapterLength
from openai import OpenAIError
import os

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key não configurada")
class TestOpenAIIntegration:
    """Testes de integração com a API da OpenAI."""

    @pytest.fixture
    def openai_service(self):
        """Fixture que retorna uma instância do serviço OpenAI."""
        return OpenAIService()

    @pytest.mark.asyncio
    async def test_api_connection(self, openai_service):
        """Testa a conexão básica com a API."""
        response = await openai_service.test_connection()
        assert response is True

    @pytest.mark.asyncio
    async def test_chapter_generation(self, openai_service):
        """Testa a geração de um capítulo simples."""
        outline = ChapterOutline(
            title="Introdução ao Python",
            description="Uma introdução gentil à linguagem Python",
            topics=["O que é Python", "Por que Python", "Instalação"],
            expected_length=ChapterLength.CURTO
        )
        context = {
            "goal": "Criar um livro educacional sobre Python",
            "topic": "Python",
            "target_audience": "Iniciantes"
        }
        
        chapter = await openai_service.generate_chapter(outline, context)
        assert isinstance(chapter, Chapter)
        assert len(chapter.content) > 100
        assert "# Introdução ao Python" in chapter.content

    @pytest.mark.asyncio
    async def test_token_limit_handling(self, openai_service):
        """Testa o tratamento de limites de tokens."""
        # Tenta gerar um capítulo muito grande
        outline = ChapterOutline(
            title="Capítulo Extenso",
            description="Um capítulo muito longo para testar limites",
            topics=["Tópico " + str(i) for i in range(50)],
            expected_length=ChapterLength.MUITO_LONGO
        )
        context = {
            "goal": "Testar limites",
            "topic": "Teste",
            "target_audience": "Desenvolvedores"
        }
        
        with pytest.raises(ValueError, match="Limite de tokens excedido"):
            await openai_service.generate_chapter(outline, context)

    @pytest.mark.asyncio
    async def test_error_handling(self, openai_service):
        """Testa o tratamento de erros da API."""
        # Força um erro usando uma chave inválida temporariamente
        original_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "invalid"
        
        with pytest.raises(OpenAIError):
            await openai_service.test_connection()
        
        # Restaura a chave original
        os.environ["OPENAI_API_KEY"] = original_key

    @pytest.mark.asyncio
    async def test_content_validation(self, openai_service):
        """Testa a validação do conteúdo gerado."""
        outline = ChapterOutline(
            title="Teste de Validação",
            description="Capítulo para testar validação",
            topics=["Tópico 1", "Tópico 2"],
            expected_length=ChapterLength.CURTO
        )
        context = {
            "goal": "Testar validação",
            "topic": "Teste",
            "target_audience": "Desenvolvedores"
        }
        
        chapter = await openai_service.generate_chapter(outline, context)
        
        # Verifica estrutura markdown
        assert chapter.content.startswith("#")
        assert "##" in chapter.content
        assert "```" in chapter.content  # deve ter blocos de código