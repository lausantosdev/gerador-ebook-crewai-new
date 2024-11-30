import logging
from pathlib import Path
from typing import Optional
import re
import time
from datetime import datetime, timedelta
from src.core.config.settings import settings
from src.interfaces.book_services import IBookOutlineGenerator, IChapterWriter, IBookSaver
from src.models.book_models import BookState, Chapter, ChapterLength
from src.services.book_services import OpenAIService

class BookFlow:
    """Orquestrador do fluxo de geração do livro."""

    def __init__(
        self,
        outline_generator: IBookOutlineGenerator,
        chapter_writer: IChapterWriter,
        book_saver: IBookSaver
    ):
        self.outline_generator = outline_generator
        self.chapter_writer = chapter_writer
        self.book_saver = book_saver
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._state: Optional[BookState] = None

    def _print_separator(self):
        """Imprime uma linha separadora para melhor visualização dos logs."""
        self.logger.info("="*50)

    def _print_status(self, message: str, is_step: bool = False):
        """Imprime uma mensagem de status formatada."""
        if is_step:
            self._print_separator()
            self.logger.info(f"🔄 ETAPA: {message}")
            self._print_separator()
        else:
            self.logger.info(f"📝 {message}")

    def _print_success(self, message: str):
        """Imprime uma mensagem de sucesso."""
        self.logger.info(f"✅ {message}")

    def _print_warning(self, message: str):
        """Imprime um aviso."""
        self.logger.warning(f"⚠️ {message}")

    def _print_error(self, message: str):
        """Imprime uma mensagem de erro."""
        self.logger.error(f"❌ {message}")

    def _estimate_chapter_time(self, length: ChapterLength) -> float:
        """Estima o tempo de geração de um capítulo baseado no tamanho."""
        # Tempos médios em segundos
        time_estimates = {
            ChapterLength.CURTO: 120,  # 2 minutos
            ChapterLength.MEDIO: 180,  # 3 minutos
            ChapterLength.LONGO: 240,  # 4 minutos
            ChapterLength.MUITO_LONGO: 300  # 5 minutos
        }
        return time_estimates.get(length, 180)

    def _format_time(self, seconds: float) -> str:
        """Formata o tempo em segundos para uma string legível."""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def _estimate_total_time(self) -> float:
        """Estima o tempo total de geração baseado no outline."""
        if not self._state.book_outline:
            return 0
        
        outline_time = 60  # 1 minuto para outline
        chapter_times = sum(
            self._estimate_chapter_time(outline.expected_length)
            for outline in self._state.book_outline
        )
        
        # Ajusta para processamento paralelo
        parallel_factor = min(len(self._state.book_outline), settings.MAX_CONCURRENT_CHAPTERS)
        adjusted_chapter_time = chapter_times / parallel_factor if parallel_factor > 0 else chapter_times
        
        return outline_time + adjusted_chapter_time

    async def execute(
        self, 
        topic: str, 
        target_audience: str, 
        book_type: str
    ) -> BookState:
        """Executa o fluxo completo de geração do livro."""
        start_time = time.time()
        self._print_status("INICIANDO GERAÇÃO DO EBOOK", True)
        self._print_status(f"Tema: {topic}")
        self._print_status(f"Público-alvo: {target_audience}")
        self._print_status(f"Tipo: {book_type}")
        
        try:
            # Inicializa o estado
            self._state = BookState(
                title=topic,
                topic=topic,
                goal=f"Criar um {book_type} sobre {topic} para {target_audience}",
                target_audience=target_audience
            )

            # Gera o outline
            self._print_status("GERANDO ESTRUTURA DO EBOOK", True)
            self._print_status("Analisando tema e definindo capítulos...")
            
            outline_start = time.time()
            outline = await self.outline_generator.generate_outline(
                topic=self._state.topic,
                goal=self._state.goal,
                target_audience=target_audience
            )
            self._state.book_outline = outline
            outline_time = time.time() - outline_start
            self._state.time_metrics.outline_generation_time = outline_time
            
            # Mostra estrutura gerada
            self._print_success(f"Estrutura gerada com {len(outline)} capítulos em {self._format_time(outline_time)}")
            for idx, chapter in enumerate(outline, 1):
                self._print_status(f"Capítulo {idx}: {chapter.title}")
                self._print_status(f"   Descrição: {chapter.description}")
                self._print_status(f"   Tamanho esperado: {chapter.expected_length}")
            
            # Calcula e mostra estimativa
            total_estimated_time = self._estimate_total_time()
            estimated_completion = datetime.now() + timedelta(seconds=total_estimated_time)
            self._state.time_metrics.estimated_completion_time = estimated_completion
            
            self._print_separator()
            self._print_status("PREVISÃO DE TEMPO", True)
            self._print_status(f"Tempo estimado total: {self._format_time(total_estimated_time)}")
            self._print_status(f"Previsão de conclusão: {estimated_completion.strftime('%H:%M:%S')}")
            self._print_status(f"Gerando {settings.MAX_CONCURRENT_CHAPTERS} capítulos simultaneamente")

            # Escreve os capítulos em paralelo
            self._print_status("GERANDO CONTEÚDO DOS CAPÍTULOS", True)
            chapters = await self._write_chapters_parallel()
            self._state.book = chapters

            # Finaliza métricas de tempo
            total_time = time.time() - start_time
            self._state.time_metrics.total_generation_time = total_time
            
            self._print_status("RESUMO DA GERAÇÃO", True)
            self._print_success(f"Tempo total de geração: {self._format_time(total_time)}")
            self._print_status("Tempo por capítulo:")
            for title, time_taken in self._state.time_metrics.chapter_generation_times.items():
                self._print_status(f"- {title}: {self._format_time(time_taken)}")

            # Salva o livro
            self._print_status("SALVANDO EBOOK", True)
            self._print_status("Convertendo para PDF...")
            await self._save_book()
            self._print_success("Ebook gerado e salvo com sucesso!")
            
            # Resumo final
            self._print_status("RESUMO FINAL", True)
            self._print_status(f"Título: {self._state.title}")
            self._print_status(f"Total de capítulos: {len(self._state.book)}")
            self._print_status(f"Tempo total: {self._format_time(total_time)}")
            if self._state.output_path:
                self._print_status(f"Arquivo salvo em: {self._state.output_path}")

            return self._state

        except Exception as e:
            self._print_error(f"Erro fatal no fluxo do livro: {str(e)}")
            raise RuntimeError(f"Falha na geração do livro: {str(e)}")

    async def _write_chapters_parallel(self) -> list[Chapter]:
        """Escreve todos os capítulos do livro em paralelo."""
        book_context = {
            "goal": self._state.goal,
            "topic": self._state.topic,
            "target_audience": self._state.target_audience,
            "outline": [co.model_dump() for co in self._state.book_outline]
        }

        total_chapters = len(self._state.book_outline)
        self._print_status(f"Iniciando geração de {total_chapters} capítulos")
        self._print_status(f"Processando {settings.MAX_CONCURRENT_CHAPTERS} capítulos simultaneamente")
        
        try:
            if isinstance(self.chapter_writer, OpenAIService):
                start_time = time.time()
                chapters = await self.chapter_writer.write_chapters_parallel(
                    self._state.book_outline,
                    book_context
                )
                for chapter in chapters:
                    if hasattr(chapter, 'generation_time'):
                        self._state.time_metrics.chapter_generation_times[chapter.title] = chapter.generation_time
                        self._print_success(f"Capítulo concluído: {chapter.title} ({self._format_time(chapter.generation_time)})")
            else:
                chapters = []
                for idx, outline in enumerate(self._state.book_outline, 1):
                    self._print_status(f"Gerando capítulo {idx}/{total_chapters}: {outline.title}")
                    start_time = time.time()
                    chapter = await self.chapter_writer.write_chapter(outline, book_context)
                    generation_time = time.time() - start_time
                    chapter.generation_time = generation_time
                    self._state.time_metrics.chapter_generation_times[chapter.title] = generation_time
                    self._print_success(f"Capítulo {idx} concluído em {self._format_time(generation_time)}")
                    chapters.append(chapter)
            
            return chapters
            
        except Exception as e:
            self._print_error(f"Erro na geração dos capítulos: {str(e)}")
            raise

    async def _save_book(self) -> None:
        """Salva o livro em PDF e faz backup do estado."""
        filename = self._sanitize_filename(self._state.topic)
        try:
            await self.book_saver.save_pdf(self._state, filename)
            await self.book_saver.save_backup(self._state, filename)
        except Exception as e:
            self.logger.error(f"Erro ao salvar livro: {str(e)}")
            raise

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitiza o nome do arquivo removendo caracteres especiais."""
        sanitized = re.sub(r'[^\w\s-]', '', filename)
        sanitized = re.sub(r'\s+', '_', sanitized)
        return sanitized.lower() 