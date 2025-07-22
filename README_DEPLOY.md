# 🚀 Guia de Deploy e Gestão de Certificados - LOUIS

## 📋 Situação Atual

Atualmente você está usando certificados **STAGING** do Let's Encrypt, que são ideais para desenvolvimento e testes.

## ❌ Problema com o Fluxo Anterior

O comando `docker-compose down --volumes --rmi all` estava:
- ❌ Removendo o volume dos certificados SSL
- ❌ Forçando nova requisição de certificado a cada deploy
- ❌ Potencialmente esgotando os limites do Let's Encrypt

## ✅ Solução: Scripts Otimizados

### 1. 📥 Deploy Otimizado (Uso Diário)

Use este script para todos os deploys rotineiros:

```bash
# Torne o script executável
chmod +x deploy_otimizado.sh

# Execute o deploy
./deploy_otimizado.sh
```

**O que faz:**
- ✅ Preserva certificados SSL existentes
- ✅ Rebuild apenas das aplicações
- ✅ Sem risco de esgotar limites do Let's Encrypt

### 2. 🔍 Verificar Certificados

```bash
# Torne o script executável
chmod +x verificar_certificados.sh

# Verifique o status dos certificados
./verificar_certificados.sh
```

**O que mostra:**
- Status dos certificados SSL
- Data de expiração
- Se é staging ou produção
- Status dos containers

### 3. 🎯 Migração para Produção

**⚠️ Use apenas quando tiver certeza que tudo funciona!**

```bash
# Torne o script executável
chmod +x migrar_para_producao.sh

# Execute a migração (CUIDADO!)
./migrar_para_producao.sh
```

## 📊 Limites do Let's Encrypt

### Staging (Atual)
- ✅ ~30.000 certificados por semana
- ✅ Ideal para desenvolvimento
- ⚠️ Certificados não são confiáveis pelos navegadores

### Produção
- ⚠️ 50 certificados por domínio por semana
- ⚠️ 5 certificados duplicados por semana
- ✅ Certificados confiáveis pelos navegadores

## 🔄 Fluxo Recomendado

### Para Desenvolvimento (Atual)
```bash
# 1. Faça mudanças no código
git add .
git commit -m "suas mudanças"
git push origin validacao

# 2. Na VPS, execute o deploy otimizado
./deploy_otimizado.sh
```

### Para Produção (Futuro)
```bash
# 1. Teste tudo no staging
./verificar_certificados.sh

# 2. Migre para produção (UMA VEZ APENAS)
./migrar_para_producao.sh

# 3. Para deploys futuros, use sempre
./deploy_otimizado.sh
```

## 🛠️ Comandos Úteis

### Verificar logs do Traefik
```bash
docker logs traefik-louis
```

### Verificar logs dos serviços
```bash
docker logs louis-backend-prod
docker logs louis-frontend-prod
```

### Backup dos certificados
```bash
# Criar backup do volume de certificados
docker run --rm -v louis-final_letsencrypt_data:/source -v $(pwd):/backup alpine tar czf /backup/certificados_backup.tar.gz -C /source .
```

### Restaurar certificados do backup
```bash
# Restaurar certificados do backup
docker run --rm -v louis-final_letsencrypt_data:/target -v $(pwd):/backup alpine tar xzf /backup/certificados_backup.tar.gz -C /target
```

## 🚨 Troubleshooting

### Se esgotar os limites do Let's Encrypt

1. **Aguarde** até a próxima semana
2. **Ou** use certificados autoassinados temporariamente
3. **Ou** mude temporariamente para outro domínio

### Se certificados expirarem

Os certificados renovam automaticamente. Se não renovar:

```bash
# Force a renovação
docker exec traefik-louis traefik update
```

## 📞 Contatos de Emergência

- Em caso de problemas críticos, verifique os logs
- Use `./verificar_certificados.sh` para diagnosticar
- Mantenha sempre um backup dos certificados 