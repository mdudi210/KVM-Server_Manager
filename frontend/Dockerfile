FROM node:20.15.1-slim

WORKDIR /app

COPY frontend/package*.json frontend/jsconfig.json ./
RUN npm ci

COPY frontend/ .

RUN npm run build \
    && npm install -g serve

EXPOSE 8080

CMD ["serve", "-s", "dist", "-l", "8080"]
