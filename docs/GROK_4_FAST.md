# Grok 4 Fast - Guia de Consulta Rápida

**Última atualização**: 05/Out/2025

---

## 🎯 Visão Geral

**Grok 4 Fast** é a linha de modelos de raciocínio acelerado da xAI, com foco em **baixo custo** e **baixa latência**.

### Especificações Principais
- **Context Window**: 2.000.000 tokens (2M)
- **Modalidades**: Texto apenas
- **Knowledge Cutoff**: Novembro 2024
- **Suporte**: Structured outputs (JSON), Function calling, Reasoning
- **Acesso em tempo real**: Não (exceto com Live Search)

---

## 📊 Catálogo de Modelos Grok

| Modelo | Modalidades | Capacidade | Contexto | TPM / RPM | Preço Input | Preço Output |
|--------|-------------|------------|----------|-----------|-------------|--------------|
| `grok-4-fast-reasoning` | Texto | Raciocínio | 2M | 4M / 480 | $0.20/1M | $0.50/1M |
| `grok-4-fast-non-reasoning` | Texto | Não-raciocínio | 2M | 4M / 480 | $0.20/1M | $0.50/1M |
| `grok-4-0709` | Texto | Raciocínio | 2M | 4M / 480 | $3.00/1M | $15.00/1M |
| `grok-code-fast-1` | Texto | Coding agentic | 256k | 2M / 480 | $0.20/1M | $1.50/1M |
| `grok-3` | Texto | Raciocínio | 131k | - / 600 | $3.00/1M | $15.00/1M |
| `grok-3-mini` | Texto | Raciocínio | 131k | - / 480 | $0.30/1M | $0.50/1M |
| `grok-2-vision-1212` | Texto + Imagem | Multimodal | 32.768 | - / 600 | $2.00/1M | $10.00/1M |
| `grok-2-image-1212` | Imagem | Geração | - | - / 300 | $0.07/imagem | - |

**Recomendação para Louis**: `grok-4-fast-reasoning` (melhor custo-benefício)

---

## 🔑 Diferenças Importantes vs Grok 3

- Grok 4 é **sempre um modelo de raciocínio**
- **NÃO suporta**: `presencePenalty`, `frequencyPenalty`, `stop`, `reasoning_effort`
- Mensagens podem ser enviadas em **qualquer ordem** de papéis (`system`, `user`, `assistant`)

---

## 💰 Política de Uso e Custos

### Custos Principais
- **Inferência**: $0.20/1M input + $0.50/1M output
- **Live Search**: $25 / 1.000 fontes ($0.025 por fonte)
- **Document Search (Collections API)**: $2.50 / 1k requests
- **Armazenamento**: Gratuito para arquivos e coleções
- **Usage Guidelines Violation**: $0.05 por requisição marcada

### Limitações
- **Sem eventos em tempo real**: é necessário habilitar Live Search ou fornecer contexto atualizado manualmente
- **Live Search**: Contagem disponível em `response.usage.num_sources_used`

---

## 🔧 Implementação com Python

### Instalação
```bash
pip install openai
```

### Configuração Básica

```python
import os
from openai import OpenAI

# Configurar cliente xAI (compatível com OpenAI SDK)
client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# Fazer requisição
response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are a medical assistant."},
        {"role": "user", "content": "What are the symptoms of stroke?"}
    ],
    temperature=0.2,  # Baixa temperatura para respostas precisas
    stream=False
)

print(response.choices[0].message.content)
```

### Exemplo com Streaming

```python
response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are a medical assistant."},
        {"role": "user", "content": "Explain cerebral ischemia."}
    ],
    temperature=0.2,
    stream=True  # Habilitar streaming
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Exemplo com Structured Output (JSON)

```python
import json

response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {
            "role": "system",
            "content": "You are a medical diagnosis assistant. Always respond in valid JSON."
        },
        {
            "role": "user",
            "content": "Patient has left hemiparesis and aphasia. Provide differential diagnosis."
        }
    ],
    temperature=0.2,
    response_format={"type": "json_object"}
)

# Parse JSON
result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))
```

---

## 🚀 Exemplo de Requisição cURL

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4-fast-reasoning",
    "stream": false,
    "temperature": 0.2,
    "messages": [
      {"role": "system", "content": "You are a neurologist assistant."},
      {"role": "user", "content": "What are common ischemic stroke syndromes?"}
    ]
  }'
```

---

## 📦 Estrutura da Resposta

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "grok-4-fast-reasoning",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "...",
        "reasoning_content": "... (opcional) ..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579,
    "prompt_tokens_details": {
      "text_tokens": 123,
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 200
    },
    "num_sources_used": 0
  }
}
```

**Campos importantes**:
- `reasoning_content`: Raciocínio interno do modelo (quando disponível)
- `reasoning_tokens`: Tokens usados no raciocínio
- `num_sources_used`: Fontes do Live Search usadas (se habilitado)

---

## ⚙️ Parâmetros de Configuração

### Parâmetros Aceitos
- `model`: Nome do modelo (ex: `grok-4-fast-reasoning`)
- `messages`: Lista de mensagens (role + content)
- `temperature`: Controle de aleatoriedade (0.0 - 2.0)
- `top_p`: Nucleus sampling (0.0 - 1.0)
- `max_tokens`: Máximo de tokens na resposta
- `stream`: Boolean para streaming (SSE)
- `response_format`: `{"type": "json_object"}` para JSON garantido

### Parâmetros NÃO Aceitos (geram erro)
- ❌ `presencePenalty`
- ❌ `frequencyPenalty`
- ❌ `stop`
- ❌ `reasoning_effort`

---

## 🔍 Live Search (Busca em Tempo Real)

**Custo**: $0.025 por fonte (mínimo $25 para 1.000 fontes)

```python
response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {"role": "user", "content": "What are the latest treatments for stroke in 2024?"}
    ],
    search_parameters={
        "enabled": True,
        "max_sources": 5  # Limitar número de fontes
    }
)

# Verificar quantas fontes foram usadas
sources_used = response.usage.num_sources_used
cost = sources_used * 0.025
print(f"Fontes usadas: {sources_used}, Custo: ${cost:.2f}")
```

---

## ⏱️ Timeouts e Rate Limits

### Rate Limits
- **TPM**: 4.000.000 tokens/minuto
- **RPM**: 480 requests/minuto

### Timeout Recomendado
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=300.0  # 5 minutos (recomendado para reasoning)
)
```

**Importante**: Modelos de raciocínio podem levar mais tempo. Configure timeout adequado.

---

## 🎯 Boas Práticas para Louis

### 1. Extração de Keywords
```python
response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {
            "role": "system",
            "content": "You are a medical keyword extractor. Extract keywords in English from clinical text."
        },
        {
            "role": "user",
            "content": f"Extract keywords from: {clinical_text}"
        }
    ],
    temperature=0.2,
    response_format={"type": "json_object"}
)
```

### 2. Inferência de Síndromes
```python
response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {
            "role": "system",
            "content": "You are a neurologist. Provide differential diagnosis based on clinical presentation."
        },
        {
            "role": "user",
            "content": f"Clinical text: {text}\n\nRelevant context from literature: {snippets}"
        }
    ],
    temperature=0.2,
    response_format={"type": "json_object"}
)
```

### 3. Fallback Strategy
```python
def infer_with_fallback(text, snippets):
    try:
        # Tentar Grok primeiro (mais barato)
        return infer_with_grok(text, snippets)
    except Exception as e:
        print(f"Grok failed: {e}, falling back to Gemini")
        # Fallback para Gemini
        return infer_with_gemini(text, snippets)
```

---

## ⚠️ Limitações para Louis

### NÃO suporta:
- ❌ **Imagens anatômicas** (só texto)
- ❌ **Vídeos ou áudios**
- ❌ **Multimodalidade**

### Impacto:
- Não pode fazer **matching com imagens** diretamente
- Precisa de **workaround** para associar síndromes com imagens

### Solução Proposta:
1. Usar **Grok para inferência de síndromes** (texto)
2. Usar **Gemini para matching de imagens** (multimodal)
3. Combinar resultados no backend

---

## 📚 Recursos Adicionais

- [xAI Console - API Keys](https://console.x.ai/api-keys)
- [xAI Service Status](https://status.x.ai)
- [xAI Developer Discord](https://discord.gg/xaidev)
- [OpenAI SDK Docs](https://platform.openai.com/docs/libraries/python-library)

---

**Última revisão**: 05/Out/2025
**Status**: Documentação completa, implementação pendente
**API Key**: Configurada no `.env` (XAI_API_KEY)
