from pathlib import Path
from src.models.book_models import BookState
import markdown
import weasyprint
import ebooklib
from ebooklib import epub

class BookExporter:
    """Classe responsável por exportar o livro em diferentes formatos"""

    def __init__(self, book_state: BookState):
        """Inicializa o exportador com o estado do livro"""
        if not book_state:
            raise ValueError("Estado do livro não pode ser nulo")
        if not book_state.title or not book_state.book:
            raise ValueError("Livro deve ter título e pelo menos um capítulo")
        self.book_state = book_state

    def export_markdown(self, output_file: Path, template: str = None) -> None:
        """Exporta o livro para markdown"""
        if not output_file:
            raise ValueError("Caminho de saída não pode ser vazio")

        # Usar template padrão se nenhum for fornecido
        if not template:
            template = """# {title}

{content}
"""

        # Gerar conteúdo
        content = []
        for chapter in self.book_state.book:
            content.append(chapter.content)

        # Aplicar template
        markdown_content = template.format(
            title=self.book_state.title,
            content="\n\n".join(content)
        )

        # Salvar arquivo
        output_file.write_text(markdown_content, encoding='utf-8')

    def export_pdf(self, output_file: Path) -> None:
        """Exporta o livro para PDF"""
        if not output_file:
            raise ValueError("Caminho de saída não pode ser vazio")

        # Converter markdown para HTML
        html_content = f"""
        <html>
        <head>
            <title>{self.book_state.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; }}
            </style>
        </head>
        <body>
            <h1>{self.book_state.title}</h1>
            {"".join(markdown.markdown(chapter.content) for chapter in self.book_state.book)}
        </body>
        </html>
        """

        # Gerar PDF
        weasyprint.HTML(string=html_content).write_pdf(str(output_file))

    def export_epub(self, output_file: Path) -> None:
        """Exporta o livro para EPUB"""
        if not output_file:
            raise ValueError("Caminho de saída não pode ser vazio")
        if not str(output_file).endswith('.epub'):
            raise ValueError("Arquivo de saída deve ter extensão .epub")

        # Criar livro EPUB
        book = epub.EpubBook()
        book.set_title(self.book_state.title)
        book.set_language(self.book_state.output_language)

        # Adicionar capítulos
        chapters = []
        for i, chapter in enumerate(self.book_state.book, 1):
            epub_chapter = epub.EpubHtml(
                title=chapter.title,
                file_name=f'chapter_{i}.xhtml',
                content=markdown.markdown(chapter.content)
            )
            book.add_item(epub_chapter)
            chapters.append(epub_chapter)

        # Adicionar navegação
        book.toc = [(epub.Section('Chapters'), chapters)]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Gerar spine
        book.spine = ['nav'] + chapters

        # Salvar arquivo
        epub.write_epub(str(output_file), book) 