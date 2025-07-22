import sys
sys.path.append('..')

from database.database import SessionLocal, engine
from database import models
from sqlalchemy import inspect

def check_sus_table():
    """Verifica a estrutura e dados da tabela SUS"""
    db = SessionLocal()
    
    try:
        # Verificar se a tabela existe
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tabelas no banco: {tables}")
        
        if 'sus_responses' not in tables:
            print("\n❌ Tabela 'sus_responses' NÃO existe!")
            return
        
        print("\n✅ Tabela 'sus_responses' existe!")
        
        # Verificar colunas
        columns = inspector.get_columns('sus_responses')
        print("\nColunas da tabela:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Contar registros
        count = db.query(models.SUSResponse).count()
        print(f"\nTotal de respostas SUS: {count}")
        
        # Mostrar algumas respostas
        if count > 0:
            print("\nPrimeiras 5 respostas:")
            responses = db.query(models.SUSResponse).limit(5).all()
            for r in responses:
                print(f"  User: {r.user_identifier}, Q1: {r.q1}, Q10: {r.q10}, Created: {r.created_at}")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_sus_table() 