FROM nginx:1.25-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
COPY includes/ /etc/nginx/includes/

RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx && \
    chmod -R 755 /var/cache/nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
