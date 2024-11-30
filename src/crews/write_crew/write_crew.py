from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from src.models.book_models import Chapter, ChapterOutline
from src.core.config.settings import settings
from pathlib import Path
import logging
import os
from langchain.tools import SerperDevTool

logger = logging.getLogger(__name__)

@CrewBase
class WriteChapterCrew:
    """Book Chapter Writer Crew"""

    root_dir = Path(__file__).parent.parent.parent.parent
    agents_config = str(root_dir / "config" / "agents.yaml")
    tasks_config = str(root_dir / "config" / "write_crew" / "tasks.yaml")
    
    def __init__(self):
        """Inicializa o WriteChapterCrew."""
        logger.info(f"Inicializando WriteChapterCrew com modelo: {settings.MODEL_NAME}")
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

    def _validate_inputs(self, chapter_title: str, topic: str, chapter_description: str, chapter_topics: list) -> None:
        """Valida os inputs do capítulo."""
        if not chapter_title or not topic or not chapter_description or not chapter_topics:
            raise ValueError("Todos os campos são obrigatórios: chapter_title, topic, chapter_description, chapter_topics")
        
        if len(chapter_title.strip()) < 3 or len(topic.strip()) < 3 or len(chapter_description.strip()) < 10:
            raise ValueError("Input inválido: os campos devem ter um tamanho mínimo")
        
        if not isinstance(chapter_topics, list) or len(chapter_topics) < 1:
            raise ValueError("chapter_topics deve ser uma lista com pelo menos um item")

    @agent
    def researcher(self) -> Agent:
        search_tool = SerperDevTool(api_key=settings.SERPER_API_KEY)
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool],
            llm="gpt-4o",
            verbose=True,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            llm="gpt-4o",
            verbose=True,
        )

    @task
    def write_chapter(self) -> Task:
        task_description = self.tasks_config["write"]["description"].format(**self.inputs)
        return Task(
            description=task_description,
            agent=self.writer(),
            expected_output="A well-written book chapter with detailed content."
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Book Chapter Writer Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    async def write_chapter_content(
        self,
        chapter_title: str,
        topic: str,
        chapter_description: str,
        chapter_topics: list,
        book_type: str = "Guia Prático"
    ) -> Chapter:
        """Escreve um capítulo do livro usando o crew."""
        self._validate_inputs(chapter_title, topic, chapter_description, chapter_topics)
        
        self.inputs = {
            "chapter_title": chapter_title,
            "topic": topic,
            "chapter_description": chapter_description,
            "chapter_topics": ", ".join(chapter_topics),
            "book_type": book_type
        }
        
        result = self.crew().kickoff()
        
        if hasattr(result, 'raw'):
            content = result.raw
        else:
            content = str(result)
            
        return content
