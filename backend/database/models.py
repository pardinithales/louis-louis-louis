from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class ValidationCase(Base):
    __tablename__ = "validation_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True, nullable=False)
    clinical_history = Column(Text, nullable=False)
    # Aqui você poderia adicionar colunas para o diagnóstico correto, se desejar
    # correct_syndrome = Column(String) 

class UserSubmission(Base):
    __tablename__ = "user_submissions"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    # Poderíamos armazenar a resposta da IA também, para análise futura
    # inference_response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ValidationSubmission(Base):
    __tablename__ = "validation_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String(5), nullable=False, index=True)
    case_id = Column(String, nullable=False, index=True)
    user_group = Column(String, nullable=False) # 'louis_group' ou 'control_group'
    answer = Column(Text, nullable=False)
    user_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SUSResponse(Base):
    __tablename__ = "sus_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String(5), nullable=False, index=True)
    q1 = Column(Integer, nullable=False)
    q2 = Column(Integer, nullable=False)
    q3 = Column(Integer, nullable=False)
    q4 = Column(Integer, nullable=False)
    q5 = Column(Integer, nullable=False)
    q6 = Column(Integer, nullable=False)
    q7 = Column(Integer, nullable=False)
    q8 = Column(Integer, nullable=False)
    q9 = Column(Integer, nullable=False)
    q10 = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 