import pytest
from src.core.config.settings import AppSettings, OutputLanguage
from pathlib import Path

def test_settings_default_values():
    """Testa os valores padrão das configurações"""
    settings = AppSettings()
    
    assert settings.DEFAULT_LANGUAGE == OutputLanguage.PORTUGUESE
    assert isinstance(settings.BASE_DIR, Path)
    assert isinstance(settings.OUTPUT_DIR, Path)
    assert isinstance(settings.LOGS_DIR, Path)
    assert isinstance(settings.BACKUP_DIR, Path)

def test_settings_model_name():
    """Testa o nome do modelo baseado no ambiente"""
    # Em ambiente de teste
    settings = AppSettings()
    assert settings.MODEL_NAME == "gpt-4o-mini"
    
    # Em ambiente de produção
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("TESTING", raising=False)
        settings = AppSettings()
        assert settings.MODEL_NAME == "gpt-4o-mini"

def test_settings_directories():
    """Testa se os diretórios são criados corretamente"""
    settings = AppSettings()
    
    # Verifica se os diretórios existem
    assert settings.OUTPUT_DIR.exists()
    assert settings.LOGS_DIR.exists()
    assert settings.BACKUP_DIR.exists()
    
    # Verifica se são diretórios
    assert settings.OUTPUT_DIR.is_dir()
    assert settings.LOGS_DIR.is_dir()
    assert settings.BACKUP_DIR.is_dir()

def test_settings_api_keys():
    """Testa a validação das chaves de API"""
    # Em ambiente de teste, as chaves são opcionais
    settings = AppSettings()
    assert settings.OPENAI_API_KEY is not None
    assert settings.SERPER_API_KEY is not None
  