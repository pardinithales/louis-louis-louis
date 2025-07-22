#!/bin/bash

# Script para backup dos certificados SSL
# Recomenda-se executar semanalmente

echo "💾 Iniciando backup dos certificados SSL..."

# Cria diretório de backup se não existir
mkdir -p /root/backups/certificados

# Nome do arquivo com timestamp
BACKUP_FILE="/root/backups/certificados/certificados_$(date +%Y%m%d_%H%M%S).tar.gz"

# Verifica se o volume de certificados existe
if docker volume ls | grep -q "louis-final_letsencrypt_data"; then
    echo "📦 Criando backup dos certificados..."
    
    # Cria o backup
    docker run --rm \
        -v louis-final_letsencrypt_data:/source:ro \
        -v /root/backups/certificados:/backup \
        alpine tar czf /backup/certificados_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
    
    if [ $? -eq 0 ]; then
        echo "✅ Backup criado com sucesso: $BACKUP_FILE"
        echo "📊 Tamanho do backup: $(du -h $BACKUP_FILE | cut -f1)"
    else
        echo "❌ Erro ao criar backup"
        exit 1
    fi
else
    echo "⚠️ Volume de certificados não encontrado"
    exit 1
fi

# Lista backups existentes
echo ""
echo "📋 Backups existentes:"
ls -lh /root/backups/certificados/

# Remove backups antigos (mantém apenas os 5 mais recentes)
echo ""
echo "🧹 Limpando backups antigos (mantendo os 5 mais recentes)..."
cd /root/backups/certificados/
ls -t certificados_*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null || true

echo ""
echo "🎉 Backup concluído!"
echo "💡 Para restaurar um backup, use:"
echo "   docker run --rm -v louis-final_letsencrypt_data:/target -v /root/backups/certificados:/backup alpine tar xzf /backup/NOME_DO_BACKUP.tar.gz -C /target" 