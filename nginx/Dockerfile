FROM nginxinc/nginx-unprivileged:1.25-alpine

# Render template with envsubst on container start
COPY ./nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
