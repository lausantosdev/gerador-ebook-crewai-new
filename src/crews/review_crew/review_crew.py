from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from src.models.book_models import Chapter
from src.core.config.settings import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@CrewBase
class ReviewCrew:
    """Book Review Crew"""

    root_dir = Path(__file__).parent.parent.parent.parent
    agents_config = str(root_dir / "config" / "agents.yaml")
    tasks_config = str(root_dir / "config" / "review_crew" / "tasks.yaml")
    
    def __init__(self):
        """Inicializa o ReviewCrew."""
        logger.info(f"Inicializando ReviewCrew com modelo: {settings.MODEL_NAME}")
        logger.debug(f"Configurações carregadas: MODEL_NAME={settings.MODEL_NAME}, TEMPERATURE={settings.OPENAI_TEMPERATURE}")
        
        # Forçar o uso do modelo gpt-4o
        model_name = "gpt-4o"
        logger.info(f"Forçando uso do modelo: {model_name}")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        logger.info(f"LangChain ChatOpenAI inicializado com modelo: {self.llm.model}")
        logger.debug(f"Configuração final do LLM: {self.llm}")
        
        # Validar modelo
        if not self.llm.model == model_name:
            logger.error(f"Modelo configurado incorretamente: esperado={model_name}, atual={self.llm.model}")
            raise ValueError(f"Modelo configurado incorretamente: {self.llm.model}")

    def _validate_inputs(self, chapter_title: str, chapter_content: str) -> None:
        """Valida os inputs do capítulo."""
        if not chapter_title or not chapter_content:
            raise ValueError("Todos os campos são obrigatórios: chapter_title, chapter_content")
        
        if len(chapter_title.strip()) < 3 or len(chapter_content.strip()) < 100:
            raise ValueError("Input inválido: os campos devem ter um tamanho mínimo")

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["reviewer"],
            llm="gpt-4o",
            verbose=True,
        )

    @task
    def review_chapter(self) -> Task:
        task_description = self.tasks_config["review"]["description"].format(**self.inputs)
        return Task(
            description=task_description,
            agent=self.reviewer(),
            expected_output="A reviewed and improved book chapter."
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Book Review Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    async def review_chapter_content(
        self,
        chapter_title: str,
        chapter_content: str
    ) -> str:
        """Revisa um capítulo do livro usando o crew."""
        self._validate_inputs(chapter_title, chapter_content)
        
        self.inputs = {
            "chapter_title": chapter_title,
            "chapter_content": chapter_content
        }
        
        result = self.crew().kickoff()
        
        if hasattr(result, 'raw'):
            content = result.raw
        else:
            content = str(result)
            
        return content 