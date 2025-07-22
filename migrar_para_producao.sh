#!/bin/bash

# Script para migrar do Let's Encrypt Staging para Produção
# ⚠️ USAR APENAS QUANDO TIVER CERTEZA QUE TUDO ESTÁ FUNCIONANDO

echo "⚠️ ATENÇÃO: Este script migra para certificados de PRODUÇÃO do Let's Encrypt"
echo "📊 Limites de produção: 50 certificados/semana por domínio"
echo ""
read -p "Tem certeza que deseja continuar? (sim/nao): " confirmacao

if [ "$confirmacao" != "sim" ]; then
    echo "❌ Operação cancelada."
    exit 1
fi

echo "🔄 Iniciando migração para produção..."

# 1. Para os serviços
echo "⏹️ Parando serviços..."
docker-compose down

# 2. Remove certificados de staging (IMPORTANTE!)
echo "🗑️ Removendo certificados de staging..."
docker volume rm louis-final_letsencrypt_data 2>/dev/null || true

# 3. Edita o docker-compose.yml para usar servidor de produção
echo "✏️ Configurando para servidor de produção..."
sed -i 's|acme-staging-v02|acme-v02|g' docker-compose.yml

# 4. Verifica se a mudança foi feita
echo "✅ Verificando configuração..."
if grep -q "acme-v02.api.letsencrypt.org" docker-compose.yml; then
    echo "✅ Configuração de produção aplicada com sucesso!"
else
    echo "❌ Erro na configuração. Revertendo..."
    sed -i 's|acme-v02|acme-staging-v02|g' docker-compose.yml
    exit 1
fi

# 5. Sobe os serviços com certificados de produção
echo "🚀 Iniciando serviços com certificados de produção..."
docker-compose up -d --build

echo ""
echo "🎉 Migração concluída!"
echo "📋 Próximos passos:"
echo "   - Aguarde alguns minutos para os certificados serem gerados"
echo "   - Teste os domínios: https://louis.tpfbrain.com e https://app-louis.tpfbrain.com"
echo "   - Use o script deploy_otimizado.sh para futuros deploys" 