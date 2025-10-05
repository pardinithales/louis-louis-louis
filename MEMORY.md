# MEMORY.md - Preferências e Convenções do Projeto

**Propósito**: Registrar padrões de código, convenções e preferências específicas deste projeto para manter consistência entre sessões.

---

## 🎯 Filosofia de Desenvolvimento

### Abordagem Geral
- **VPS Production-Only**: Não há ambiente local de teste. Todo teste é feito em produção.
- **Backup Before Changes**: SEMPRE criar backup antes de mudanças críticas.
- **Incremental Testing**: Testar cada mudança isoladamente antes de prosseguir.
- **Documentation-First**: Documentar descobertas e decisões imediatamente.

### Prioridades
1. **Preservar dados** (database.db é SAGRADO)
2. **Não afetar app-cefaleia** (container separado na mesma VPS)
3. **Manter uptime** (sistema em produção com usuários reais)
4. **Documentar tudo** (para próximas sessões)

---

## 🔧 Preferências de Comandos

### Deploy e Restart

**✅ PREFERIDO**:
```bash
# Deploy completo (usa script recomendado)
./deploy_completo.sh                    # Usa branch validacao (padrão)
./deploy_completo.sh louis-claude       # Especifica branch

# Restart rápido (sem rebuild)
docker-compose restart backend
docker-compose restart frontend
```

**❌ EVITAR**:
```bash
docker-compose down --volumes           # APAGA CERTIFICADOS
docker-compose down -v                  # Apaga volumes
docker stop $(docker ps -q)             # Para TODOS containers (inclui app-cefaleia!)
```

### Backup

**✅ PREFERIDO**:
```bash
# Backup completo (automático com cleanup)
./backup_completo.sh "descrição-da-mudança"

# Backup rápido do database
cp database.db database.db.backup-$(date +%Y%m%d-%H%M%S)
```

**❌ EVITAR**:
```bash
# Backups manuais sem timestamp
cp database.db database.db.backup       # Sem data, dificulta rastreamento
```

### Verificação de Status

**✅ PREFERIDO**:
```bash
# Ver status de containers (formato tabela)
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs com limite (não sobrecarrega terminal)
docker logs louis-backend-prod --tail=50

# Logs em tempo real (quando necessário monitorar)
docker logs -f louis-backend-prod
```

**❌ EVITAR**:
```bash
# Logs sem limite (pode travar terminal com milhares de linhas)
docker logs louis-backend-prod
```

### Git Workflow

**✅ PREFERIDO**:
```bash
# Desenvolvimento em louis-claude
git checkout louis-claude
git add [arquivos-específicos]          # Nunca git add .
git commit -m "tipo(escopo): mensagem"  # Conventional Commits

# Verificar antes de commitar
git status
git diff
```

**❌ EVITAR**:
```bash
git add .                               # Pode adicionar arquivos indesejados
git commit -m "updates"                 # Mensagem não descritiva
git push --force                        # Nunca forçar push
```

---

## 📝 Convenções de Código

### Python (Backend)

**Imports**:
```python
# ✅ Ordem preferida
# 1. Standard library
import os
import json
from typing import List, Dict

# 2. Third-party
from fastapi import FastAPI
from google import genai

# 3. Local
from backend.database.models import ValidationCase
from backend.services.inference_service import run_inference
```

**Configuração de API**:
```python
# ✅ PREFERIDO - SDK novo (atual)
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    temperature=0.2
)

# ❌ LEGADO - Não usar mais
import google.generativeai as genai
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
```

**Async/Await**:
```python
# ✅ PREFERIDO - Funções async quando possível
async def get_validation_cases(user_id: str):
    # Código...
    return cases

# ⚠️ NOTA: SDK novo do Gemini é SÍNCRONO (não tem async)
# Funções async podem chamar código síncrono normalmente
response = client.models.generate_content(...)  # Não é async
```

### JavaScript (Frontend)

**Fetch API**:
```javascript
// ✅ PREFERIDO - async/await com try/catch
async function sendInferenceRequest() {
    try {
        const response = await fetch('/infer/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: text})
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Inference error:', error);
        showErrorMessage(error.message);
    }
}

// ❌ EVITAR - Promises encadeadas
fetch('/infer/')
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.log(err));
```

---

## 🏗️ Padrões de Arquitetura

### Estrutura de Endpoints (FastAPI)

**✅ PREFERIDO**:
```python
@app.get("/validation_cases/")
async def get_validation_cases(
    user_identifier: str,
    db: Session = Depends(get_db)
):
    """
    Retorna casos de validação randomizados para o usuário.

    Args:
        user_identifier: ID único do usuário (UUID ou timestamp)
        db: Sessão do banco de dados (injetada)

    Returns:
        List[ValidationCase]: Lista de 20 casos aleatórios
    """
    cases = get_random_cases_for_user(user_identifier, db)
    return cases
```

**Características**:
- Barra final na rota (`/validation_cases/`)
- Async quando possível
- Docstring descritiva
- Type hints completos
- Dependency injection para DB

### Tratamento de Erros

**✅ PREFERIDO**:
```python
from fastapi import HTTPException

@app.post("/infer/")
async def infer_syndromes(request: InferenceRequest):
    try:
        result = await run_full_inference_process(request.query)
        return result
    except ValueError as e:
        # Erro de validação/entrada
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erro interno
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Internal inference error")
```

---

## 🗄️ Banco de Dados

### SQLAlchemy Patterns

**✅ PREFERIDO - Session management**:
```python
from backend.database.database import SessionLocal

def get_validation_data():
    db = SessionLocal()
    try:
        results = db.query(ValidationResponse).all()
        return results
    finally:
        db.close()  # SEMPRE fechar sessão
```

**✅ PREFERIDO - Dependency injection (FastAPI)**:
```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/cases/")
async def get_cases(db: Session = Depends(get_db)):
    return db.query(ValidationCase).all()
```

### Queries

**✅ PREFERIDO**:
```python
# Query com filtros
cases = db.query(ValidationCase)\
    .filter(ValidationCase.case_order > 0)\
    .order_by(ValidationCase.case_order)\
    .all()

# Verificar existência antes de criar
existing = db.query(Chapter).filter(Chapter.title == title).first()
if not existing:
    new_chapter = Chapter(title=title, content=content)
    db.add(new_chapter)
    db.commit()
```

---

## 📦 Docker Patterns

### Verificações Pré-Deploy

**✅ SEMPRE fazer antes de deploy**:
```bash
# 1. Backup
./backup_completo.sh "antes-[descrição]"

# 2. Verificar branch
git branch
git status

# 3. Verificar containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# 4. Confirmar localização
pwd  # Deve ser /root/louis-final
```

### Pós-Deploy

**✅ SEMPRE fazer após deploy**:
```bash
# 1. Popular banco (CRÍTICO!)
docker exec louis-backend-prod python /app/backend/scripts/populate_db.py

# 2. Verificar logs
docker logs louis-backend-prod --tail=50 | grep -i error

# 3. Testar URLs
curl -I https://louis.tpfbrain.com
curl -I https://app-louis.tpfbrain.com/docs

# 4. Verificar app-cefaleia NÃO foi afetado
docker ps | grep app-cefaleia
# Uptime NÃO deve ter resetado
```

---

## 📊 Logging e Debug

### Backend (Python)

**✅ PREFERIDO**:
```python
import logging

logger = logging.getLogger(__name__)

# Níveis apropriados
logger.debug("Detailed diagnostic info")
logger.info("Normal operation milestone")
logger.warning("Something unexpected but handled")
logger.error("Error that needs attention")

# Com contexto
logger.error(f"Inference failed for user {user_id}: {error}", exc_info=True)
```

### Frontend (JavaScript)

**✅ PREFERIDO**:
```javascript
// Console logs estruturados
console.log('[Inference] Starting request:', {query, timestamp});
console.error('[Inference] Request failed:', {error, status, url});

// Evitar logs excessivos em produção
if (process.env.NODE_ENV === 'development') {
    console.debug('[Debug] Internal state:', state);
}
```

---

## 🎨 Estilo de Commit Messages

### Conventional Commits

**Formato**: `tipo(escopo): mensagem`

**Tipos**:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `refactor`: Refatoração (sem mudança de comportamento)
- `perf`: Melhoria de performance
- `test`: Adicionar/modificar testes
- `chore`: Manutenção (deps, config, etc)

**Exemplos**:
```bash
git commit -m "feat(inference): Adiciona suporte a caching de capítulos"
git commit -m "fix(api): Corrige erro 422 em /validation_cases/ sem user_identifier"
git commit -m "perf(inference): Reduz contexto enviado ao Gemini de 52 para 5 snippets"
git commit -m "docs(claude): Atualiza MEMORY.md com convenções de código"
git commit -m "chore(deps): Atualiza google-genai para v1.42.0"
```

**Commit multi-linha** (para mudanças grandes):
```bash
git commit -m "feat(inference): Migra para SDK novo do Gemini com thinking desabilitado

- Atualiza requirements.txt: google-generativeai → google-genai (v1.41.0)
- Migra inference_service.py para SDK novo com client.models.generate_content()
- Configura thinking_budget=0 para otimizar latência
- Remove uso de API async (não existe no SDK novo)

Performance:
- Query simples: ~17.5s (melhoria de ~10-15%)
- Query complexa: ~22.5s (sem melhoria significativa)
- Qualidade: Mantida (síndromes identificadas corretamente)

Refs: Checkpoint #3, backup-20251005-164512-antes-migracao-sdk-novo"
```

---

## 🚨 Checklist de Segurança

### Antes de Qualquer Mudança Crítica

- [ ] Backup criado (`./backup_completo.sh`)
- [ ] Branch correto (`git branch` = louis-claude)
- [ ] Working directory correto (`pwd` = /root/louis-final)
- [ ] Containers verificados (app-cefaleia ainda Up)
- [ ] Database.db existe e tem tamanho > 70 KB

### Após Mudanças

- [ ] Database.db preservado (tamanho não mudou para 0)
- [ ] Containers Louis reiniciaram corretamente
- [ ] app-cefaleia NÃO foi afetado (uptime mantido)
- [ ] URLs de produção acessíveis (200 OK)
- [ ] Logs sem erros críticos

### Antes de Commitar

- [ ] `git status` revisado (nenhum arquivo sensível)
- [ ] `git diff` revisado (mudanças intencionais apenas)
- [ ] Mensagem de commit descritiva (conventional commits)
- [ ] Não commitando .env ou arquivos de backup

---

## 🔐 Segredos e Credenciais

### Nunca Commitar

**Arquivos proibidos no Git**:
- `.env` (API keys)
- `database.db` (dados reais)
- `database.db.backup-*` (backups)
- `CLAUDE.md`, `MEMORY.md`, `CHECKPOINT.md` (docs privadas com credenciais)
- `*.pem`, `*.key` (chaves SSH/SSL)

**Verificar .gitignore**:
```bash
# SEMPRE antes de commitar
git status --ignored
```

### Credenciais em Código

**✅ PREFERIDO**:
```python
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment")
```

**❌ NUNCA**:
```python
GEMINI_API_KEY = "AIzaSyCo-..."  # Hardcoded!
```

---

## 📚 Documentação Contínua

### Quando Atualizar CHECKPOINT.md

**Sempre registrar**:
- Mudanças críticas (arquitetura, database, API)
- Deploys realizados
- Problemas encontrados e soluções
- Decisões de design importantes
- Testes de performance

**Formato**:
```markdown
## 📅 Checkpoint #X - [Título]
**Data**: DD/Mês/YYYY
**Horário**: HH:MM UTC (HH:MM BRT)
**Branch**: louis-claude
**Status**: ✅/⚠️/❌

### 🎯 Objetivo
[O que foi solicitado]

### ✅ Realizado
[O que foi feito]

### 📊 Resultados
[Métricas, testes, observações]

### 🚨 Lições Aprendidas
[O que aprendemos]
```

### Quando Atualizar MEMORY.md

**Registrar**:
- Novos padrões de código adotados
- Preferências de comandos descobertas
- Convenções estabelecidas
- Atalhos úteis criados

---

## 🎯 Objetivos de Performance

### Latência de Inferência

**Estado atual** (Checkpoint #3):
- Query simples: ~17.5s
- Query complexa: ~22.5s

**Alvo desejável**:
- Query simples: <10s
- Query complexa: <15s

**Próximas otimizações planejadas**:
1. Reduzir contexto (top-5 snippets em vez de todos)
2. Implementar caching de capítulos
3. Paralelizar search local
4. Considerar Grok 4 Fast (alternativa)

### Uptime

**Alvo**: 99.9% (máximo 43 minutos de downtime por mês)
**Estratégia**: Rolling updates, health checks, backups frequentes

---

## 🔄 Workflow de Desenvolvimento Típico

### 1. Início de Sessão
```bash
cd /root/louis-final
git checkout louis-claude
git status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 2. Fazer Mudanças
```bash
# Criar backup
./backup_completo.sh "antes-[descrição]"

# Editar arquivos
# ... modificar código ...

# Verificar mudanças
git diff
```

### 3. Deploy
```bash
./deploy_completo.sh louis-claude
# Ou se já estiver na branch:
./deploy_completo.sh
```

### 4. Verificação
```bash
# Popular banco
docker exec louis-backend-prod python /app/backend/scripts/populate_db.py

# Testar
curl -I https://louis.tpfbrain.com
curl -I https://app-louis.tpfbrain.com/docs

# Verificar logs
docker logs louis-backend-prod --tail=50
```

### 5. Commit
```bash
git add [arquivos]
git commit -m "tipo(escopo): mensagem"

# Atualizar CHECKPOINT.md se mudança crítica
# Atualizar MEMORY.md se nova convenção
```

---

## 🎓 Lições Aprendidas (Acumulado)

### Checkpoint #2 - Otimização Falhou
- ❌ Reutilizar modelos globais PIOROU performance (77s)
- ✅ Backup salvou o sistema de downtime
- 📚 SDK legado não permite controle de thinking

### Checkpoint #3 - Migração SDK Novo
- ❌ SDK novo não tem API async (generate_content_async não existe)
- ❌ Expectativa de 70% melhoria não se confirmou (apenas 10-15%)
- ✅ Thinking não é o gargalo real (latência de rede + contexto)
- 📚 Gargalo real: Volume de contexto enviado ao Gemini

### Padrões que Funcionaram
- ✅ Sempre criar backup antes de mudanças críticas
- ✅ Testar cada mudança isoladamente
- ✅ Migração incremental (não tudo de uma vez)
- ✅ Medir performance antes e depois

---

**Última atualização**: 05/Out/2025 17:15 BRT
**Próxima revisão**: Após próximo checkpoint com mudanças significativas

---

## 📌 Quick Reference

```bash
# Deploy
./deploy_completo.sh [branch]

# Backup
./backup_completo.sh "descrição"

# Status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Logs
docker logs louis-backend-prod --tail=50

# Popular DB
docker exec louis-backend-prod python /app/backend/scripts/populate_db.py

# Testar
curl -I https://louis.tpfbrain.com
curl -I https://app-louis.tpfbrain.com/docs
```
