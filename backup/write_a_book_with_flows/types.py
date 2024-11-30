from typing import List
from enum import Enum

from pydantic import BaseModel


class ChapterOutline(BaseModel):
    title: str
    description: str


class BookOutline(BaseModel):
    chapters: List[ChapterOutline]


class Chapter(BaseModel):
    title: str
    content: str


class OutputLanguage(Enum):
    PORTUGUESE = "pt-BR"
    ENGLISH = "en-US"
    SPANISH = "es-ES"
    # Adicione outros idiomas conforme necessário
