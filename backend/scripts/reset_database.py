import os
import sys

# Adiciona o diretório raiz ao path para encontrar os módulos do backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.database import engine
from backend.database import models

DB_FILE = "database.db"

def reset_database():
    print("--- Iniciando Reset do Banco de Dados ---")
    
    # Apaga o arquivo de banco de dados antigo, se ele existir
    if os.path.exists(DB_FILE):
        print(f"Arquivo de banco de dados antigo '{DB_FILE}' encontrado. Removendo...")
        os.remove(DB_FILE)
        print("Arquivo removido com sucesso.")
    else:
        print(f"Nenhum arquivo de banco de dados antigo '{DB_FILE}' encontrado. Pulando a remoção.")

    # Cria todas as tabelas com base nos modelos definidos
    print("Criando novas tabelas com o esquema atualizado...")
    models.Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")
    print("--- Reset do Banco de Dados Concluído ---")

if __name__ == "__main__":
    reset_database() 