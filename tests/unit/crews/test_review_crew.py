import pytest
from unittest.mock import Mock, patch, MagicMock
from src.crews.review_crew.review_crew import ReviewChapterCrew
from src.models.book_models import Chapter
from crewai import Crew, Process

@pytest.mark.asyncio
class TestReviewChapterCrew:
    @pytest.fixture
    def review_crew(self, mock_llm, mock_config, mock_tasks_config, sample_chapter):
        with patch('src.crews.review_crew.review_crew.ChatOpenAI', return_value=mock_llm), \
             patch.object(ReviewChapterCrew, 'agents_config', mock_config), \
             patch.object(ReviewChapterCrew, 'tasks_config', mock_tasks_config):
            
            crew = ReviewChapterCrew(
                chapter=sample_chapter,
                chapter_description="Conceitos básicos da linguagem Python",
                target_audience="Iniciantes em programação",
                goal="Ensinar programação básica",
                book_type="technical"
            )
            return crew

    async def test_initialization(self, review_crew, sample_chapter):
        """Testa a inicialização correta do ReviewCrew"""
        assert review_crew.chapter == sample_chapter
        assert review_crew.inputs["chapter_title"] == sample_chapter.title
        assert review_crew.inputs["chapter_description"] == "Conceitos básicos da linguagem Python"
        assert review_crew.inputs["target_audience"] == "Iniciantes em programação"
        assert review_crew.inputs["goal"] == "Ensinar programação básica"
        assert review_crew.inputs["book_type"] == "technical"

    async def test_invalid_initialization(self, sample_chapter_data):
        """Testa a inicialização com parâmetros inválidos"""
        with pytest.raises(ValueError) as exc_info:
            ReviewChapterCrew(
                chapter=None,  # capítulo inválido
                chapter_description="Descrição",
                target_audience="Público",
                goal="Objetivo",
                book_type="technical"
            )
        assert "capítulo" in str(exc_info.value).lower()

        with pytest.raises(ValueError) as exc_info:
            ReviewChapterCrew(
                chapter=sample_chapter_data,  # não é instância de Chapter
                chapter_description="Descrição",
                target_audience="Público",
                goal="Objetivo",
                book_type="technical"
            )
        assert "capítulo" in str(exc_info.value).lower()

    async def test_reviewer_agent_creation(self, review_crew):
        """Testa a criação do agente revisor"""
        reviewer = review_crew.reviewer()
        assert reviewer is not None
        assert not reviewer.tools  # revisor não deve ter ferramentas
        assert reviewer.llm is not None

    async def test_editor_agent_creation(self, review_crew):
        """Testa a criação do agente editor"""
        editor = review_crew.editor()
        assert editor is not None
        assert not editor.tools  # editor não deve ter ferramentas
        assert editor.llm is not None

    async def test_review_task_creation(self, review_crew):
        """Testa a criação da tarefa de revisão"""
        task = review_crew.review_chapter()
        assert task is not None
        assert review_crew.inputs["chapter_title"] in task.description
        assert review_crew.inputs["chapter_description"] in task.description
        assert "Review the chapter" in task.description
        assert "Chapter Content:" in task.description
        assert review_crew.chapter.content in task.description

    async def test_improve_task_creation(self, review_crew):
        """Testa a criação da tarefa de melhoria"""
        task = review_crew.improve_chapter()
        assert task is not None
        assert review_crew.inputs["chapter_title"] in task.description
        assert review_crew.inputs["chapter_description"] in task.description
        assert "Improve the chapter" in task.description
        assert "Chapter Content:" in task.description
        assert review_crew.chapter.content in task.description
        assert task.output_pydantic == Chapter

    async def test_successful_review_and_improvement(self, review_crew, sample_chapter_data):
        """Testa o fluxo completo de revisão e melhoria"""
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
        
        mock_crew = MagicMock(spec=Crew)
        mock_crew.kickoff.return_value = improved_chapter
        
        with patch.object(review_crew, 'crew', return_value=mock_crew):
            result = review_crew.crew().kickoff()
            chapter = Chapter(**result)
            
            assert isinstance(chapter, Chapter)
            assert chapter.title == improved_chapter["title"]
            assert chapter.content == improved_chapter["content"]

    async def test_error_handling(self, review_crew):
        """Testa o tratamento de erros durante a revisão"""
        mock_crew = MagicMock(spec=Crew)
        mock_crew.kickoff.side_effect = Exception("Erro de API")
        
        with patch.object(review_crew, 'crew', return_value=mock_crew):
            with pytest.raises(Exception) as exc_info:
                review_crew.crew().kickoff()
            assert "erro" in str(exc_info.value).lower()

    @pytest.mark.parametrize("book_type,expected_feedback", [
        ("technical", ["código", "exemplo", "prática"]),
        ("educational", ["conceito", "exercício", "aprenda"]),
        ("business", ["mercado", "estratégia", "negócio"])
    ])
    async def test_review_style_by_book_type(self, review_crew, book_type, expected_feedback):
        """Testa se a revisão se adapta ao tipo de livro"""
        content = f"""# Título Principal

## Introdução
Este capítulo foi revisado considerando {', '.join(expected_feedback)}.
O conteúdo foi adaptado para o tipo de livro específico.

## Conteúdo Principal
Aqui está o conteúdo principal com foco nos elementos importantes.

### Exemplos Específicos
- Exemplo de {expected_feedback[0]}
- Demonstração de {expected_feedback[1]}
- Aplicação de {expected_feedback[2]}

## Conclusão
Resumo dos pontos principais abordados."""
        
        mock_data = {
            "title": "Título Revisado",
            "content": content
        }
        
        mock_crew = MagicMock(spec=Crew)
        mock_crew.kickoff.return_value = mock_data
        
        with patch.object(review_crew, 'crew', return_value=mock_crew):
            result = review_crew.crew().kickoff()
            chapter = Chapter(**result)
            
            for keyword in expected_feedback:
                assert keyword in chapter.content.lower() 