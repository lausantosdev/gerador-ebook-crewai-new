import os
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiofiles
import markdown
from weasyprint import HTML
from openai import AsyncOpenAI, OpenAIError
import time

from src.models.book_models import Chapter, ChapterOutline, ChapterLength, Book, BookState
from src.interfaces.book_services import IBookOutlineGenerator, IChapterWriter, IBookSaver
from src.core.config.settings import settings

# Configuração do logger
logger = logging.getLogger(__name__)

class OpenAIService(IBookOutlineGenerator, IChapterWriter):
    """Serviço para interação com a API da OpenAI."""

    def __init__(self, llm=None):
        """Inicializa o serviço OpenAI."""
        logger.debug(f"Inicializando OpenAIService com configurações:")
        logger.debug(f"MODEL_NAME definido em settings: {settings.MODEL_NAME}")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm = llm
        if self.llm:
            self.model = self.llm.model_name
        else:
            self.model = settings.MODEL_NAME
            
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
        self.language = settings.DEFAULT_LANGUAGE
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CHAPTERS)
        
        logger.debug(f"Modelo configurado no serviço: {self.model}")
        logger.info(f"OpenAIService inicializado com modelo: {self.model}")
        
        # Validar modelo
        if not self.model:
            raise ValueError("Modelo não configurado corretamente")
        
        logger.debug(f"Configuração final do OpenAI Service:")
        logger.debug(f"- Model: {self.model}")
        logger.debug(f"- Temperature: {self.temperature}")
        logger.debug(f"- Max Tokens: {self.max_tokens}")
        logger.debug(f"- Language: {self.language}")

    async def test_connection(self) -> bool:
        """Testa a conexão com a API da OpenAI."""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            raise OpenAIError(f"Erro na API da OpenAI: {str(e)}")

    async def generate_outline(self, topic: str, goal: str, target_audience: str) -> List[ChapterOutline]:
        """Gera o outline do livro."""
        logger.info(f"Gerando outline usando modelo: {self.model}")
        logger.debug(f"Configurações da API: model={self.model}, temperature={self.temperature}, max_tokens={self.max_tokens}")
        
        prompt = f"""Crie um outline detalhado para um livro sobre {topic}.
Objetivo: {goal}
Público-alvo: {target_audience}

O outline deve ter a seguinte estrutura:
1. Sumário (lista com todos os capítulos)
2. Introdução (visão geral do tema)
3. 5-8 capítulos de conteúdo
4. Conclusão (síntese e fechamento)

Cada capítulo deve ter:
1. Título claro e objetivo
2. Descrição concisa em UMA única linha
3. Lista de 2-3 tópicos principais
4. Estimativa de tamanho (médio/longo)

IMPORTANTE: As descrições devem ser extremamente concisas, com no máximo uma linha cada.

Responda em formato JSON seguindo este exemplo:
{{
    "chapters": [
        {{
            "title": "Sumário",
            "description": "Lista organizada dos capítulos com breves descrições.",
            "topics": ["Lista de capítulos"],
            "expected_length": "curto"
        }},
        {{
            "title": "Introdução",
            "description": "Uma visão geral sobre o tema e seu impacto na vida das pessoas.",
            "topics": ["Contextualização", "Importância"],
            "expected_length": "médio"
        }},
        {{
            "title": "Entendendo o Tema",
            "description": "Conceitos fundamentais e suas aplicações práticas.",
            "topics": ["Conceitos", "Aplicações"],
            "expected_length": "médio"
        }},
        {{
            "title": "Conclusão",
            "description": "Síntese das principais estratégias e próximos passos.",
            "topics": ["Resumo", "Ação"],
            "expected_length": "médio"
        }}
    ]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            logger.info(f"Outline gerado com sucesso usando modelo: {self.model}")
            
            result = response.choices[0].message.content
            data = eval(result)
            
            outlines = []
            for chapter in data["chapters"]:
                outline = ChapterOutline(
                    title=chapter["title"],
                    description=chapter["description"],
                    topics=chapter["topics"],
                    expected_length=ChapterLength(chapter["expected_length"])
                )
                outlines.append(outline)
            
            return outlines
            
        except Exception as e:
            logger.error(f"Erro ao gerar outline: {str(e)}")
            raise

    async def write_chapters_parallel(
        self,
        outlines: List[ChapterOutline],
        context: Dict[str, Any]
    ) -> List[Chapter]:
        """Escreve múltiplos capítulos em paralelo."""
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self._write_chapter_with_semaphore(outline, context))
                for outline in outlines
            ]
        
        # Ordena os capítulos na ordem original do outline
        chapters = [task.result() for task in tasks]
        chapter_dict = {chapter.title: chapter for chapter in chapters}
        ordered_chapters = [chapter_dict[outline.title] for outline in outlines]
        
        return ordered_chapters

    async def _write_chapter_with_semaphore(
        self,
        outline: ChapterOutline,
        context: Dict[str, Any]
    ) -> Chapter:
        """Escreve um capítulo usando um semáforo para controle de concorrência."""
        async with self.semaphore:
            logger.info(f"Iniciando geração do capítulo: {outline.title}")
            start_time = time.time()
            chapter = await self.generate_chapter(outline, context)
            generation_time = time.time() - start_time
            chapter.generation_time = generation_time
            logger.info(f"Capítulo concluído: {outline.title} em {generation_time:.1f}s")
            return chapter

    async def write_chapter(self, outline: ChapterOutline, context: Dict[str, Any]) -> Chapter:
        """Escreve um único capítulo do livro."""
        return await self.generate_chapter(outline, context)

    async def generate_chapter(
        self,
        outline: ChapterOutline,
        context: Dict[str, Any]
    ) -> Chapter:
        """Gera o conteúdo de um capítulo."""
        logger.info(f"Gerando capítulo '{outline.title}' usando modelo: {self.model}")
        max_tokens = {
            ChapterLength.CURTO: 2000,
            ChapterLength.MEDIO: 3000,
            ChapterLength.LONGO: 4000,
            ChapterLength.MUITO_LONGO: 4000
        }.get(outline.expected_length, 3000)

        # Define instruções específicas para cada tipo de capítulo
        instrucoes_especificas = {
            "Sumário": """
    Gere um sumário limpo e organizado seguindo estas regras:

    1. Use exatamente este formato:
       # [Título do Livro]
       
       ## Sumário
       
       ### [Nome do Capítulo]
       [Uma única linha explicando o objetivo do capítulo]

    2. Mantenha as descrições extremamente concisas (máximo uma linha)
    3. Use formatação markdown consistente
    4. Não inclua subtópicos ou detalhamentos
    5. Evite repetições e redundâncias
    6. Mantenha um estilo profissional e direto
    """
        }

        instrucoes_padrao = """
    ESTRUTURA E PROFUNDIDADE:
    - Desenvolva cada tópico com profundidade e riqueza de detalhes
    - Inclua subtópicos que exploram diferentes aspectos do tema
    - Use uma estrutura clara e bem organizada
    - Mantenha uma progressão lógica do conteúdo

    EXEMPLOS E CASOS:
    - Apresente múltiplos exemplos práticos e detalhados
    - Inclua casos de estudo reais e relevantes
    - Demonstre aplicações práticas em diferentes contextos
    - Forneça exemplos tanto positivos quanto negativos para análise

    FUNDAMENTAÇÃO:
    - Cite pesquisas e estudos relevantes
    - Inclua dados estatísticos quando apropriado
    - Referencie especialistas e autoridades no assunto
    - Apresente diferentes perspectivas sobre o tema

    ASPECTOS PRÁTICOS:
    - Forneça exercícios práticos e atividades
    - Inclua checklists e frameworks aplicáveis
    - Adicione dicas específicas e recomendações
    - Destaque armadilhas comuns e como evitá-las

    ENGAJAMENTO:
    - Use analogias e metáforas para explicar conceitos complexos
    - Inclua perguntas reflexivas para o leitor
    - Crie seções de "Pontos-Chave" ao final de cada parte
    - Mantenha um tom que mistura profissionalismo com engajamento

    RECURSOS ADICIONAIS:
    - Sugira ferramentas e recursos complementares
    - Inclua leituras recomendadas para aprofundamento
    - Forneça links para materiais adicionais
    - Crie seções de "Para Saber Mais" quando relevante
    """

        prompt = f"""Escreva um capítulo extremamente detalhado e aprofundado para um livro em {self.language}.

IMPORTANTE: O capítulo DEVE começar com o título no formato Markdown exatamente como mostrado abaixo:
# {outline.title}

Descrição: {outline.description}
Tópicos Principais: {', '.join(outline.topics)}

Contexto do Livro:
- Objetivo: {context['goal']}

DIRETRIZES DE QUALIDADE:
1. Mantenha o mais alto padrão de qualidade e profundidade
2. Use exemplos práticos e relevantes
3. Inclua código quando apropriado
4. Mantenha um tom profissional mas acessível
5. Use formatação markdown para estruturar o conteúdo

INSTRUÇÕES ESPECÍFICAS:
{instrucoes_especificas.get(outline.title, instrucoes_padrao)}

IMPORTANTE:
- Use formatação markdown para títulos e subtítulos
- Inclua exemplos práticos e código quando relevante
- Mantenha um tom profissional mas acessível
- Estruture o conteúdo de forma clara e organizada
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            return Chapter(
                title=outline.title,
                content=content,
                topics=outline.topics,
                expected_length=outline.expected_length
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar capítulo: {str(e)}")
            raise

class BookSaver(IBookSaver):
    """Serviço para salvar o livro em markdown."""

    def __init__(self, output_dir: Path):
        """Inicializa o serviço de salvamento.
        
        Args:
            output_dir: Diretório onde os arquivos serão salvos
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def save_pdf(self, book_state: BookState, filename: str) -> None:
        """Salva o livro em markdown."""
        try:
            # Salva em markdown
            markdown_path = self.output_dir / f"{filename}.md"
            content = f"# {book_state.title}\n\n"
            
            # Adiciona os capítulos
            for chapter in book_state.book:
                content += f"\n{chapter.content}\n"
            
            # Salva o arquivo markdown
            async with aiofiles.open(markdown_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            book_state.output_path = str(markdown_path)
            logger.info(f"Arquivo markdown salvo em: {markdown_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            raise

    async def save_backup(self, book_state: BookState, filename: str) -> None:
        """Salva um backup do livro em formato markdown."""
        try:
            backup_dir = self.output_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Salva cada capítulo separadamente
            for i, chapter in enumerate(book_state.book, 1):
                chapter_file = backup_dir / f"{filename}_chapter_{i}.md"
                async with aiofiles.open(chapter_file, 'w', encoding='utf-8') as f:
                    await f.write(chapter.content)
            
            # Salva metadados
            meta_file = backup_dir / f"{filename}_metadata.txt"
            async with aiofiles.open(meta_file, 'w', encoding='utf-8') as f:
                await f.write(f"Title: {book_state.title}\n")
                await f.write(f"Language: {book_state.language}\n")
                
        except Exception as e:
            logger.error(f"Erro ao salvar backup: {str(e)}")
            raise