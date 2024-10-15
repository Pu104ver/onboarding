FROM nginx:1.23-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./api-nginx-proxy-headers.conf /etc/nginx/conf/api-nginx-proxy-headers.conf
COPY ./nginx.conf /etc/nginx/conf.d/
