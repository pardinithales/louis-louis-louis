# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo de dependências para o diretório de trabalho
COPY backend/requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do backend, os capítulos e as imagens para o contêiner
COPY ./backend /app/backend
COPY ./chapters /app/chapters
COPY ./images /app/images

# Exponha a porta em que o aplicativo é executado
EXPOSE 8000

# Comando para executar a aplicação usando Uvicorn
# O host 0.0.0.0 torna o servidor acessível de fora do contêiner
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 