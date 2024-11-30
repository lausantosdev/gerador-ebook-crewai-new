import pytest
import time
import asyncio
from pathlib import Path
from src.models.book_models import BookState, Chapter, ChapterOutline
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.crews.write_crew.write_crew import WriteChapterCrew

@pytest.mark.e2e
class TestLimitsE2E:
    """Testes end-to-end para limites e performance"""

    @pytest.fixture
    def book_state(self):
        """Fixture que retorna um estado inicial do livro"""
        return BookState(
            title="Python para Iniciantes",
            topic="Python",
            goal="Ensinar programação básica",
            target_audience="Iniciantes em programação"
        )

    @pytest.mark.asyncio
    async def test_large_chapter_generation(self, book_state, mock_all_llm, mock_serper):
        """Testa a geração de capítulos muito grandes"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Gerar capítulo grande (mais de 1000 caracteres)
        write_crew = WriteChapterCrew(
            chapter_title=book_outline.chapters[0].title,
            topic=book_state.topic,
            chapter_description="Gere um capítulo detalhado com mais de 1000 caracteres",
            target_audience=book_state.target_audience,
            goal=book_state.goal
        )

        chapter = write_crew.execute()
        assert isinstance(chapter, Chapter)
        assert len(chapter.content) > 1000

    @pytest.mark.asyncio
    async def test_many_chapters_generation(self, book_state, mock_all_llm, mock_serper):
        """Testa a geração de muitos capítulos"""
        # 1. Gerar outline com muitos capítulos
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal="Criar um guia completo com mais de 3 capítulos",
            target_audience=book_state.target_audience
        )

        assert len(book_outline.chapters) >= 3

        # 2. Gerar alguns capítulos para testar performance
        start_time = time.time()
        for chapter_outline in book_outline.chapters[:3]:
            write_crew = WriteChapterCrew(
                chapter_title=chapter_outline.title,
                topic=book_state.topic,
                chapter_description=chapter_outline.description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            chapter = write_crew.execute()
            book_state.book.append(chapter)

        end_time = time.time()
        generation_time = end_time - start_time

        # Verificar se o tempo médio por capítulo é aceitável (menos de 60 segundos)
        assert generation_time / 3 < 60

    @pytest.mark.asyncio
    async def test_concurrent_generation(self, book_state, mock_all_llm, mock_serper):
        """Testa a geração concorrente de capítulos"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Gerar capítulos concorrentemente
        async def generate_chapter(chapter_outline):
            write_crew = WriteChapterCrew(
                chapter_title=chapter_outline.title,
                topic=book_state.topic,
                chapter_description=chapter_outline.description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            return write_crew.execute()

        # Adicionar delay artificial para simular processamento
        async def delayed_generate_chapter(chapter_outline):
            await asyncio.sleep(0.1)  # Delay artificial
            return await generate_chapter(chapter_outline)

        # Gerar sequencialmente primeiro
        start_time = time.time()
        for outline in book_outline.chapters[:3]:
            write_crew = WriteChapterCrew(
                chapter_title=outline.title,
                topic=book_state.topic,
                chapter_description=outline.description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            write_crew.execute()
        end_time = time.time()
        sequential_time = end_time - start_time

        # Gerar concorrentemente
        start_time = time.time()
        chapters = await asyncio.gather(*[
            delayed_generate_chapter(outline)
            for outline in book_outline.chapters[:3]
        ])
        end_time = time.time()
        concurrent_time = end_time - start_time

        # Verificar resultados
        assert len(chapters) == 3
        assert all(isinstance(chapter, Chapter) for chapter in chapters)
        
        # A geração concorrente deve ser pelo menos 10% mais rápida
        assert concurrent_time < sequential_time * 0.9

    @pytest.mark.asyncio
    async def test_memory_usage(self, book_state, mock_all_llm, mock_serper):
        """Testa o uso de memória durante a geração"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Gerar vários capítulos
        for i in range(3):
            write_crew = WriteChapterCrew(
                chapter_title=f"Capítulo {i+1}",
                topic=book_state.topic,
                chapter_description="Descrição do capítulo",
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            chapter = write_crew.execute()
            book_state.book.append(chapter)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # O aumento de memória não deve ser maior que 1GB
        assert memory_increase < 1024 * 1024 * 1024  # 1GB em bytes

    @pytest.mark.asyncio
    async def test_error_rate(self, book_state, mock_all_llm, mock_serper):
        """Testa a taxa de erro na geração"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Tentar gerar 5 capítulos e contar erros
        total_attempts = 5
        errors = 0

        for i in range(total_attempts):
            try:
                write_crew = WriteChapterCrew(
                    chapter_title=f"Capítulo {i+1}",
                    topic=book_state.topic,
                    chapter_description="Descrição do capítulo",
                    target_audience=book_state.target_audience,
                    goal=book_state.goal
                )
                chapter = write_crew.execute()
                book_state.book.append(chapter)
            except Exception:
                errors += 1

        error_rate = errors / total_attempts
        # Taxa de erro deve ser menor que 20%
        assert error_rate < 0.2