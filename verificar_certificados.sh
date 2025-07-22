#!/bin/bash

# Script para verificar status dos certificados SSL

echo "🔍 Verificando status dos certificados SSL..."
echo ""

# Função para verificar certificado de um domínio
verificar_dominio() {
    local dominio=$1
    echo "🌐 Verificando: $dominio"
    
    # Verifica se o domínio responde
    if curl -I -s --connect-timeout 10 https://$dominio > /dev/null; then
        # Obtém informações do certificado
        cert_info=$(echo | openssl s_client -servername $dominio -connect $dominio:443 2>/dev/null | openssl x509 -noout -dates -issuer 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            echo "✅ Certificado ativo"
            echo "$cert_info" | grep "notBefore"
            echo "$cert_info" | grep "notAfter"
            echo "$cert_info" | grep "issuer"
            
            # Verifica se é certificado de staging
            if echo "$cert_info" | grep -q "Fake LE"; then
                echo "⚠️ CERTIFICADO DE STAGING (desenvolvimento)"
            else
                echo "🎉 CERTIFICADO DE PRODUÇÃO (válido)"
            fi
        else
            echo "❌ Erro ao obter informações do certificado"
        fi
    else
        echo "❌ Domínio não acessível"
    fi
    echo ""
}

# Verifica ambos os domínios
verificar_dominio "louis.tpfbrain.com"
verificar_dominio "app-louis.tpfbrain.com"

# Verifica o status dos containers
echo "🐳 Status dos containers:"
docker-compose ps

echo ""
echo "📊 Espaço usado pelos volumes:"
docker system df -v | grep letsencrypt 