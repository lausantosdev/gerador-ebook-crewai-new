import pytest
from pathlib import Path
from src.models.book_models import BookState, BookOutline, Chapter, OutputLanguage
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.crews.write_crew.write_crew import WriteChapterCrew


@pytest.mark.e2e
class TestBookGenerationE2E:
    """Testes end-to-end para geração de livros usando mocks"""

    @pytest.fixture
    def book_state(self):
        """Fixture que retorna um estado inicial do livro"""
        return BookState(
            title="Python para Iniciantes",
            topic="Python",
            goal="Ensinar programação básica",
            target_audience="Iniciantes em programação"
        )

    @pytest.fixture
    def output_dir(self):
        """Fixture que retorna o diretório de output"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        return output_dir

    @pytest.fixture
    def backup_dir(self):
        """Fixture que retorna o diretório de backup"""
        backup_dir = Path("backup")
        backup_dir.mkdir(exist_ok=True)
        return backup_dir

    @pytest.mark.asyncio
    async def test_generate_first_chapter(self, book_state, output_dir, backup_dir, mock_all_llm, mock_serper):
        """Testa a geração do primeiro capítulo do livro usando mocks"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        assert isinstance(book_outline, BookOutline)
        assert len(book_outline.chapters) > 0
        assert "Python" in book_outline.chapters[0].title

        # 2. Escrever primeiro capítulo
        write_crew = WriteChapterCrew(
            chapter_title=book_outline.chapters[0].title,
            topic=book_state.topic,
            chapter_description=book_outline.chapters[0].description,
            target_audience=book_state.target_audience,
            goal=book_state.goal
        )

        chapter = write_crew.execute()
        assert isinstance(chapter, Chapter)
        assert len(chapter.content) > 0
        assert "Python" in chapter.content

        # 3. Atualizar estado do livro
        book_state.book.append(chapter)
        assert len(book_state.book) == 1

    @pytest.mark.asyncio
    async def test_generate_multiple_chapters(self, book_state, output_dir, backup_dir, mock_all_llm, mock_serper):
        """Testa a geração de múltiplos capítulos do livro usando mocks"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        assert isinstance(book_outline, BookOutline)
        assert len(book_outline.chapters) > 0

        # 2. Escrever e revisar os dois primeiros capítulos
        for chapter_outline in book_outline.chapters[:2]:
            # Escrever capítulo
            write_crew = WriteChapterCrew(
                chapter_title=chapter_outline.title,
                topic=book_state.topic,
                chapter_description=chapter_outline.description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )

            chapter = write_crew.execute()
            assert isinstance(chapter, Chapter)
            assert len(chapter.content) > 0
            assert "Python" in chapter.content
            
            # Adicionar ao livro
            book_state.book.append(chapter)

        # 3. Verificar estado final
        book_state.book_outline = book_outline.chapters
        assert len(book_state.book) == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, book_state):
        """Testa o tratamento de erros durante a geração do livro"""
        # 1. Testar erro no OutlineCrew
        outline_crew = OutlineCrew()
        with pytest.raises(Exception):
            await outline_crew.generate_outline(
                topic="error",  # Tópico que gera erro
                goal=book_state.goal,
                target_audience=book_state.target_audience
            )

    @pytest.mark.asyncio
    async def test_complete_book_generation(self, book_state, output_dir, backup_dir, mock_all_llm, mock_serper):
        """Testa a geração completa do livro, incluindo todos os capítulos"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        assert isinstance(book_outline, BookOutline)
        assert len(book_outline.chapters) > 0

        # 2. Escrever todos os capítulos
        for chapter_outline in book_outline.chapters:
            write_crew = WriteChapterCrew(
                chapter_title=chapter_outline.title,
                topic=book_state.topic,
                chapter_description=chapter_outline.description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )

            chapter = write_crew.execute()
            book_state.book.append(chapter)

        # 3. Verificar livro completo
        assert len(book_state.book) == len(book_outline.chapters)
        assert all(isinstance(chapter, Chapter) for chapter in book_state.book)
        assert all(len(chapter.content) > 0 for chapter in book_state.book)

    @pytest.mark.asyncio
    async def test_different_languages(self, book_state, mock_all_llm, mock_serper):
        """Testa a geração de livros em diferentes idiomas"""
        # 1. Configurar para inglês
        book_state.output_language = OutputLanguage.ENGLISH
        
        # 2. Gerar outline em inglês
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        assert isinstance(book_outline, BookOutline)
        
        # 3. Escrever primeiro capítulo em inglês
        write_crew = WriteChapterCrew(
            chapter_title=book_outline.chapters[0].title,
            topic=book_state.topic,
            chapter_description=book_outline.chapters[0].description,
            target_audience=book_state.target_audience,
            goal=book_state.goal
        )

        chapter = write_crew.execute()
        assert isinstance(chapter, Chapter)

    @pytest.mark.asyncio
    async def test_backup_and_recovery(self, book_state, backup_dir, mock_all_llm, mock_serper):
        """Testa o sistema de backup e recuperação do estado do livro"""
        # 1. Gerar outline e primeiro capítulo
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        write_crew = WriteChapterCrew(
            chapter_title=book_outline.chapters[0].title,
            topic=book_state.topic,
            chapter_description=book_outline.chapters[0].description,
            target_audience=book_state.target_audience,
            goal=book_state.goal
        )

        chapter = write_crew.execute()
        book_state.book.append(chapter)
        book_state.book_outline = book_outline.chapters

        # 2. Salvar backup
        backup_file = backup_dir / f"{book_state.topic.lower().replace(' ', '_')}_backup.json"
        book_state.save_backup(backup_file)
        
        # 3. Carregar backup
        loaded_state = BookState.load_backup(backup_file)
        
        # 4. Verificar se estados são iguais
        assert loaded_state.title == book_state.title
        assert loaded_state.topic == book_state.topic
        assert len(loaded_state.book) == len(book_state.book)
        assert len(loaded_state.book_outline) == len(book_state.book_outline)