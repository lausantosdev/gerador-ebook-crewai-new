# Gerador de Ebooks com IA

Um gerador de ebooks automatizado usando Inteligência Artificial e CrewAI.

## 📚 Sobre o Projeto

Este projeto utiliza IA para gerar ebooks completos de forma automatizada. Ele usa o conceito de "crews" (equipes) do CrewAI, onde diferentes agentes de IA trabalham juntos para criar um livro completo:

- **Outline Crew**: Responsável por gerar a estrutura e o sumário do livro
- **Write Crew**: Responsável por escrever os capítulos
- **Review Crew**: Responsável por revisar e melhorar o conteúdo

## 🚀 Funcionalidades

- Geração automática de estrutura do livro
- Escrita de capítulos com GPT-4
- Revisão e melhoria automática do conteúdo
- Exportação para PDF e Markdown
- Suporte a múltiplos idiomas (pt-BR e en-US)
- Processamento paralelo de capítulos

## 🛠️ Tecnologias Utilizadas

- Python 3.10+
- CrewAI
- OpenAI GPT-4
- Langchain
- WeasyPrint (para geração de PDF)
- Pydantic (para configurações)

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)
- Chave de API da OpenAI
- Chave de API do Serper (para pesquisas)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/lausantosdev/gerador-ebook-crewai-new.git
cd gerador-ebook-crewai-new
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```env
OPENAI_API_KEY=sua_chave_api_openai
SERPER_API_KEY=sua_chave_api_serper
DEFAULT_LANGUAGE=pt-BR
MODEL_NAME=gpt-4o
```

## 🚀 Uso

1. Execute o script principal:
```bash
python run.py
```

2. O script irá:
   - Gerar a estrutura do livro
   - Escrever os capítulos
   - Revisar o conteúdo
   - Gerar o arquivo final em PDF

## 📁 Estrutura do Projeto

```
src/
├── agents/         # Agentes de IA
├── core/          # Configurações e funcionalidades principais
├── crews/         # Implementação das crews
├── models/        # Modelos de dados
├── services/      # Serviços do livro
└── interfaces/    # Interfaces e abstrações

tests/             # Testes automatizados
├── unit/         # Testes unitários
├── integration/  # Testes de integração
└── e2e/          # Testes end-to-end
```

## 🧪 Testes

Execute os testes com:
```bash
pytest
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🤝 Suporte

Se você encontrar algum problema ou tiver sugestões, por favor abra uma issue no GitHub.
