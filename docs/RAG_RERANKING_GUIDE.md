# 🎯 Guia de Implementação: Reranking para Louis RAG

**Objetivo**: Reduzir latência de inferência de ~22s para ~10-12s através de reranking inteligente de snippets.

**Impacto Esperado**: 45-50% de redução na latência

---

## 📊 Problema Atual

### Performance Medida (Checkpoint #3)
```
Query simples:   ~17.5s
Query complexa:  ~22.5s
```

### Gargalo Identificado
1. ❌ **Volume excessivo de contexto**: Enviamos TODOS os snippets encontrados (~300KB)
2. ❌ **Baixa precisão**: Nem todos snippets são igualmente relevantes
3. ❌ **Latência da API**: Mais contexto = mais tempo de processamento

### Análise do Código Atual
```python
# backend/services/inference_service.py - Linha 102
def search_chapters_for_snippets(keywords: list[str]) -> str:
    all_snippets = set()

    # Busca por keywords em 52 capítulos
    for filename in chapter_files:
        for paragraph in paragraphs:
            for keyword in keywords:
                if keyword.lower() in paragraph.lower():
                    all_snippets.add(snippet)
                    break

    return "\n".join(all_snippets)  # ❌ Retorna TODOS os snippets
```

**Problema**: Se encontrar 30 snippets, envia todos os 30 para o Gemini (~300KB de contexto).

---

## ✅ Solução: Reranking com RankLLM

### Opções de Reranker

| Modelo | Descrição | VRAM | Latência | Qualidade |
|--------|-----------|------|----------|-----------|
| **RankGPT-4o** | GPT-4o Mini via API | 0GB | ~2-3s | ⭐⭐⭐⭐⭐ |
| **Cohere Rerank** | Cohere API | 0GB | ~1-2s | ⭐⭐⭐⭐⭐ |
| **cross-encoder/ms-marco** | Local (CPU-friendly) | 0GB | ~0.5s | ⭐⭐⭐⭐ |
| **RankZephyr** | Local (GPU) | 24GB | ~3-5s | ⭐⭐⭐⭐⭐ |

**Recomendação para Louis**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (local, CPU-friendly, sem custo adicional)

---

## 🛠️ Implementação - Opção 1: Reranker Local (CPU)

### 1. Instalação de Dependências

```bash
cd /root/louis-final
source venv/bin/activate  # Se usar venv

# Instalar bibliotecas necessárias
pip install sentence-transformers
pip install torch  # Se ainda não tiver

# Testar instalação
python -c "from sentence_transformers import CrossEncoder; print('✅ OK')"
```

### 2. Criar Módulo de Reranking

**Arquivo**: `backend/services/reranker.py`

```python
"""
Módulo de reranking para melhorar relevância de snippets no RAG.
Usa CrossEncoder para ordenar snippets por relevância à query.
"""

import logging
from typing import List, Tuple
from sentence_transformers import CrossEncoder

# Modelo leve e eficiente (CPU-friendly)
# Tamanho: ~90MB, Latência: ~0.5s para 30 snippets
MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class SnippetReranker:
    """
    Reranker de snippets usando cross-encoder.
    Ordena snippets por relevância semântica à query.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        """
        Inicializa o reranker com o modelo especificado.

        Args:
            model_name: Nome do modelo HuggingFace cross-encoder
        """
        self.model_name = model_name
        self._model = None
        logging.info(f"🔄 Inicializando reranker: {model_name}")

    @property
    def model(self) -> CrossEncoder:
        """Lazy loading do modelo (carrega apenas quando necessário)"""
        if self._model is None:
            self._model = CrossEncoder(self.model_name, max_length=512)
            logging.info(f"✅ Reranker carregado: {self.model_name}")
        return self._model

    def rerank(
        self,
        query: str,
        snippets: List[str],
        top_k: int = 5
    ) -> Tuple[List[str], List[float]]:
        """
        Reordena snippets por relevância à query.

        Args:
            query: Query do usuário (descrição clínica)
            snippets: Lista de snippets a serem reordenados
            top_k: Número de snippets a retornar (default: 5)

        Returns:
            Tupla com:
            - Lista dos top_k snippets mais relevantes
            - Lista dos scores correspondentes

        Example:
            >>> reranker = SnippetReranker()
            >>> query = "hemiparesia esquerda e afasia"
            >>> snippets = ["snippet1...", "snippet2...", "snippet3..."]
            >>> top_snippets, scores = reranker.rerank(query, snippets, top_k=3)
            >>> print(f"Top snippet score: {scores[0]:.3f}")
        """
        if not snippets:
            logging.warning("⚠️ Lista de snippets vazia para reranking")
            return [], []

        if len(snippets) <= top_k:
            logging.info(f"ℹ️ Snippets ({len(snippets)}) <= top_k ({top_k}), retornando todos")
            return snippets, [1.0] * len(snippets)

        logging.info(f"🔄 Rerankando {len(snippets)} snippets, retornando top-{top_k}")

        # Criar pares (query, snippet) para o cross-encoder
        pairs = [[query, snippet] for snippet in snippets]

        # Calcular scores de relevância
        scores = self.model.predict(pairs)

        # Ordenar por score (maior = mais relevante)
        scored_snippets = list(zip(snippets, scores))
        scored_snippets.sort(key=lambda x: x[1], reverse=True)

        # Retornar top_k
        top_snippets = [s[0] for s in scored_snippets[:top_k]]
        top_scores = [float(s[1]) for s in scored_snippets[:top_k]]

        logging.info(
            f"✅ Reranking completo. "
            f"Top score: {top_scores[0]:.3f}, "
            f"Bottom score: {top_scores[-1]:.3f}"
        )

        return top_snippets, top_scores

    def rerank_with_threshold(
        self,
        query: str,
        snippets: List[str],
        min_score: float = 0.3,
        max_results: int = 10
    ) -> Tuple[List[str], List[float]]:
        """
        Reordena e filtra snippets por score mínimo.

        Args:
            query: Query do usuário
            snippets: Lista de snippets
            min_score: Score mínimo para considerar relevante (0-1)
            max_results: Número máximo de resultados

        Returns:
            Tupla (snippets relevantes, scores)
        """
        if not snippets:
            return [], []

        # Criar pares e calcular scores
        pairs = [[query, snippet] for snippet in snippets]
        scores = self.model.predict(pairs)

        # Filtrar por score mínimo
        filtered = [
            (snippet, float(score))
            for snippet, score in zip(snippets, scores)
            if score >= min_score
        ]

        if not filtered:
            logging.warning(
                f"⚠️ Nenhum snippet passou o threshold {min_score}. "
                f"Retornando top-3 mesmo assim."
            )
            # Fallback: retornar top-3 mesmo que abaixo do threshold
            filtered = sorted(
                zip(snippets, scores),
                key=lambda x: x[1],
                reverse=True
            )[:3]

        # Ordenar e limitar
        filtered.sort(key=lambda x: x[1], reverse=True)
        filtered = filtered[:max_results]

        top_snippets = [s[0] for s in filtered]
        top_scores = [s[1] for s in filtered]

        logging.info(
            f"✅ Filtrados {len(top_snippets)}/{len(snippets)} snippets "
            f"com score >= {min_score}"
        )

        return top_snippets, top_scores


# Singleton global (carregado uma vez, reutilizado)
_reranker_instance = None

def get_reranker() -> SnippetReranker:
    """
    Retorna instância singleton do reranker.
    Evita recarregar modelo a cada chamada.
    """
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = SnippetReranker()
    return _reranker_instance
```

### 3. Modificar `inference_service.py`

**Arquivo**: `backend/services/inference_service.py`

```python
# Adicionar no início do arquivo (após imports existentes)
from .reranker import get_reranker
import logging

# ... código existente ...

def search_chapters_for_snippets(keywords: list[str], query: str = None) -> str:
    """
    Busca por palavras-chave em todos os capítulos e extrai os parágrafos
    inteiros que as contêm.

    MUDANÇA: Agora aceita 'query' opcional para reranking.
    """
    all_snippets = set()
    chapter_files = list_available_files(CHAPTERS_DIR, '_extracted.txt')

    for filename in chapter_files:
        try:
            with open(os.path.join(CHAPTERS_DIR, filename), 'r', encoding='utf-8') as f:
                paragraphs = f.read().split('\n\n')

            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue

                for keyword in keywords:
                    if keyword.lower() in paragraph.lower():
                        snippet = (f"--- Snippet from {filename} ---\n" + paragraph.strip() + "\n")
                        all_snippets.add(snippet)
                        break
        except Exception as e:
            logging.warning(f"Could not process file {filename}: {e}")

    if not all_snippets:
        return "No relevant information found for the given keywords."

    # ============================================================================
    # 🆕 RERANKING: Ordena snippets por relevância
    # ============================================================================
    snippet_list = list(all_snippets)

    if query and len(snippet_list) > 5:
        logging.info(f"🔄 Aplicando reranking em {len(snippet_list)} snippets")

        try:
            reranker = get_reranker()
            top_snippets, scores = reranker.rerank(
                query=query,
                snippets=snippet_list,
                top_k=5  # ⚡ Reduz de ~30 para 5 snippets
            )

            logging.info(
                f"✅ Reranking completo. "
                f"Reduzido de {len(snippet_list)} para {len(top_snippets)} snippets. "
                f"Top score: {scores[0]:.3f}"
            )

            return "\n".join(top_snippets)

        except Exception as e:
            logging.error(f"❌ Erro no reranking: {e}. Usando snippets originais.")
            # Fallback: se reranking falhar, usar amostragem aleatória
            if len(snippet_list) > 10:
                import random
                snippet_list = random.sample(snippet_list, 10)

    return "\n".join(snippet_list)


async def run_full_inference_process(query: str) -> dict:
    """
    Orquestra todo o processo de inferência neurológica.

    MUDANÇA: Passa 'query' para search_chapters_for_snippets() para reranking.
    """
    # 1. Extrai keywords
    keywords = await extract_keywords(query)

    # 2. Busca snippets relevantes (AGORA COM RERANKING)
    context_snippets = search_chapters_for_snippets(
        keywords,
        query=query  # 🆕 Passa query para reranking
    )

    # Verifica se encontrou contexto suficiente
    snippet_count = context_snippets.count("--- Snippet from")

    if snippet_count < 3:
        logging.warning(
            f"⚠️ Poucos snippets encontrados ({snippet_count}). "
            f"Usando contexto completo como fallback."
        )
        full_chapters = load_all_chapters_content()
        image_list = list_available_files(IMAGES_DIR, '.png')

        result = await get_syndrome_inference_with_full_context(
            query, full_chapters, image_list
        )
    else:
        logging.info(f"✅ {snippet_count} snippets encontrados após reranking")
        image_list = list_available_files(IMAGES_DIR, '.png')
        result = await get_syndrome_inference(query, context_snippets, image_list)

    return result
```

### 4. Atualizar `requirements.txt`

```bash
# Adicionar ao arquivo backend/requirements.txt
sentence-transformers>=2.2.0
torch>=2.0.0
```

---

## 🧪 Testes Locais

### Teste 1: Verificar Instalação

```python
# test_reranker_installation.py
from backend.services.reranker import get_reranker

def test_installation():
    print("🔄 Testando instalação do reranker...")

    reranker = get_reranker()

    query = "Paciente com hemiparesia esquerda"
    snippets = [
        "Hemiparesia direita é comum em AVC",
        "Lesão no hemisfério esquerdo causa hemiparesia direita",
        "Afasia de Broca ocorre em lesões frontais",
        "Hemiparesia esquerda indica lesão à direita"
    ]

    top_snippets, scores = reranker.rerank(query, snippets, top_k=2)

    print(f"✅ Top 2 snippets mais relevantes:")
    for i, (snippet, score) in enumerate(zip(top_snippets, scores), 1):
        print(f"{i}. Score: {score:.3f} - {snippet[:50]}...")

    assert len(top_snippets) == 2
    assert scores[0] > scores[1]
    print("\n✅ Teste passou!")

if __name__ == "__main__":
    test_installation()
```

```bash
# Executar teste
cd /root/louis-final
python test_reranker_installation.py
```

**Saída esperada**:
```
🔄 Testando instalação do reranker...
🔄 Inicializando reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
✅ Reranker carregado: cross-encoder/ms-marco-MiniLM-L-6-v2
🔄 Rerankando 4 snippets, retornando top-2
✅ Reranking completo. Top score: 0.856, Bottom score: 0.423
✅ Top 2 snippets mais relevantes:
1. Score: 0.856 - Hemiparesia esquerda indica lesão à direita...
2. Score: 0.612 - Lesão no hemisfério esquerdo causa hemiparesia d...

✅ Teste passou!
```

### Teste 2: Benchmark de Performance

```python
# test_reranker_performance.py
import time
from backend.services.reranker import get_reranker

def benchmark_performance():
    print("⏱️ Benchmarking performance do reranker...")

    reranker = get_reranker()

    query = "Paciente de 65 anos com início súbito de hemiparesia esquerda, afasia de expressão e negligência espacial"

    # Simular 30 snippets (cenário real do Louis)
    snippets = [f"Snippet {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 5 for i in range(30)]

    # Testar com diferentes valores de top_k
    for top_k in [3, 5, 10]:
        start = time.time()
        top_snippets, scores = reranker.rerank(query, snippets, top_k=top_k)
        elapsed = time.time() - start

        print(f"\n📊 top_k={top_k}:")
        print(f"  ⏱️ Tempo: {elapsed:.3f}s")
        print(f"  📉 Redução: {len(snippets)} → {len(top_snippets)} snippets ({len(top_snippets)/len(snippets)*100:.1f}%)")
        print(f"  🎯 Score range: {scores[0]:.3f} - {scores[-1]:.3f}")

if __name__ == "__main__":
    benchmark_performance()
```

**Saída esperada**:
```
⏱️ Benchmarking performance do reranker...

📊 top_k=3:
  ⏱️ Tempo: 0.487s
  📉 Redução: 30 → 3 snippets (10.0%)
  🎯 Score range: 0.923 - 0.745

📊 top_k=5:
  ⏱️ Tempo: 0.492s
  📉 Redução: 30 → 5 snippets (16.7%)
  🎯 Score range: 0.923 - 0.612

📊 top_k=10:
  ⏱️ Tempo: 0.501s
  📉 Redução: 30 → 10 snippets (33.3%)
  🎯 Score range: 0.923 - 0.387
```

### Teste 3: Comparação Antes/Depois

```python
# test_inference_comparison.py
import asyncio
import time
from backend.services.inference_service import run_full_inference_process

async def compare_inference_times():
    """
    Compara tempo de inferência com e sem reranking.
    NOTA: Executar este teste requer banco populado e API key do Gemini.
    """
    queries = [
        "Paciente com hemiparesia esquerda",
        "Início súbito de afasia e paralisia facial",
        "Paciente de 70 anos com hemiparesia direita, afasia de expressão, desvio de olhar e negligência espacial esquerda"
    ]

    print("⏱️ Comparando tempo de inferência (COM reranking):\n")

    for query in queries:
        print(f"📝 Query: {query[:60]}...")

        start = time.time()
        result = await run_full_inference_process(query)
        elapsed = time.time() - start

        print(f"  ⏱️ Tempo: {elapsed:.2f}s")
        print(f"  🎯 Síndromes encontradas: {len(result.get('ischemic_syndromes', []))} isquêmicas, {len(result.get('hemorrhagic_syndromes', []))} hemorrágicas")
        print()

if __name__ == "__main__":
    asyncio.run(compare_inference_times())
```

---

## 🚀 Deploy para Produção

### 1. Backup Antes do Deploy

```bash
cd /root/louis-final
./backup_completo.sh "antes-adicionar-reranking"
```

### 2. Commitar Mudanças

```bash
git add backend/services/reranker.py
git add backend/services/inference_service.py
git add backend/requirements.txt
git add docs/RAG_RERANKING_GUIDE.md

git commit -m "feat(rag): Adiciona reranking de snippets com cross-encoder

- Cria módulo backend/services/reranker.py
- Usa cross-encoder/ms-marco-MiniLM-L-6-v2 (CPU-friendly)
- Reduz snippets enviados de ~30 para top-5 (83% redução)
- Mantém qualidade através de reranking por relevância semântica
- Adiciona testes de instalação e performance

Impacto esperado: Redução de latência de ~22s para ~10-12s (45%)

Refs: docs/RAG_RERANKING_GUIDE.md, Checkpoint de otimização RAG"
```

### 3. Deploy

```bash
# Parar apenas o backend
docker-compose stop backend
docker-compose rm -f backend

# Rebuild com novas dependências
docker-compose build backend

# Subir backend
docker-compose up -d backend

# Aguardar 10s
sleep 10

# Verificar logs
docker logs louis-backend-prod --tail=30
```

**Saída esperada nos logs**:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
🔄 Inicializando reranker: cross-encoder/ms-marco-MiniLM-L-6-v2
✅ Reranker carregado: cross-encoder/ms-marco-MiniLM-L-6-v2
✅ Gemini client initialized with SDK novo (thinking disabled for optimal latency)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Testar em Produção

```bash
# Teste via curl
curl -X POST https://app-louis.tpfbrain.com/infer \
  -H "Content-Type: application/json" \
  -d '{"query":"Paciente com hemiparesia esquerda e afasia"}' \
  | python -m json.tool
```

### 5. Monitorar Performance

```bash
# Ver logs em tempo real
docker logs -f louis-backend-prod | grep -E "Reranking|Tempo|score"
```

Procurar por linhas como:
```
🔄 Aplicando reranking em 28 snippets
✅ Reranking completo. Reduzido de 28 para 5 snippets. Top score: 0.867
✅ 5 snippets encontrados após reranking
```

---

## 📊 Métricas Esperadas

### Antes do Reranking
```
Query simples:   ~17.5s  (10-15 snippets)
Query complexa:  ~22.5s  (25-35 snippets)
Contexto médio:  ~250-300KB
```

### Depois do Reranking (Estimativa)
```
Query simples:   ~9-10s  (3-5 snippets) ✅ 43% melhoria
Query complexa:  ~10-12s (5 snippets)   ✅ 47% melhoria
Contexto médio:  ~40-60KB              ✅ 80% redução
```

### Breakdown Estimado
```
Antes:
extract_keywords():       ~0.5s
search_chapters():        ~1.0s
[sem reranking]           ~0.0s
get_syndrome_inference(): ~21.0s  (contexto grande)
TOTAL:                    ~22.5s

Depois:
extract_keywords():       ~0.5s
search_chapters():        ~1.0s
reranking:                ~0.5s  🆕
get_syndrome_inference(): ~9.0s  ⚡ (contexto reduzido)
TOTAL:                    ~11.0s  ✅ 51% melhoria
```

---

## 🔬 Opções Avançadas (Futuro)

### Opção 2: Reranker via API (Cohere)

**Vantagens**:
- Não requer GPU/CPU local
- Qualidade superior
- Latência consistente (~1-2s)

**Custo**: ~$2 por 1000 reranks

```python
# backend/services/reranker.py - Versão Cohere
from cohere import Client

class CohereReranker:
    def __init__(self, api_key: str):
        self.client = Client(api_key)

    def rerank(self, query: str, snippets: List[str], top_k: int = 5):
        results = self.client.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=snippets,
            top_n=top_k
        )

        top_snippets = [snippets[r.index] for r in results.results]
        scores = [r.relevance_score for r in results.results]

        return top_snippets, scores
```

### Opção 3: RankGPT (GPT-4o Mini)

**Vantagens**:
- Máxima qualidade de reranking
- Entende nuances clínicas
- Usa API OpenAI existente

**Custo**: ~$0.15 por 1000 tokens (~$0.02/query)

```python
# backend/services/reranker.py - Versão GPT
from langchain_community.document_compressors.rankllm_rerank import RankLLMRerank

class GPTReranker:
    def __init__(self, openai_api_key: str):
        self.compressor = RankLLMRerank(
            top_n=5,
            model="gpt",
            gpt_model="gpt-4o-mini"
        )

    def rerank(self, query: str, snippets: List[str], top_k: int = 5):
        # Converte snippets para formato Document
        from langchain_core.documents import Document
        docs = [Document(page_content=s) for s in snippets]

        # Rerank
        reranked_docs = self.compressor.compress_documents(docs, query)

        top_snippets = [d.page_content for d in reranked_docs[:top_k]]
        # GPT não retorna scores numéricos, usar posição como proxy
        scores = [1.0 - (i * 0.1) for i in range(len(top_snippets))]

        return top_snippets, scores
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solução**:
```bash
docker exec louis-backend-prod pip install sentence-transformers
docker-compose restart backend
```

### Erro: "RuntimeError: CUDA out of memory"

**Causa**: Modelo tentando usar GPU inexistente.

**Solução**: Forçar uso de CPU

```python
# backend/services/reranker.py - linha 20
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Desabilita GPU

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
```

### Aviso: "Reranking muito lento (>2s)"

**Causa**: CPU sobrecarregado ou modelo muito grande.

**Soluções**:
1. Usar modelo menor: `cross-encoder/ms-marco-TinyBERT-L-2-v2` (mais rápido, menor qualidade)
2. Reduzir `top_k` de 5 para 3
3. Aumentar threshold de snippets para acionar reranking (apenas se >10 snippets)

```python
# Otimização: só fazer rerank se muitos snippets
if query and len(snippet_list) > 10:  # Aumenta de 5 para 10
    reranker = get_reranker()
    top_snippets, scores = reranker.rerank(query, snippet_list, top_k=3)  # Reduz de 5 para 3
```

---

## ✅ Checklist de Implementação

- [ ] 1. Criar `backend/services/reranker.py`
- [ ] 2. Modificar `backend/services/inference_service.py`
  - [ ] 2.1. Import do reranker
  - [ ] 2.2. Adicionar parâmetro `query` em `search_chapters_for_snippets()`
  - [ ] 2.3. Aplicar reranking antes de retornar snippets
  - [ ] 2.4. Passar `query` em `run_full_inference_process()`
- [ ] 3. Atualizar `backend/requirements.txt`
- [ ] 4. Testar localmente
  - [ ] 4.1. `test_reranker_installation.py`
  - [ ] 4.2. `test_reranker_performance.py`
  - [ ] 4.3. `test_inference_comparison.py`
- [ ] 5. Backup pré-deploy (`./backup_completo.sh`)
- [ ] 6. Commitar mudanças
- [ ] 7. Deploy (`docker-compose build backend && docker-compose up -d backend`)
- [ ] 8. Verificar logs (procurar por "Reranking")
- [ ] 9. Testar em produção (curl ou interface web)
- [ ] 10. Monitorar performance (latência deve cair ~50%)
- [ ] 11. Atualizar CHECKPOINT.md com resultados

---

## 📚 Referências

1. **Cross-Encoder para Reranking**: https://www.sbert.net/examples/applications/cross-encoder/README.html
2. **MS MARCO Dataset**: https://microsoft.github.io/msmarco/
3. **LangChain Reranking**: https://python.langchain.com/docs/how_to/contextual_compression/
4. **RAG Optimization Techniques**: https://towardsdatascience.com/10-ways-to-improve-rag-systems
5. **Sentence Transformers**: https://www.sbert.net/

---

**Criado em**: 05/Out/2025
**Última atualização**: 05/Out/2025
**Status**: Pronto para implementação local
**Próximo passo**: Executar testes locais e deploy incremental
