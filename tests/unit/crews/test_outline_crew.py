import pytest
from unittest.mock import patch, MagicMock
from src.crews.outline_crew.outline_crew import OutlineCrew
from src.models.book_models import BookOutline

class TestOutlineCrew:
    @pytest.fixture
    def outline_crew(self, mock_llm, mock_config, mock_tasks_config):
        with patch('src.crews.outline_crew.outline_crew.ChatOpenAI', return_value=mock_llm), \
             patch.object(OutlineCrew, 'agents_config', mock_config), \
             patch.object(OutlineCrew, 'tasks_config', mock_tasks_config):
            
            crew = OutlineCrew()
            return crew

    @pytest.mark.asyncio
    async def test_generate_outline_success(self, outline_crew, mock_llm, sample_book_data):
        """Testa a geração bem-sucedida de um outline."""
        # Arrange
        mock_llm.predict.return_value = sample_book_data
        
        with patch.object(outline_crew, 'crew') as mock_crew_method:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.return_value = sample_book_data
            mock_crew_method.return_value = mock_crew_instance
            
            # Act
            result = await outline_crew.generate_outline(
                topic="Python",
                goal="Ensinar programação básica",
                target_audience="Iniciantes em programação"
            )
            
            # Assert
            assert isinstance(result, BookOutline)
            assert result.title == sample_book_data["title"]
            assert result.description == sample_book_data["description"]
            assert len(result.chapters) > 0

    @pytest.mark.asyncio
    async def test_generate_outline_invalid_input(self, outline_crew):
        """Testa a validação de inputs inválidos."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await outline_crew.generate_outline(
                topic="",  # tópico vazio
                goal="Ensinar Python",
                target_audience="Iniciantes"
            )
        assert "campos são obrigatórios" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_research_task_creation(self, outline_crew):
        # Arrange
        outline_crew.inputs = {
            "topic": "Python Programming",
            "goal": "Ensinar programação básica",
            "target_audience": "Iniciantes",
            "book_type": "Guia Prático",
            "language": "pt-BR"
        }
        
        # Act
        task = outline_crew.research_outline()
        
        # Assert
        assert task is not None, "Research task should be created"
        assert "research" in task.description.lower(), "Task should be about research"
        assert outline_crew.inputs["topic"] in task.description, "Topic should be in description"

    @pytest.mark.asyncio
    async def test_write_task_creation(self, outline_crew):
        # Arrange
        outline_crew.inputs = {
            "topic": "Python Programming",
            "goal": "Ensinar programação básica",
            "target_audience": "Iniciantes",
            "book_type": "Guia Prático",
            "language": "pt-BR"
        }
        
        # Act
        task = outline_crew.write_outline()
        
        # Assert
        assert task is not None, "Write task should be created"
        assert "outline" in task.description.lower(), "Task should be about creating an outline"
        assert outline_crew.inputs["topic"] in task.description, "Topic should be in description"
 