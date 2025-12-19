FROM node:10

WORKDIR /app
COPY . .
CMD ["echo", "This is a vulnerable app"]