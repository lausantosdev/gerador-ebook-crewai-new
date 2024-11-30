import pytest
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.crews.write_crew.write_crew import WriteChapterCrew
from src.crews.review_crew.review_crew import ReviewChapterCrew
from src.models.book_models import BookOutline, Chapter, BookState
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
class TestBookGeneration:
    @pytest.fixture
    def book_state(self):
        return BookState(
            title="Python para Iniciantes",
            topic="Python",
            goal="Ensinar programação básica",
            target_audience="Iniciantes em programação"
        )

    @pytest.fixture
    def mock_llm(self):
        return MagicMock()

    async def test_outline_to_write_flow(self, book_state, mock_llm, sample_book_data, sample_chapter_data):
        """Testa o fluxo do OutlineCrew para o WriteCrew"""
        # Mock do OutlineCrew
        with patch('src.crews.outline_crew.outline_crew.ChatOpenAI', return_value=mock_llm):
            outline_crew = OutlineCrew()
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = sample_book_data
            
            with patch.object(outline_crew, 'crew', return_value=mock_crew):
                book_outline = await outline_crew.generate_outline(
                    topic=book_state.topic,
                    goal=book_state.goal,
                    target_audience=book_state.target_audience
                )
                
                assert isinstance(book_outline, BookOutline)
                assert book_outline.title == sample_book_data["title"]
                assert len(book_outline.chapters) == len(sample_book_data["chapters"])

        # Mock do WriteCrew
        with patch('src.crews.write_crew.write_crew.ChatOpenAI', return_value=mock_llm):
            write_crew = WriteChapterCrew(
                chapter_title=book_outline.chapters[0].title,
                topic=book_state.topic,
                chapter_description=book_outline.chapters[0].description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = sample_chapter_data
            
            with patch.object(write_crew, 'crew', return_value=mock_crew):
                result = write_crew.crew().kickoff()
                chapter = Chapter(**result)
                
                assert isinstance(chapter, Chapter)
                assert chapter.title == sample_chapter_data["title"]
                assert chapter.content == sample_chapter_data["content"]

    async def test_write_to_review_flow(self, book_state, mock_llm, sample_chapter_data):
        """Testa o fluxo do WriteCrew para o ReviewCrew"""
        # Mock do WriteCrew
        with patch('src.crews.write_crew.write_crew.ChatOpenAI', return_value=mock_llm):
            write_crew = WriteChapterCrew(
                chapter_title="Introdução ao Python",
                topic=book_state.topic,
                chapter_description="Conceitos básicos da linguagem",
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = sample_chapter_data
            
            with patch.object(write_crew, 'crew', return_value=mock_crew):
                result = write_crew.crew().kickoff()
                chapter = Chapter(**result)
                
                assert isinstance(chapter, Chapter)
                assert chapter.title == sample_chapter_data["title"]

        # Mock do ReviewCrew
        improved_chapter = {
            "title": "Título Melhorado",
            "content": """# Título Melhorado

## Introdução
Este é um capítulo melhorado que demonstra as correções feitas.
O conteúdo foi revisado e aprimorado para melhor clareza.

## Conteúdo Principal
Aqui está o conteúdo principal com explicações mais detalhadas.

### Exemplos
1. Exemplo melhorado um
2. Exemplo melhorado dois
3. Exemplo melhorado três

## Conclusão
Uma conclusão mais robusta e informativa."""
        }
        
        with patch('src.crews.review_crew.review_crew.ChatOpenAI', return_value=mock_llm):
            review_crew = ReviewChapterCrew(
                chapter=chapter,
                chapter_description="Conceitos básicos da linguagem",
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = improved_chapter
            
            with patch.object(review_crew, 'crew', return_value=mock_crew):
                result = review_crew.crew().kickoff()
                improved = Chapter(**result)
                
                assert isinstance(improved, Chapter)
                assert improved.title == improved_chapter["title"]
                assert improved.content == improved_chapter["content"]
                assert improved.content != chapter.content

    async def test_complete_book_generation_flow(self, book_state, mock_llm, sample_book_data, sample_chapter_data):
        """Testa o fluxo completo de geração de livro"""
        # 1. Gerar outline
        with patch('src.crews.outline_crew.outline_crew.ChatOpenAI', return_value=mock_llm):
            outline_crew = OutlineCrew()
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = sample_book_data
            
            with patch.object(outline_crew, 'crew', return_value=mock_crew):
                book_outline = await outline_crew.generate_outline(
                    topic=book_state.topic,
                    goal=book_state.goal,
                    target_audience=book_state.target_audience
                )
                
                assert isinstance(book_outline, BookOutline)

        # 2. Escrever primeiro capítulo
        with patch('src.crews.write_crew.write_crew.ChatOpenAI', return_value=mock_llm):
            write_crew = WriteChapterCrew(
                chapter_title=book_outline.chapters[0].title,
                topic=book_state.topic,
                chapter_description=book_outline.chapters[0].description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = sample_chapter_data
            
            with patch.object(write_crew, 'crew', return_value=mock_crew):
                result = write_crew.crew().kickoff()
                chapter = Chapter(**result)
                
                assert isinstance(chapter, Chapter)

        # 3. Revisar e melhorar o capítulo
        improved_chapter = {
            "title": "Título Melhorado",
            "content": """# Título Melhorado

## Introdução
Este é um capítulo melhorado que demonstra as correções feitas.
O conteúdo foi revisado e aprimorado para melhor clareza.

## Conteúdo Principal
Aqui está o conteúdo principal com explicações mais detalhadas.

### Exemplos
1. Exemplo melhorado um
2. Exemplo melhorado dois
3. Exemplo melhorado três

## Conclusão
Uma conclusão mais robusta e informativa."""
        }
        
        with patch('src.crews.review_crew.review_crew.ChatOpenAI', return_value=mock_llm):
            review_crew = ReviewChapterCrew(
                chapter=chapter,
                chapter_description=book_outline.chapters[0].description,
                target_audience=book_state.target_audience,
                goal=book_state.goal
            )
            
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = improved_chapter
            
            with patch.object(review_crew, 'crew', return_value=mock_crew):
                result = review_crew.crew().kickoff()
                improved = Chapter(**result)
                
                assert isinstance(improved, Chapter)
                assert improved.title == improved_chapter["title"]
                assert improved.content == improved_chapter["content"]

        # 4. Verificar estado final
        book_state.book_outline = book_outline.chapters
        book_state.book.append(improved)
        
        assert len(book_state.book) == 1
        assert book_state.book[0].title == improved_chapter["title"]
        assert book_state.book[0].content == improved_chapter["content"]
        assert len(book_state.book_outline) == len(sample_book_data["chapters"])