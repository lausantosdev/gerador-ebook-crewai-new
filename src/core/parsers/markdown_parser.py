from src.models.book_models import BookOutline, ChapterOutline
import re

def parse_markdown_to_book_outline(markdown_text: str) -> dict:
    """
    Converte o texto markdown retornado pelo CrewAI em um dicionário compatível com BookOutline.
    
    Args:
        markdown_text (str): Texto markdown retornado pelo CrewAI
        
    Returns:
        dict: Dicionário compatível com BookOutline
    """
    # Normalizar quebras de linha
    markdown_text = markdown_text.replace('\r\n', '\n').strip()
    
    # Extrair título do livro (primeira linha com #)
    title_match = re.search(r'^#\s*(.*?)$', markdown_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Sem título"
    
    # Extrair capítulos (linhas começando com ###)
    chapters = []
    chapter_pattern = r'###\s*(.*?)\n(.*?)(?=\n###|\Z)'
    chapter_matches = re.finditer(chapter_pattern, markdown_text, re.DOTALL)
    
    for match in chapter_matches:
        chapter_title = match.group(1).strip()
        chapter_description = match.group(2).strip()
        if chapter_title and chapter_description:
            chapters.append({
                "title": chapter_title,
                "description": chapter_description,
                "topics": [],  # Lista vazia de tópicos por padrão
                "expected_length": "médio"  # Tamanho padrão
            })
    
    # Se não encontrou nenhum capítulo, adicionar um capítulo padrão
    if not chapters:
        chapters.append({
            "title": "Introdução",
            "description": "Capítulo introdutório do livro.",
            "topics": [],
            "expected_length": "médio"
        })
    
    return {
        "title": title,
        "chapters": chapters
    }

def parse_crew_output_to_chapter(crew_output) -> dict:
    """
    Converte o output do CrewAI em um dicionário compatível com Chapter.
    
    Args:
        crew_output: Output do CrewAI (pode ser string, dict ou CrewOutput)
        
    Returns:
        dict: Dicionário compatível com Chapter
    """
    # Se já é um dicionário, retornar como está
    if isinstance(crew_output, dict):
        return crew_output
    
    # Se é um CrewOutput, pegar o raw
    if hasattr(crew_output, 'raw'):
        content = crew_output.raw
    else:
        content = str(crew_output)
    
    # Extrair título (primeira linha em negrito ou primeiro título)
    title_match = re.search(r'(?:\*\*(.*?)\*\*|#\s*(.*?)(?:\n|$))', content)
    title = (title_match.group(1) or title_match.group(2)).strip() if title_match else "Sem título"
    
    return {
        "title": title,
        "content": content
    }