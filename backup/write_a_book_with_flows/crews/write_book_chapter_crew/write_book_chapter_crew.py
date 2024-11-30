from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
import os

from write_a_book_with_flows.types import Chapter


@CrewBase
class WriteBookChapterCrew:
    """Write Book Chapter Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    def __init__(self, **kwargs):
        super().__init__()
        self.inputs = kwargs

    @agent
    def researcher(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def research_chapter(self) -> Task:
        task_config = self.tasks_config["research_chapter"]
        # Formatar a descrição com as variáveis antes de criar a Task
        formatted_description = task_config["description"].format(
            chapter_title=self.inputs.get("chapter_title", ""),
            tema=self.inputs.get("tema", ""),
            chapter_description=self.inputs.get("chapter_description", "")
        )
        
        return Task(
            description=formatted_description,
            agent=self.researcher(),
            expected_output="Detailed research about the chapter including main concepts and best practices."
        )

    @task
    def write_chapter(self) -> Task:
        task_config = self.tasks_config["write_chapter"]
        # Formatar a descrição com as variáveis antes de criar a Task
        formatted_description = task_config["description"].format(
            tema=self.inputs.get("tema", ""),
            chapter_title=self.inputs.get("chapter_title", ""),
            chapter_description=self.inputs.get("chapter_description", "")
        )
        
        return Task(
            description=formatted_description,
            agent=self.writer(),
            expected_output="A well-structured chapter in Portuguese.",
            output_pydantic=Chapter
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Write Book Chapter Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
