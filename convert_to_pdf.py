import argparse
import logging
from pathlib import Path
from weasyprint import HTML
import markdown
import sys
from typing import List, Optional
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_markdown_files(directory: str = "output") -> List[Path]:
    """Lista todos os arquivos markdown no diretório especificado."""
    output_dir = Path(directory)
    if not output_dir.exists():
        logger.error(f"Diretório {directory} não encontrado!")
        return []
    
    return list(output_dir.glob("*.md"))

def select_file(files: List[Path]) -> Optional[Path]:
    """Permite ao usuário selecionar um arquivo da lista."""
    if not files:
        logger.error("Nenhum arquivo markdown encontrado no diretório output!")
        return None
    
    # Ordena os arquivos por data de modificação (mais recente primeiro)
    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    print("\nArquivos markdown disponíveis (ordenados por data de modificação):")
    print("\n{:<4} {:<40} {:<20} {:<10}".format("Nº", "Nome do Arquivo", "Data Modificação", "Tamanho"))
    print("-" * 74)
    
    for i, file in enumerate(files, 1):
        # Obtém as informações do arquivo
        stats = file.stat()
        size_kb = stats.st_size / 1024
        mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M')
        
        print("{:<4} {:<40} {:<20} {:.1f}KB".format(
            i,
            file.name[:37] + "..." if len(file.name) > 40 else file.name,
            mod_time,
            size_kb
        ))
    
    while True:
        try:
            choice = input("\nEscolha o número do arquivo para converter (ou 'q' para sair): ")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(files):
                return files[index]
            else:
                print("Número inválido! Tente novamente.")
        except ValueError:
            print("Entrada inválida! Digite um número ou 'q' para sair.")

def convert_md_to_pdf(input_file: str, output_file: str = None):
    """
    Converte um arquivo Markdown para PDF.
    
    Args:
        input_file (str): Caminho do arquivo markdown de entrada
        output_file (str, optional): Caminho do arquivo PDF de saída.
            Se não fornecido, será criado no mesmo diretório com o mesmo nome.
    """
    try:
        input_path = Path(input_file)
        
        # Verifica se o arquivo de entrada existe
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")
            
        # Define o arquivo de saída se não fornecido
        if output_file is None:
            output_file = input_path.with_suffix('.pdf')
        
        logger.info(f"Convertendo {input_path} para PDF...")
        
        # Lê o conteúdo do arquivo markdown
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converte markdown para HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'nl2br', 'sane_lists', 'smarty']
        )
        
        # Adiciona estilo CSS básico
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 2cm;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                h1 {{
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 10px;
                }}
                code {{
                    background-color: #f7f7f7;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
                pre {{
                    background-color: #f7f7f7;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                blockquote {{
                    border-left: 4px solid #2c3e50;
                    margin: 0;
                    padding-left: 15px;
                    color: #666;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f7f7f7;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Converte HTML para PDF
        HTML(string=styled_html).write_pdf(output_file)
        
        logger.info(f"PDF gerado com sucesso: {output_file}")
        
    except Exception as e:
        logger.error(f"Erro ao converter arquivo: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Converte arquivo Markdown para PDF')
    parser.add_argument('-i', '--input', help='Arquivo markdown de entrada (opcional)')
    parser.add_argument('-o', '--output', help='Arquivo PDF de saída (opcional)')
    parser.add_argument('-d', '--directory', default='output',
                      help='Diretório onde procurar arquivos markdown (padrão: output)')
    
    args = parser.parse_args()
    
    if args.input:
        # Se um arquivo foi especificado, converte diretamente
        convert_md_to_pdf(args.input, args.output)
    else:
        # Lista arquivos disponíveis e permite seleção
        files = list_markdown_files(args.directory)
        selected_file = select_file(files)
        
        if selected_file:
            output_file = args.output if args.output else None
            convert_md_to_pdf(str(selected_file), output_file)
        else:
            logger.info("Operação cancelada pelo usuário.")

if __name__ == "__main__":
    main() 