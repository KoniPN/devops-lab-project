FROM nginx:alpine
# รับค่าจาก Jenkins มาแสดงผล
ARG APP_VERSION
RUN echo "<h1>Deployed Version: ${APP_VERSION}</h1>" > /usr/share/nginx/html/index.html