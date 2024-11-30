from crewai import Agent

class WriteAgents:
    """Classe responsável por criar os agentes de escrita."""

    @staticmethod
    def researcher() -> Agent:
        """Cria um agente pesquisador.

        Returns:
            Agent: Agente configurado para pesquisa
        """
        return Agent(
            role="Researcher",
            goal="Research and analyze the topic to gather information for the book outline",
            backstory="You are an expert researcher with vast experience in analyzing topics and identifying key concepts and best practices.",
            allow_delegation=False
        )

    @staticmethod
    def writer() -> Agent:
        """Cria um agente escritor.

        Returns:
            Agent: Agente configurado para escrita
        """
        return Agent(
            role="Writer",
            goal="Write engaging and informative content based on the research provided",
            backstory="You are a skilled technical writer with expertise in creating clear, concise, and engaging content.",
            allow_delegation=False
        ) 