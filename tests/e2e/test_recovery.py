import pytest
from pathlib import Path
from src.models.book_models import BookState, Chapter, ChapterOutline
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.crews.write_crew.write_crew import WriteChapterCrew

@pytest.mark.e2e
class TestRecoveryE2E:
    """Testes end-to-end para recuperação após falhas"""

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
    def backup_dir(self):
        """Fixture que retorna o diretório de backup"""
        backup_dir = Path("backup")
        backup_dir.mkdir(exist_ok=True)
        return backup_dir

    @pytest.mark.asyncio
    async def test_recovery_after_outline_failure(self, book_state, backup_dir, mock_all_llm, mock_serper):
        """Testa a recuperação após falha na geração do outline"""
        # 1. Simular falha na primeira tentativa
        outline_crew = OutlineCrew()
        with pytest.raises(Exception):
            await outline_crew.generate_outline(
                topic="error",
                goal=book_state.goal,
                target_audience=book_state.target_audience
            )

        # 2. Segunda tentativa deve funcionar
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        assert book_outline is not None
        assert len(book_outline.chapters) > 0

    @pytest.mark.asyncio
    async def test_recovery_after_chapter_failure(self, book_state, backup_dir, mock_all_llm, mock_serper):
        """Testa a recuperação após falha na escrita de capítulo"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Simular falha na escrita do primeiro capítulo
        with pytest.raises(ValueError):
            write_crew = WriteChapterCrew(
                chapter_title="",  # título inválido para forçar erro
                topic=book_state.topic,
                chapter_description=book_outline.chapters[0].description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )

        # 3. Segunda tentativa com título correto deve funcionar
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

    @pytest.mark.asyncio
    async def test_recovery_from_backup(self, book_state, backup_dir, mock_all_llm, mock_serper):
        """Testa a recuperação a partir de um backup"""
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

        # 3. Simular perda de dados
        book_state.book = []
        book_state.book_outline = []

        # 4. Recuperar do backup
        recovered_state = BookState.load_backup(backup_file)
        assert len(recovered_state.book) == 1
        assert len(recovered_state.book_outline) == len(book_outline.chapters)

    @pytest.mark.asyncio
    async def test_recovery_with_partial_progress(self, book_state, backup_dir, mock_all_llm, mock_serper):
        """Testa a recuperação com progresso parcial"""
        # 1. Gerar outline
        outline_crew = OutlineCrew()
        book_outline = await outline_crew.generate_outline(
            topic=book_state.topic,
            goal=book_state.goal,
            target_audience=book_state.target_audience
        )

        # 2. Escrever primeiro capítulo e salvar
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

        backup_file = backup_dir / f"{book_state.topic.lower().replace(' ', '_')}_backup.json"
        book_state.save_backup(backup_file)

        # 3. Simular falha no segundo capítulo
        with pytest.raises(ValueError):
            write_crew = WriteChapterCrew(
                chapter_title="",  # título inválido
                topic=book_state.topic,
                chapter_description=book_outline.chapters[1].description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )

        # 4. Recuperar e continuar
        recovered_state = BookState.load_backup(backup_file)
        assert len(recovered_state.book) == 1

        # 5. Continuar com o segundo capítulo
        write_crew = WriteChapterCrew(
            chapter_title=book_outline.chapters[1].title,
            topic=book_state.topic,
            chapter_description=book_outline.chapters[1].description,
            target_audience=book_state.target_audience,
            goal=book_state.goal
        )

        chapter = write_crew.execute()
        recovered_state.book.append(chapter)
        assert len(recovered_state.book) == 2 