# Gemini 2.5 Flash - Guia de Consulta Rápida

**Última atualização**: 05/Out/2025

---

## 🎯 Visão Geral

**Gemini 2.5 Flash** é o modelo da Google com **melhor custo-benefício** e recursos completos. Ideal para processamento em grande escala, baixa latência e tarefas de alto volume que exigem raciocínio.

### Especificações Principais
- **Context Window**: 1.048.576 tokens (1M)
- **Output Tokens**: 65.536 tokens
- **Modalidades**: Texto, Imagens, Vídeo, Áudio
- **Knowledge Cutoff**: Janeiro 2025
- **Suporte**: Thinking, Function calling, Structured outputs, Caching

---

## 📊 Detalhes do Modelo

| Propriedade | Descrição |
|-------------|-----------|
| **Código do modelo** | `gemini-flash-latest` (recomendado) ou versões específicas como `gemini-2.5-flash` |
| **Tipos de dados** | Entrada: Texto, imagens, vídeo, áudio / Saída: Texto |
| **Limite input** | 1.048.576 tokens |
| **Limite output** | 65.536 tokens |
| **Knowledge cutoff** | Janeiro 2025 |

### Recursos Disponíveis
- ✅ **Geração de áudio**: incompatível
- ✅ **API Batch**: Compatível
- ✅ **Armazenamento em cache**: Compatível
- ✅ **Execução de código**: Compatível
- ✅ **Chamadas de função**: Compatível
- ✅ **Geração de imagens**: incompatível
- ✅ **API Live**: incompatível
- ✅ **Pesquisa com embasamento (Grounding)**: Compatível
- ✅ **Respostas estruturadas**: Compatível
- ✅ **Pensar (Thinking)**: Compatível
- ✅ **Contexto do URL**: Compatível

### Versões Disponíveis
- **Latest (recomendado)**: `gemini-flash-latest` - sempre aponta para a versão mais recente
- **Estável**: `gemini-2.5-flash` - versão específica do 2.5 Flash
- **Preview**: `gemini-2.5-flash-preview-05-20` - versão de pré-lançamento

---

## 💰 Preços Estimados

- **Input**: ~$0.10 / 1M tokens
- **Output**: ~$0.30 / 1M tokens
- **Cached tokens**: ~75% de desconto

**Melhor custo-benefício** para alto volume de requisições.

---

## 🔧 Implementação com Python

### Instalação
```bash
pip install google-genai
```

### Configuração Básica (SDK Novo)

```python
import os
from google import genai
from google.genai import types

# Configurar cliente
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Fazer requisição
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="How does AI work?"
)

print(response.text)
```

### Configuração Básica (SDK Legado - Atual no Louis)

```python
import os
import google.generativeai as genai

# Configurar API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Criar modelo
model = genai.GenerativeModel("gemini-flash-latest")

# Gerar resposta
response = model.generate_content("How does AI work?")
print(response.text)
```

---

## 💡 Thinking (Pensamento) - ATUALIZADO

Os modelos 2.5 Flash e Pro têm **"thinking" (pensamento dinâmico) ativado por padrão** para melhorar a qualidade, o que:
- ✅ Melhora significativamente habilidades de raciocínio e planejamento de várias etapas
- ✅ Muito eficaz para tarefas complexas (programação, matemática, análise)
- ⚠️ Aumenta o uso de tokens (thoughtsTokenCount)
- ⚠️ Pode aumentar a latência significativamente

### Orçamentos de Thinking (thinkingBudget)

| Modelo | Padrão | Intervalo | Desativar | Dinâmico |
|--------|--------|-----------|-----------|----------|
| 2.5 Flash | Dinâmico | 0 - 24576 | `thinkingBudget=0` | `thinkingBudget=-1` |
| 2.5 Pro | Dinâmico | 128 - 32768 | N/A (não pode desativar) | `thinkingBudget=-1` |
| 2.5 Flash-Lite | OFF | 512 - 24576 | `thinkingBudget=0` | `thinkingBudget=-1` |

### Desabilitar Thinking (para latência menor) - SDK NOVO

⚠️ **IMPORTANTE**: Desabilitar thinking **REQUER o SDK NOVO** (`from google import genai`).

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Desabilita thinking
    )
)

print(response.text)
```

### SDK Legado (google.generativeai) - SEM SUPORTE

⚠️ **LIMITAÇÃO CRÍTICA**: O SDK legado `import google.generativeai as genai` **NÃO SUPORTA** controle de thinking.

```python
# ❌ SDK LEGADO - NÃO PODE DESABILITAR THINKING
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-latest")

# Thinking estará SEMPRE ativo (padrão dinâmico)
# Não há parâmetro para desabilitar
response = model.generate_content("How does AI work?")
```

**Consequências para o Louis:**
- O sistema atual usa SDK legado
- Thinking está **sempre ativo** (não pode ser desabilitado)
- Isso explica a latência de ~19-22 segundos por inferência
- **Para reduzir latência, é necessário migrar para SDK novo**

---

## ⚙️ Instruções do Sistema e Configurações

### System Instructions

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Hello there",
    config=types.GenerateContentConfig(
        system_instruction="You are a neurologist assistant. Provide clear, evidence-based answers."
    )
)

print(response.text)
```

### Ajustar Temperature

```python
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="Explain cerebral ischemia",
    config=types.GenerateContentConfig(
        temperature=0.2,  # Baixa para respostas precisas
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192
    )
)
```

---

## 🖼️ Entradas Multimodais

### Processar Imagem

```python
from PIL import Image
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Carregar imagem
image = Image.open("/path/to/brain_scan.png")

# Enviar imagem + texto
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=[image, "Describe this brain scan."]
)

print(response.text)
```

### Processar Vídeo

```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Upload de vídeo
video_file = genai.upload_file(path="/path/to/video.mp4")

# Gerar resposta
model = genai.GenerativeModel("gemini-flash-latest")
response = model.generate_content([video_file, "Summarize this video."])

print(response.text)
```

### Processar Áudio

```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Upload de áudio
audio_file = genai.upload_file(path="/path/to/audio.mp3")

# Gerar resposta
model = genai.GenerativeModel("gemini-flash-latest")
response = model.generate_content([audio_file, "Transcribe this audio."])

print(response.text)
```

---

## 📤 Streaming de Respostas

```python
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Streaming habilitado
response = client.models.generate_content_stream(
    model="gemini-flash-latest",
    contents="Explain how AI works"
)

for chunk in response:
    print(chunk.text, end="")
```

---

## 💬 Conversas Multi-Turno (Chat)

```python
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Criar chat
chat = client.chats.create(model="gemini-flash-latest")

# Primeiro turno
response = chat.send_message("I have 2 dogs in my house.")
print(response.text)

# Segundo turno (mantém histórico)
response = chat.send_message("How many paws are in my house?")
print(response.text)

# Ver histórico completo
for message in chat.get_history():
    print(f'{message.role}: {message.parts[0].text}')
```

---

## 📋 Structured Outputs (JSON)

```python
import google.generativeai as genai
import json

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")

# Solicitar JSON estruturado
prompt = """
Analyze the following clinical presentation and return a JSON with:
- syndromes: array of possible syndrome names
- confidence: float 0-1 for each syndrome
- reasoning: brief explanation

Clinical text: Patient with left hemiparesis and aphasia.
"""

response = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json"
    )
)

# Parse JSON
result = json.loads(response.text)
print(json.dumps(result, indent=2))
```

---

## 🎯 Implementação Atual no Louis

### Localização
`backend/services/inference_service.py`

### Configuração Atual (SDK Legado)
```python
import google.generativeai as genai
import os

# Configurar API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Criar modelo
model = genai.GenerativeModel("gemini-flash-latest")

# Configuração de geração
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Exemplo de uso no Louis
response = model.generate_content(
    contents=[
        {"role": "user", "parts": [{"text": prompt_text}]}
    ],
    generation_config=generation_config
)
```

### ⚠️ Problema de Performance Identificado

**Status Atual (05/Out/2025):**
- Latência média: **~19-22 segundos** por inferência
- Causa raiz: **Thinking dinâmico sempre ativo** (SDK legado não permite desabilitar)
- Breakdown de tempo:
  - `extract_keywords()`: ~14 segundos (70% do tempo total)
  - `search_chapters_for_snippets()`: ~1 segundo
  - `get_syndrome_inference()`: ~4-7 segundos

**Tentativa de Otimização (05/Out/2025):**
- Quick Win #1 (desabilitar thinking): **FALHOU** - SDK legado não suporta
- Quick Win #2 (reutilizar modelos): **IMPLEMENTADO** - ganho mínimo (~2-3%)
- Resultado: Performance **PIOROU** para ~77 segundos (provavelmente por bug na implementação)
- Ação: **REVERTIDO** para backup anterior

### Funções Principais no Louis
1. **extract_keywords()**: Extrai palavras-chave do texto clínico (gargalo de 14s)
2. **search_chapters_for_snippets()**: Busca snippets relevantes nos 52 capítulos
3. **get_syndrome_inference()**: Infere síndromes (isquêmicas + hemorrágicas)
4. **get_syndrome_inference_with_full_context()**: Fallback com contexto completo
5. **run_full_inference_process()**: Orquestra todo o pipeline RAG

---

## 🚀 Otimizações para Louis

### 0. Migrar para SDK Novo (CRÍTICO para performance)

**Impacto esperado**: Redução de 70-80% na latência (~19s → ~4-6s)

⚠️ **ATENÇÃO**: Esta migração requer testes extensivos antes de deploy em produção!

#### Instalação do SDK Novo

```bash
# Desinstalar SDK legado
pip uninstall google-generativeai

# Instalar SDK novo
pip install google-genai
```

#### Atualizar requirements.txt

```txt
# Substituir:
google-generativeai

# Por:
google-genai
```

#### Exemplo de Migração no inference_service.py

**ANTES (SDK Legado):**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")
response = await model.generate_content_async(prompt)
```

**DEPOIS (SDK Novo com thinking desabilitado):**
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

# Modelo reutilizável com thinking desabilitado
async def generate_with_no_thinking(prompt: str) -> str:
    response = await client.models.generate_content_async(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.2,
            top_p=0.95,
            top_k=40,
        )
    )
    return response.text
```

#### Checklist de Migração

- [ ] Backup completo do sistema (`./backup_completo.sh "antes-migracao-sdk"`)
- [ ] Atualizar `backend/requirements.txt`
- [ ] Modificar `backend/services/inference_service.py`:
  - [ ] Trocar import: `from google import genai`
  - [ ] Criar cliente global: `client = genai.Client(api_key=...)`
  - [ ] Atualizar `extract_keywords()` com `thinking_budget=0`
  - [ ] Atualizar `get_syndrome_inference()` com `thinking_budget=0`
  - [ ] Atualizar `get_syndrome_inference_with_full_context()` com `thinking_budget=0`
- [ ] Rebuild containers: `docker-compose up -d --build backend`
- [ ] Testar em ambiente de desenvolvimento
- [ ] Medir performance real (esperar ~4-6s por inferência)
- [ ] Validar qualidade das inferências (comparar com baseline)
- [ ] Deploy em produção
- [ ] Monitorar métricas por 24-48h

### 1. Caching de Contexto Longo

Para os 52 capítulos que são usados repetidamente:

```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Cache de contexto (capítulos)
cache = genai.caching.CachedContent.create(
    model="gemini-flash-latest",
    contents=[{"role": "user", "parts": [{"text": all_chapters_text}]}],
    ttl="3600s"  # 1 hora
)

# Usar cache em requisições
model = genai.GenerativeModel.from_cached_content(cache)
response = model.generate_content("What are ischemic syndromes?")
```

**Economia**: ~75% no custo de tokens de entrada

### 2. Batch Processing

Para processar múltiplos casos de validação:

```python
# TODO: Implementar batch API quando disponível
```

### 3. Grounding (Busca com Embasamento)

Para casos que exigem informações atualizadas:

```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-latest")

response = model.generate_content(
    "What are the latest stroke treatments in 2025?",
    tools="google_search_retrieval"  # Habilita grounding
)

print(response.text)
```

---

## ⚠️ Limitações

### Não suporta:
- ❌ Geração de áudio
- ❌ Geração de imagens
- ❌ API Live (tempo real)

### Cuidados:
- ⚠️ Thinking aumenta tokens (~30-50% mais)
- ⚠️ Context window de 1M (menor que Grok 4 Fast)
- ⚠️ Knowledge cutoff em Jan 2025

---

## 📚 Recursos Adicionais

- [Google AI Studio](https://aistudio.google.com/) - Testar modelos interativamente
- [Documentação Oficial](https://ai.google.dev/gemini-api/docs)
- [Preços](https://ai.google.dev/pricing)
- [API Key Console](https://makersuite.google.com/app/apikey)
- [Guia de Comandos](https://ai.google.dev/gemini-api/docs/prompting-intro)
- [Exemplos de Código](https://github.com/google-gemini/cookbook)

---

## 🎓 Boas Práticas

### 1. Comandos Claros
```python
# ❌ Ruim
"Tell me about stroke"

# ✅ Bom
"List the 5 most common ischemic stroke syndromes with their clinical presentations."
```

### 2. Few-Shot Learning
```python
prompt = """
Extract keywords from clinical text. Examples:

Input: "Patient with left hemiparesis and dysarthria"
Output: ["hemiparesis", "left", "dysarthria", "motor deficit", "speech"]

Input: "Sudden vision loss in right eye"
Output: ["vision loss", "sudden", "right eye", "monocular", "visual deficit"]

Now extract from: "{clinical_text}"
"""
```

### 3. Structured Prompts
```python
system_instruction = """
You are a neurologist assistant specialized in stroke diagnosis.
- Always provide evidence-based answers
- Cite relevant medical literature when available
- Use ICD-10 codes when applicable
- Format output as JSON when requested
"""
```

---

**Última revisão**: 05/Out/2025
**Status**: ✅ Implementado e em produção
**API Key**: Configurada no `.env` (GEMINI_API_KEY)
**Uso atual**: 100% das inferências do Louis
