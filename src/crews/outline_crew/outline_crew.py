from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from src.models.book_models import BookOutline, OutputLanguage
from src.core.config.settings import settings
from src.core.parsers.markdown_parser import parse_markdown_to_book_outline
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@CrewBase
class OutlineCrew:
    """Book Outline Crew"""

    root_dir = Path(__file__).parent.parent.parent.parent
    agents_config = str(root_dir / "config" / "agents.yaml")
    tasks_config = str(root_dir / "config" / "outline_crew" / "tasks.yaml")
    
    def __init__(self):
        """Inicializa o OutlineCrew."""
        super().__init__()
        self.inputs = {}
        self.topic = None
        
        logger.debug(f"Inicializando OutlineCrew com modelo: {settings.MODEL_NAME}")
        
        # Forçar o uso do modelo gpt-4o
        model_name = "gpt-4o"
        logger.info(f"Forçando uso do modelo: {model_name}")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        
        logger.debug(f"LLM configurado com modelo: {self.llm.model}")
        logger.debug(f"Temperatura: {self.llm.temperature}")

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
    def research_outline(self) -> Task:
        task_description = self.tasks_config["research"]["description"].format(**self.inputs)
        return Task(
            description=task_description,
            agent=self.researcher(),
            expected_output="Detailed research about the topic including main concepts and best practices."
        )

    @task
    def write_outline(self) -> Task:
        task_description = self.tasks_config["write"]["description"].format(**self.inputs)
        return Task(
            description=task_description,
            agent=self.writer(),
            expected_output="A well-structured book outline with chapters and descriptions."
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Book Outline Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def _validate_inputs(self, topic: str, goal: str, target_audience: str) -> None:
        """Valida os inputs do outline."""
        if not topic or not goal or not target_audience:
            raise ValueError("Todos os campos são obrigatórios: topic, goal e target_audience")
        
        if len(topic.strip()) < 3 or len(goal.strip()) < 10 or len(target_audience.strip()) < 3:
            raise ValueError("Input inválido: os campos devem ter um tamanho mínimo")

    async def generate_outline(
        self, 
        topic: str, 
        goal: str, 
        target_audience: str,
        book_type: str = "Guia Prático",
        language: OutputLanguage = OutputLanguage.PORTUGUESE
    ) -> BookOutline:
        """Gera o outline do livro usando o crew."""
        self._validate_inputs(topic, goal, target_audience)
        
        self.inputs = {
            "topic": topic,
            "goal": goal,
            "target_audience": target_audience,
            "book_type": book_type,
            "language": language.value
        }
        self.topic = topic
        
        result = self.crew().kickoff()
        
        # Converter o markdown para dicionário
        if hasattr(result, 'raw'):
            outline_dict = parse_markdown_to_book_outline(result.raw)
            # Atualizar com os inputs originais
            outline_dict["target_audience"] = target_audience
            outline_dict["goal"] = goal
            return BookOutline(**outline_dict)
            
        if isinstance(result, dict):
            return BookOutline(**result)
            
        return result
