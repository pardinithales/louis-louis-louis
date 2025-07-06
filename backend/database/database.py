import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define o caminho para o arquivo do banco de dados
DATABASE_URL = "sqlite:///./database.db"

# Cria o motor do SQLAlchemy
# O argumento connect_args={"check_same_thread": False} é necessário apenas para o SQLite
# para permitir que mais de um thread interaja com o banco de dados.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma classe de sessão. Esta será a classe que usaremos para criar sessões de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Retorna uma classe que pode ser herdada para criar modelos de banco de dados (ORM models)
Base = declarative_base() 