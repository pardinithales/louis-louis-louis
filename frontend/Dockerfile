# Use uma imagem base do Nginx, que é leve e eficiente
FROM nginx:alpine

# Copie os arquivos estáticos do frontend para o diretório padrão do Nginx
COPY ./frontend/ /usr/share/nginx/html

# Exponha a porta 80, que é a porta padrão do Nginx
EXPOSE 80

# O Nginx já é iniciado por padrão quando o contêiner é executado,
# então um CMD personalizado não é necessário. 