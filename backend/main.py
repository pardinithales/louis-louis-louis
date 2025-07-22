import logging
import pandas as pd
from io import StringIO
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import random

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from fpdf import FPDF

from .models.api_models import (
    InferenceRequest,
    InferenceResponse,
    ValidationCaseResponse,
    ValidationSubmissionRequest,
    ValidationSubmissionResponse,
    AdminActionRequest,
    SUSSubmissionRequest,
    SUSSubmissionResponse,
    SUSResponseModel
)
from .services.inference_service import run_full_inference_process
from .database import crud, models
from .database.database import SessionLocal, engine

# Cria todas as tabelas no banco de dados (se não existirem)
# Isso é seguro para executar toda vez que a aplicação inicia.
models.Base.metadata.create_all(bind=engine)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="API de Inferência de Síndromes Neurológicas",
    description="Use esta API para obter uma inferência de 4 síndromes neurológicas com base em sinais clínicos.",
    version="1.0.0"
)

# Configuração do CORS
# Em produção, restrinja para o domínio específico.
# Para desenvolvimento, permita origens locais.
origins = ["*"]


# Configuração do CORS para permitir requisições de qualquer origem.
# Em um ambiente de produção, é recomendado restringir para domínios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite apenas o seu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Monta o diretório 'images' para ser servido estaticamente
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.post("/infer/", response_model=InferenceResponse)
async def infer_syndrome(request: InferenceRequest, db: Session = Depends(get_db)):
    """
    Recebe um quadro clínico e retorna as síndromes mais prováveis.
    """
    logging.info(f"Received inference request with query: '{request.query}'")
    
    try:
        # Chama o serviço que orquestra todo o processo de inferência
        result = await run_full_inference_process(request.query)
        # O Pydantic validará automaticamente se o 'result' corresponde ao 'InferenceResponse'
        return result
    except FileNotFoundError as e:
        # Erro caso o diretório de capítulos ou um arquivo não seja encontrado
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        # Erro caso o modelo da Gemini retorne um valor inesperado (ex: nome de arquivo inválido)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Captura de erro genérica para outras falhas inesperadas
        # Idealmente, teríamos um log mais detalhado aqui
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")

@app.get("/validation_cases/", response_model=List[ValidationCaseResponse])
def get_validation_cases(user_identifier: str = Query(..., description="Últimos 5 dígitos do CPF do usuário."), db: Session = Depends(get_db)):
    """
    Retorna 20 casos clínicos de validação aleatórios para o usuário específico.
    """
    cases = crud.get_all_validation_cases(db)
    if len(cases) < 20:
        raise HTTPException(status_code=400, detail="Não há casos suficientes para sortear 20.")
    
    # Usa o user_identifier como semente para reproducibilidade
    random.seed(user_identifier)
    
    # Sorteia 20 casos únicos
    selected_cases = random.sample(cases, 20)
    
    return selected_cases

@app.post("/submit_validation_answer/")
def submit_validation_answer(submission: ValidationSubmissionRequest, db: Session = Depends(get_db)):
    """
    Recebe e armazena a resposta de um usuário para um caso de validação.
    """
    logging.info(f"Recebida submissão do usuário {submission.user_identifier} para o caso {submission.case_id}")
    try:
        crud.create_validation_submission(
            db=db,
            user_identifier=submission.user_identifier,
            case_id=submission.case_id,
            answer=submission.answer,
            user_group=submission.user_group,
            user_type=submission.user_type
        )
        return {"status": "success", "message": "Resposta armazenada com sucesso."}
    except Exception as e:
        logging.error(f"Falha ao armazenar a submissão de validação: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível armazenar a resposta.")

@app.post("/submit_sus/", response_model=SUSSubmissionResponse)
def submit_sus(request: SUSSubmissionRequest, db: Session = Depends(get_db)):
    try:
        crud.create_sus_response(
            db=db,
            user_identifier=request.user_identifier,
            q1=request.q1,
            q2=request.q2,
            q3=request.q3,
            q4=request.q4,
            q5=request.q5,
            q6=request.q6,
            q7=request.q7,
            q8=request.q8,
            q9=request.q9,
            q10=request.q10
        )
        return {"status": "success", "message": "Respostas do questionário SUS armazenadas com sucesso."}
    except Exception as e:
        logging.error(f"Falha ao armazenar as respostas SUS: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível armazenar as respostas do SUS.")

@app.get("/validation_submissions/", response_model=List[ValidationSubmissionResponse])
def get_validation_submissions(db: Session = Depends(get_db)):
    """
    Retorna todas as respostas de validação submetidas.
    """
    submissions = crud.get_all_validation_submissions(db)
    return submissions

@app.post("/delete_validation_submissions/")
def delete_validation_submissions(request: AdminActionRequest, db: Session = Depends(get_db)):
    """
    Apaga todas as respostas de validação submetidas se a senha estiver correta.
    """
    if request.password != "admin":
        raise HTTPException(status_code=403, detail="Senha incorreta.")
    
    try:
        deleted_count = crud.delete_all_validation_submissions(db)
        logging.info(f"{deleted_count} submissões de validação foram apagadas.")
        return {"status": "success", "message": f"{deleted_count} respostas foram apagadas com sucesso."}
    except Exception as e:
        logging.error(f"Falha ao apagar submissões de validação: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível apagar as respostas.")

@app.get("/sus_responses/", response_model=List[SUSResponseModel])
def get_sus_responses(db: Session = Depends(get_db)):
    """
    Retorna todas as respostas do questionário SUS.
    """
    responses = crud.get_all_sus_responses(db)
    return responses

@app.get("/sus_responses/{user_identifier}", response_model=List[SUSResponseModel])
def get_user_sus_responses(user_identifier: str, db: Session = Depends(get_db)):
    """
    Retorna as respostas do questionário SUS de um usuário específico.
    """
    responses = db.query(models.SUSResponse).filter(
        models.SUSResponse.user_identifier == user_identifier
    ).order_by(models.SUSResponse.created_at).all()
    return responses

@app.post("/delete_sus_responses/")
def delete_sus_responses(request: AdminActionRequest, db: Session = Depends(get_db)):
    """
    Apaga todas as respostas do SUS se a senha estiver correta.
    """
    if request.password != "admin":
        raise HTTPException(status_code=403, detail="Senha incorreta.")
    
    try:
        deleted_count = crud.delete_all_sus_responses(db)
        logging.info(f"{deleted_count} respostas SUS foram apagadas.")
        return {"status": "success", "message": f"{deleted_count} respostas SUS foram apagadas com sucesso."}
    except Exception as e:
        logging.error(f"Falha ao apagar respostas SUS: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível apagar as respostas SUS.")


# --- Constantes e Configurações ---
CONSENT_FORMS_DIR = "consent_forms"
os.makedirs(CONSENT_FORMS_DIR, exist_ok=True)

# Adicione o texto do TCLE aqui para mantê-lo centralizado
TCLE_TEXT = """Você está sendo convidado(a) a participar de um projeto de pesquisa. Antes de assinar o termo de consentimento para a sua participação, por favor leia com atenção todas as informações.

DESCRIÇÃO GERAL DA PESQUISA
Você está sendo convidado(a) a participar da validação de uma ferramenta de diagnóstico sindrômico e topográfico em Neurologia Vascular. O diagnóstico topográfico em Neurologia representa uma faceta essencial na prática clínica, integrando um profundo conhecimento em Neuroanatomia e Semiologia. Este tipo de diagnóstico é crucial para a correta interpretação de neuroimagem, sendo indispensável na avaliação de distúrbios neurológicos complexos como o Acidente Vascular Cerebral (AVC). A habilidade de localizar precisamente uma lesão no sistema nervoso não só direciona o manejo clínico apropriado, mas também pode guiar as intervenções terapêuticas. Objetivo da pesquisa: Validar uma ferramenta digital de diagnóstico sindrômico e topográfico em Neurologia Vascular.

PROCEDIMENTOS DO ESTUDO
Se você aceitar participar desse estudo, você fará: Um questionário anonimizado com casos simulados de pacientes com histórico de doença cerebrovascular. Você responderá a questões sobre o provável diagnóstico sindrômico e topográfico de cada caso hipotético. Suas respostas não serão identificadas, reveladas ou usadas para qualquer propósito senão o especificado neste termo.

Riscos em participar da pesquisa: A participação na pesquisa não oferece riscos diretos ou indiretos aos sujeitos de pesquisa, exceto pelo risco de perda do sigilo dos dados ou eventual desconforto pelo tempo que emanará ao responder aos casos.
Benefícios: Não há benefícios diretos aos participantes. No entanto, esta pesquisa se propõe a oferecer uma plataforma para auxílio no diagnóstico sindrômico e topográfico. Os pesquisadores supõem que a ferramenta melhorará a acurácia desses diagnósticos em Neurologia.
Acesso a resultados parciais ou finais da pesquisa: Você tem o direito, caso solicite, a ter acesso aos resultados da pesquisa.
Custos envolvidos pela participação da pesquisa: Sua participação na pesquisa não envolve custos, tampouco compensações financeiras.

PARTICIPAÇÃO VOLUNTÁRIA
Você é livre para participar ou desistir do estudo em qualquer momento. Se você tiver qualquer dúvida quanto ao desenvolvimento da pesquisa ou aos seus direitos como participante, poderá entrar em contato com os pesquisadores responsáveis (Dr. Thales Pardini ou Dra. Millene Rodrigues Camilo, Rua Bernardino de Campos, 1000, Centro, Ribeirão Preto/SP, no telefone (16) 36023798). A realização deste estudo foi autorizada pelo Comitê de Ética em Pesquisa (CEP) do Hospital das Clínicas da Faculdade de Medicina de Ribeirão Preto, Universidade de São Paulo. O papel do CEP é supervisionar estudos em seres humanos e garantir que os direitos, a segurança e bem-estar de todos os participantes sejam protegidos.
Em caso de qualquer dúvida ou reclamação a respeito deste estudo, você também poderá contatar o CEP, de segunda à sexta, das 08 às 17 h (Campus Universitário, SN, Monte Alegre, Ribeirão Preto/SP), no telefone (16) 3602-2228. Para maiores informações sobre os direitos dos participantes de pesquisa, leia a Cartilha dos Direitos dos Participantes de Pesquisa elaborada pela Comissão Nacional de Ética em Pesquisa (Conep), que está disponível para leitura no site: http://conselho.saude.gov.br/images/comissoes/conep/img/boletins/Cartilha_Direitos_Participantes_ de_Pesquisa_2020.pdf Assinando esse consentimento, você não desiste de nenhum de seus direitos. Além disso, você não libera os investigadores de suas responsabilidades legais e profissionais no caso de alguma situação que lhe prejudique.

CONFIDENCIALIDADE
Todas as informações coletadas neste estudo serão confidenciais. Nenhum dado sensível que possa identificá-lo será utilizado. Portanto, asseguramos que seus dados serão utilizados especificamente para esta pesquisa, a sua confidencialidade será resguardada pela equipe do centro de pesquisa, conforme disposto na Res. CNS 466/12 e na Lei Geral de Proteção de Dados (Lei n. 13.709/2018). CONSENTIMENTO Ao consentir, você confirma ter lido e compreendido este documento, autorizando o uso e divulgação das informações obtidas nas condições de preservação da confidencialidade e anonimato, sem renunciar a qualquer um de seus direitos legais. Ao concordar, será disponibilizada uma cópia desse documento.

O consentimento será dado ao selecionar a opção "Concordo em participar".
"""

@app.post("/consent/generate/")
def generate_consent_pdf(request: AdminActionRequest, db: Session = Depends(get_db)): # Reutilizando AdminActionRequest para simplicidade
    """
    Gera um PDF do TCLE, salva no servidor e retorna para download.
    Usa o campo 'password' do AdminActionRequest para passar o 'user_identifier'.
    """
    user_identifier = request.password
    timestamp = datetime.now(ZoneInfo("America/Sao_Paulo"))
    date_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Adiciona o título
    pdf.cell(200, 10, txt="Termo de Consentimento Livre e Esclarecido", ln=True, align='C')
    pdf.ln(10)

    # Adiciona o corpo do TCLE
    # Nota: A biblioteca fpdf2 espera que o texto esteja no formato Latin-1 por padrão.
    # Usamos encode/decode para lidar com caracteres especiais do português.
    full_text = TCLE_TEXT.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, txt=full_text)
    pdf.ln(10)

    # Adiciona a "assinatura"
    signature_text = (
        f"Consentimento fornecido pelo participante com identificador (final do CPF): {user_identifier}\n"
        f"Data e Hora do Consentimento: {date_str}"
    )
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 5, txt=signature_text.encode('latin-1', 'replace').decode('latin-1'))

    # Salva o PDF no servidor
    pdf_filename = f"TCLE_consent_{user_identifier}_{timestamp.strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(CONSENT_FORMS_DIR, pdf_filename)
    pdf.output(pdf_path)

    return FileResponse(path=pdf_path, media_type='application/pdf', filename=pdf_filename)


@app.post("/admin/download_csv/")
def download_csv(request: AdminActionRequest, db: Session = Depends(get_db)):
    """
    Gera e retorna um arquivo CSV com todas as respostas de validação e SUS,
    com os dados pivotados.
    """
    if request.password != "admin":
        raise HTTPException(status_code=403, detail="Senha incorreta.")

    submissions = crud.get_all_validation_submissions(db)
    sus_responses = crud.get_all_sus_responses(db)
    
    if not submissions:
        raise HTTPException(status_code=404, detail="Nenhuma resposta de validação encontrada para exportar.")

    # Converte os dados de validação para um DataFrame do pandas
    data_for_df = [{
        "user_identifier": s.user_identifier,
        "user_group": s.user_group,
        "user_type": s.user_type,
        "case_id": s.case_id,
        "answer": s.answer
    } for s in submissions]
    df = pd.DataFrame(data_for_df)

    # Pivota o DataFrame para ter usuários como linhas e casos como colunas
    pivot_df = df.pivot_table(
        index=['user_identifier', 'user_group', 'user_type'],
        columns='case_id',
        values='answer',
        aggfunc='first'  # Usa 'first' para o caso de múltiplas respostas, pega a primeira
    ).reset_index()

    # Renomeia as colunas dos casos clínicos para um formato amigável para análise
    rename_dict = {
        col: f"caso_clinico_{col.split()[-1]}"
        for col in pivot_df.columns
        if col.startswith("CASO CLÍNICO")
    }
    pivot_df.rename(columns=rename_dict, inplace=True)

    # Adiciona dados SUS ao DataFrame
    if sus_responses:
        sus_data = {}
        for sus in sus_responses:
            user_id = sus.user_identifier
            if user_id not in sus_data:
                sus_data[user_id] = {
                    f'sus_q{i}': getattr(sus, f'q{i}')
                    for i in range(1, 11)
                }
                # Calcula o score SUS
                score = 0
                # Questões ímpares (1,3,5,7,9): contribuição = resposta - 1
                for i in [1, 3, 5, 7, 9]:
                    score += getattr(sus, f'q{i}') - 1
                # Questões pares (2,4,6,8,10): contribuição = 5 - resposta
                for i in [2, 4, 6, 8, 10]:
                    score += 5 - getattr(sus, f'q{i}')
                sus_data[user_id]['sus_score'] = score * 2.5
        
        # Converte para DataFrame e faz merge
        sus_df = pd.DataFrame.from_dict(sus_data, orient='index')
        sus_df.index.name = 'user_identifier'
        sus_df.reset_index(inplace=True)
        
        # Merge com o DataFrame principal
        pivot_df = pivot_df.merge(sus_df, on='user_identifier', how='left')

    # Cria um buffer de string para o CSV
    output = StringIO()
    pivot_df.to_csv(output, index=False)
    output.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=louis_validation_dataset.csv"
    }
    
    return StreamingResponse(output, media_type="text/csv", headers=headers)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Inferência de Síndromes. Use o endpoint /docs para ver a documentação."} 