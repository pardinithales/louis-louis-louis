import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models.api_models import InferenceRequest, InferenceResponse
from .services.inference_service import run_full_inference_process

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="API de Inferência de Síndromes Neurológicas",
    description="Use esta API para obter uma inferência de 4 síndromes neurológicas com base em sinais clínicos.",
    version="1.0.0"
)

# Configuração do CORS para permitir requisições de qualquer origem.
# Em um ambiente de produção, é recomendado restringir para domínios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Monta o diretório 'images' para ser servido estaticamente
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.post("/infer/", response_model=InferenceResponse)
async def infer_syndrome(request: InferenceRequest):
    """
    Recebe um quadro clínico e retorna as 4 síndromes mais prováveis.
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

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Inferência de Síndromes. Use o endpoint /docs para ver a documentação."} 