# Dockerfile para despliegue en Google Cloud Run
# Usa una imagen multi-etapa para optimizar el tamaño final

# Etapa 1: Build del frontend
FROM node:24-alpine AS frontend-builder

WORKDIR /app

# Copia solo los archivos necesarios para el frontend
COPY frontend/package.json frontend/package-lock.json ./
COPY frontend/ .

# Instala dependencias y construye el frontend
RUN npm install
RUN npm run build

# Etapa 2: Prepara el backend Python
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del backend
COPY backend/requirements.txt .
COPY backend/ .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa final: Imagen de producción
FROM python:3.11-slim

WORKDIR /app

# Copia el frontend construido desde la etapa 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copia el backend desde la etapa 2
COPY --from=backend-builder /app/ .

# Instala dependencias adicionales para producción
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Configura Nginx para servir el frontend
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expone los puertos
EXPOSE 80 8080

# Comando para iniciar la aplicación
CMD ["sh", "-c", "nginx && python main.py --dashboard"]