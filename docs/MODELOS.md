# Guia de Modelos - Louis Final

**Última atualização**: 05/Out/2025

Este documento descreve os modelos de IA disponíveis para uso no sistema Louis e como configurá-los.

---

## 📋 Modelos Suportados

### 1. Gemini 2.5 Flash (Atual - Padrão)

**Provedor**: Google AI
**Modelo**: `gemini-2.5-flash` (ou `gemini-flash-latest`)
**Status**: ✅ Implementado e em produção

#### Características
- **Context Window**: 1.048.576 tokens (1M)
- **Output Tokens**: 65.536 tokens
- **Modalidades**: Texto, imagens, vídeo, áudio
- **Recursos**:
  - ✅ Thinking (raciocínio)
  - ✅ Function calling
  - ✅ Structured outputs (JSON)
  - ✅ Caching
  - ✅ Code execution
  - ✅ Grounding (busca)

#### Preços
- **Entrada**: ~$0.10 / 1M tokens
- **Saída**: ~$0.30 / 1M tokens
- **Melhor custo-benefício** para alto volume

#### Quando Usar
- ✅ Processamento em larga escala
- ✅ Baixa latência necessária
- ✅ Alto volume de requisições
- ✅ Casos de uso com agentes
- ✅ Tarefas que exigem raciocínio

#### Configuração Atual (backend/services/inference_service.py)
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Configuração com thinking desabilitado (para latência)
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

---

### 2. Grok 4 Fast (Proposto)

**Provedor**: xAI
**Modelo**: `grok-4-fast-reasoning` ou `grok-4-fast-non-reasoning`
**Status**: ⚠️ Não implementado (documentação apenas)

#### Características
- **Context Window**: 2.000.000 tokens (2M)
- **Modalidades**: Texto apenas (sem imagem/vídeo/áudio)
- **Recursos**:
  - ✅ Reasoning (raciocínio acelerado)
  - ✅ Structured outputs (JSON)
  - ✅ Function calling
  - ✅ Live Search (com custo adicional)
  - ❌ Não suporta `presencePenalty`, `frequencyPenalty`, `stop`

#### Preços
- **Entrada**: $0.20 / 1M tokens
- **Saída**: $0.50 / 1M tokens
- **Live Search**: $25 / 1.000 fontes ($0.025/fonte)
- **Mais barato que Gemini 2.5** em alguns casos

#### Rate Limits
- **TPM**: 4M tokens/minuto
- **RPM**: 480 requests/minuto

#### Quando Usar
- ✅ Contexto muito longo (até 2M tokens)
- ✅ Tarefas de raciocínio complexo
- ✅ Baixo custo para inferência
- ❌ Não usar para multimodal (sem suporte)

#### Configuração Proposta
```python
import openai

client = openai.OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

response = client.chat.completions.create(
    model="grok-4-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are a test assistant."},
        {"role": "user", "content": "Testing latency."}
    ],
    temperature=0.2,
    stream=False
)
```

---

## 🔧 Configuração de API Keys

### Arquivo `.env` (atual)
```bash
# Google Gemini
GEMINI_API_KEY="<sua-key-aqui>"

# OpenAI (reservado)
OPEN_AI_KEY="<sua-key-aqui>"

# xAI Grok (novo - não implementado)
XAI_API_KEY="<sua-key-aqui>"
```

**⚠️ IMPORTANTE**:
- As API keys reais estão no `.env` do projeto (não versionado)
- Nunca commitar `.env` ou expor keys em código
- Para obter keys:
  - Gemini: https://makersuite.google.com/app/apikey
  - xAI Grok: https://console.x.ai/api-keys

---

## 📊 Comparação de Modelos

| Característica | Gemini 2.5 Flash | Grok 4 Fast |
|----------------|------------------|-------------|
| **Context Window** | 1M tokens | 2M tokens |
| **Modalidades** | Texto, Imagem, Vídeo, Áudio | Apenas Texto |
| **Thinking** | ✅ Sim (desabilitável) | ✅ Sim (sempre ativo) |
| **Preço Input** | ~$0.10 / 1M | $0.20 / 1M |
| **Preço Output** | ~$0.30 / 1M | $0.50 / 1M |
| **Latência** | Baixa | Muito Baixa |
| **Structured Outputs** | ✅ Sim | ✅ Sim |
| **Function Calling** | ✅ Sim | ✅ Sim |
| **Knowledge Cutoff** | Jan 2025 | Nov 2024 |
| **Live Search** | ✅ Grounding | ✅ Sim ($0.025/fonte) |

---

## 🎯 Casos de Uso Recomendados

### Use Gemini 2.5 Flash quando:
- Precisar processar **imagens, vídeos ou áudio**
- Trabalhar com **RAG multimodal**
- Precisar de **grounding** (busca integrada)
- Quiser **menor custo** para alto volume

### Use Grok 4 Fast quando:
- Precisar de **contexto muito longo** (>1M tokens)
- Trabalhar apenas com **texto**
- Precisar de **latência extremamente baixa**
- Quiser **raciocínio acelerado** sem configuração

---

## 🚀 Roadmap de Implementação

### Fase 1: Documentação ✅
- [x] Criar docs/MODELOS.md
- [x] Criar docs/GROK_4_FAST.md
- [x] Criar docs/GEMINI_FLASH.md

### Fase 2: Backend (Não implementado)
- [ ] Adicionar suporte a múltiplos modelos
- [ ] Criar service para Grok
- [ ] Implementar seleção de modelo via API
- [ ] Adicionar fallback (se Grok falhar, usar Gemini)

### Fase 3: Frontend (Não implementado)
- [ ] Adicionar dropdown de seleção de modelo
- [ ] Mostrar características do modelo selecionado
- [ ] Indicar custos estimados por consulta

### Fase 4: Testes e Validação (Não implementado)
- [ ] Comparar qualidade de inferência
- [ ] Medir latência real
- [ ] Calcular custo real
- [ ] Decidir modelo padrão

---

## 📝 Notas Importantes

### Compatibilidade com Sistema Atual
O sistema Louis atual usa **Gemini 2.5 Flash** e está otimizado para:
- Extração de palavras-chave (keywords)
- Busca em 52 capítulos (RAG)
- Inferência de síndromes (isquêmicas + hemorrágicas)
- Matching com imagens anatômicas

**Migrar para Grok requer**:
1. Adaptar prompts (Grok não tem multimodal)
2. Remover referências a imagens (ou manter Gemini para isso)
3. Testar qualidade das inferências
4. Validar com dados reais (comparar com Gemini)

### Recomendação Atual
**Manter Gemini 2.5 Flash como padrão** até:
- Testar Grok em ambiente de staging
- Validar qualidade das inferências
- Confirmar redução de custos
- Garantir que não afeta validação científica

---

## 🔗 Links Úteis

### Gemini
- [Google AI Studio](https://aistudio.google.com/)
- [Documentação Oficial](https://ai.google.dev/gemini-api/docs)
- [Preços](https://ai.google.dev/pricing)
- [API Key Console](https://makersuite.google.com/app/apikey)

### Grok
- [xAI Console](https://console.x.ai/api-keys)
- [Documentação Oficial](https://docs.x.ai/)
- [Status do Serviço](https://status.x.ai)
- [Discord de Desenvolvedores](https://discord.gg/xaidev)

---

**Última revisão**: 05/Out/2025
**Responsável**: Dr. Thales Pardini
**Status**: Documentação completa, implementação pendente
