# Louis - Sistema de Inferência de Síndromes Neurológicas

Este projeto implementa uma aplicação web completa para inferência de síndromes neurológicas a partir de descrições clínicas. Ele é composto por um frontend em HTML/CSS/JS e um backend em Python com FastAPI, ambos containerizados com Docker e gerenciados em produção pelo reverse proxy Traefik.

## Arquitetura de Produção na VPS

A aplicação está hospedada em uma VPS Ubuntu e utiliza uma arquitetura baseada em Docker e Traefik para simplificar o roteamento e a segurança.

- **Domínio Principal:** `https://louis.tpfbrain.com`
- **IP do Servidor:** `138.199.224.191`

### Componentes:

1.  **Traefik (Reverse Proxy):**
    - É o ponto de entrada de todo o tráfego web.
    - Gerencia os certificados SSL (HTTPS) automaticamente via Let's Encrypt.
    - Roteia as requisições para o serviço correto com base no caminho da URL.

2.  **Frontend (Nginx):**
    - Servido em `https://louis.tpfbrain.com/`.
    - Quando um usuário acessa a URL principal, o Traefik direciona a requisição para o contêiner do frontend.

3.  **Backend (FastAPI):**
    - Recebe requisições através do caminho `/api/`.
    - Quando o frontend faz uma chamada para `https://louis.tpfbrain.com/api/...`, o Traefik intercepta, direciona para o contêiner do backend e remove o prefixo `/api` antes de a requisição chegar na aplicação FastAPI.
    - Essa arquitetura elimina a necessidade de CORS (Cross-Origin Resource Sharing), tornando a comunicação mais simples e segura.

## Como Atualizar a Aplicação na VPS

Para atualizar a aplicação após fazer alterações no código localmente, siga estes dois processos:

### Processo 1: Enviar as Alterações para o GitHub

No seu computador **local**, execute os seguintes comandos para enviar suas modificações para o repositório principal:

```bash
# 1. Adiciona todos os arquivos modificados
git add .

# 2. Cria um commit com uma mensagem descritiva
git commit -m "feat: descreva aqui a sua alteração"

# 3. Envia as alterações para o GitHub
git push
```

---

### Processo 2: Atualizar a Aplicação na VPS

Conecte-se à sua VPS e execute os comandos abaixo. Eles irão baixar a versão mais recente do código e reconstruir os serviços com zero tempo de inatividade.

```bash
# 1. Navegue para o diretório do projeto
cd /root/louis-final

# 2. Baixe as alterações mais recentes do GitHub
git pull

# 3. Reconstrua e reinicie os contêineres com o novo código
# A flag --build garante que qualquer alteração nos Dockerfiles ou no código
# seja incorporada nas novas imagens dos contêineres.
docker-compose up -d --build
```

### Em Caso de Problemas Graves (Reset Completo)

Se a aplicação apresentar erros persistentes após uma atualização (como o `KeyError: 'ContainerConfig'`), pode ser necessário forçar uma limpeza completa do ambiente Docker. **Use este procedimento com cuidado**, pois ele apaga todos os dados em cache e os volumes.

```bash
# 1. Navegue para o diretório do projeto
cd /root/louis-final

# 2. Derrube todos os serviços, volumes e imagens relacionadas ao projeto
docker-compose down --volumes --rmi all

# 3. Suba tudo novamente, forçando uma reconstrução do zero
docker-compose up -d --build
``` 