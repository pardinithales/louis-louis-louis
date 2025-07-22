#!/bin/bash

# Script de deploy otimizado para LOUIS
# Este script preserva os certificados SSL e otimiza o processo de deploy

echo "🚀 Iniciando deploy otimizado do LOUIS..."

# 1. Fetch das últimas mudanças
echo "📥 Baixando últimas mudanças..."
git fetch origin
git reset --hard origin/validacao

# 2. Navegue para o diretório do projeto
cd /root/louis-final

# 3. Para os serviços SEM remover volumes (preserva certificados)
echo "⏹️ Parando serviços..."
docker-compose down

# 4. Remove apenas as imagens do projeto (não afeta certificados)
echo "🗑️ Limpando imagens antigas..."
docker image prune -f
docker rmi $(docker images "louis-final_*" -q) 2>/dev/null || true

# 5. Rebuild e restart (certificados são reutilizados)
echo "🔨 Reconstruindo e iniciando serviços..."
docker-compose up -d --build

# 6. Aguarda os serviços subirem
echo "⏳ Aguardando serviços iniciarem..."
sleep 15

# 7. Popula o banco de dados
echo "💾 Populando banco de dados..."
docker exec -it louis-backend-prod python /app/backend/scripts/populate_db.py

# 8. Verifica se os serviços estão rodando
echo "✅ Verificando status dos serviços..."
docker-compose ps

echo "🎉 Deploy concluído com sucesso!" 