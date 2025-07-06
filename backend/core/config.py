import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a chave da API do Gemini a partir das variáveis de ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validação simples para garantir que a chave foi configurada
if not GEMINI_API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi configurada. Crie um arquivo .env e adicione a chave.")

# Define o caminho para o diretório dos capítulos
# __file__ se refere a este arquivo (config.py)
# os.path.dirname() pega o diretório (core)
# ... sobe dois níveis (de core para backend, de backend para a raiz)
# os.path.join() junta com 'chapters'
CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'chapters')

# Define o caminho para o diretório de imagens
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'images') 