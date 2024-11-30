from dataclasses import dataclass

@dataclass
class PDFConfig:
    OUTPUT_DIR: str = "output"
    MARGINS: int = 72
    FONT_SIZES = {
        "title": 24,
        "chapter": 20,
        "body": 12
    }
    PAGE_SIZE = "letter"

@dataclass
class BookConfig:
    DEFAULT_LANGUAGE = "pt-BR"
    MIN_CHAPTERS = 5
    MAX_CHAPTERS = 5 