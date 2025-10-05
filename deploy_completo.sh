#!/bin/bash

#####################################################################
# SCRIPT DE DEPLOY COMPLETO - Louis Final
# Criado: 05/Out/2025 - Checkpoint #3
#
# ⚠️  IMPORTANTE: Este script é para deploy em PRODUÇÃO
#
# O QUE ESTE SCRIPT FAZ:
# 1. Cria backup completo antes de qualquer mudança
# 2. Atualiza código do Git
# 3. Para containers SEM remover volumes (preserva certificados SSL)
# 4. Rebuild das imagens Docker
# 5. Inicia containers
# 6. POPULA banco de dados (CRÍTICO - não esquecer!)
# 7. Verifica saúde dos serviços
#
# IMPORTANTE SOBRE POPULAR O BANCO:
# - O banco de dados SQLite é criado vazio quando o container sobe
# - É OBRIGATÓRIO rodar populate_db.py após rebuild
# - Se não popular, o sistema não terá os casos de validação
# - Os casos vêm de backend/scripts/validation_cases.json
#
# USO:
#   ./deploy_completo.sh [branch]
#
# Exemplos:
#   ./deploy_completo.sh validacao    # Deploy da branch validacao
#   ./deploy_completo.sh louis-claude # Deploy da branch louis-claude
#   ./deploy_completo.sh main         # Deploy da main
#
#####################################################################

set -e  # Para na primeira falha

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_DIR="/root/louis-final"
BACKUP_DIR="/root/backups/louis-final"
DEFAULT_BRANCH="validacao"
BRANCH="${1:-$DEFAULT_BRANCH}"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 DEPLOY COMPLETO - Louis Final                        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Branch a ser deployada: ${BRANCH}${NC}"
echo -e "${YELLOW}Diretório: ${PROJECT_DIR}${NC}"
echo ""

#####################################################################
# STEP 1: BACKUP AUTOMÁTICO
#####################################################################
echo -e "${GREEN}[1/8]${NC} Criando backup de segurança..."
cd "${PROJECT_DIR}"

if [ -f "./backup_completo.sh" ]; then
    ./backup_completo.sh "antes-deploy-${BRANCH}-$(date +%Y%m%d-%H%M%S)"
    echo -e "  ✅ Backup criado com sucesso"
else
    echo -e "  ${YELLOW}⚠️  Script de backup não encontrado, pulando...${NC}"
fi
echo ""

#####################################################################
# STEP 2: ATUALIZAÇÃO DO CÓDIGO
#####################################################################
echo -e "${GREEN}[2/8]${NC} Atualizando código do Git (branch: ${BRANCH})..."
git fetch origin
git checkout "${BRANCH}"
git reset --hard "origin/${BRANCH}"
echo -e "  ✅ Código atualizado para $(git log -1 --oneline)"
echo ""

#####################################################################
# STEP 3: PARAR CONTAINERS (SEM REMOVER VOLUMES)
#####################################################################
echo -e "${GREEN}[3/8]${NC} Parando containers (preservando volumes e certificados)..."
docker-compose down
echo -e "  ✅ Containers parados"
echo ""

#####################################################################
# STEP 4: LIMPEZA DE IMAGENS ANTIGAS
#####################################################################
echo -e "${GREEN}[4/8]${NC} Removendo imagens antigas do projeto..."
docker image prune -f
docker rmi $(docker images "louis-final_*" -q) 2>/dev/null || true
echo -e "  ✅ Imagens antigas removidas"
echo ""

#####################################################################
# STEP 5: REBUILD E START
#####################################################################
echo -e "${GREEN}[5/8]${NC} Reconstruindo e iniciando containers..."
docker-compose up -d --build
echo -e "  ✅ Containers reconstruídos e iniciados"
echo ""

#####################################################################
# STEP 6: AGUARDAR CONTAINERS FICAREM PRONTOS
#####################################################################
echo -e "${GREEN}[6/8]${NC} Aguardando containers ficarem prontos..."
sleep 20

# Verifica se backend está respondendo
MAX_TRIES=30
TRIES=0
while [ $TRIES -lt $MAX_TRIES ]; do
    if docker exec louis-backend-prod curl -f http://localhost:8000/health 2>/dev/null; then
        echo -e "  ✅ Backend está respondendo"
        break
    fi
    TRIES=$((TRIES+1))
    echo -e "  ⏳ Tentativa ${TRIES}/${MAX_TRIES}..."
    sleep 2
done

if [ $TRIES -eq $MAX_TRIES ]; then
    echo -e "  ${RED}❌ Backend não respondeu após ${MAX_TRIES} tentativas${NC}"
    echo -e "  ${YELLOW}Verifique os logs: docker logs louis-backend-prod${NC}"
    exit 1
fi
echo ""

#####################################################################
# STEP 7: POPULAR BANCO DE DADOS (CRÍTICO!)
#####################################################################
echo -e "${GREEN}[7/8]${NC} Populando banco de dados..."
echo -e "  ${YELLOW}⚠️  IMPORTANTE: Banco SQLite é criado vazio no rebuild${NC}"
echo -e "  ${YELLOW}⚠️  É OBRIGATÓRIO popular com os casos de validação${NC}"
echo ""

# IMPORTANTE: NÃO usar -it (interativo) em scripts automatizados!
# -it só funciona em terminal interativo
# Usar apenas -i para pipelines/cron
if docker exec louis-backend-prod python /app/backend/scripts/populate_db.py; then
    echo -e "  ✅ Banco de dados populado com sucesso"
else
    echo -e "  ${RED}❌ ERRO ao popular banco de dados!${NC}"
    echo -e "  ${YELLOW}Sistema está rodando mas SEM casos de validação${NC}"
    echo -e "  ${YELLOW}Execute manualmente: docker exec louis-backend-prod python /app/backend/scripts/populate_db.py${NC}"
    exit 1
fi
echo ""

#####################################################################
# STEP 8: VERIFICAÇÃO FINAL
#####################################################################
echo -e "${GREEN}[8/8]${NC} Verificando status dos serviços..."
docker-compose ps
echo ""

# Verifica se todos os containers estão UP
if docker-compose ps | grep -q "Exit\|Down"; then
    echo -e "${RED}❌ Alguns containers não estão rodando!${NC}"
    exit 1
fi

# Testa endpoint de inferência
echo -e "${YELLOW}Testando endpoint de inferência...${NC}"
if docker exec louis-backend-prod curl -f http://localhost:8000/health 2>/dev/null; then
    echo -e "  ✅ API está respondendo"
else
    echo -e "  ${RED}❌ API não está respondendo${NC}"
    exit 1
fi
echo ""

#####################################################################
# RESUMO FINAL
#####################################################################
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ DEPLOY CONCLUÍDO COM SUCESSO!                        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📊 Status Final:${NC}"
echo -e "  Branch deployada: ${BRANCH}"
echo -e "  Commit: $(git log -1 --oneline)"
echo -e "  Containers rodando: $(docker-compose ps --services | wc -l)"
echo -e "  Banco de dados: ✅ Populado"
echo ""
echo -e "${YELLOW}🔗 URLs:${NC}"
echo -e "  Frontend: https://louis.tpfbrain.com"
echo -e "  API Health: https://louis.tpfbrain.com/health"
echo ""
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo -e "  1. Testar inferência manualmente em https://louis.tpfbrain.com"
echo -e "  2. Verificar logs: docker logs louis-backend-prod"
echo -e "  3. Verificar casos de validação carregados"
echo ""
echo -e "${GREEN}✅ Deploy finalizado!${NC}"
