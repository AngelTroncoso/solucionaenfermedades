# 🚀 Despliegue en Google Cloud

Este documento proporciona instrucciones completas para desplegar la aplicación en Google Cloud usando **Cloud Run**.

## 📋 Requisitos Previos

1. **Cuenta de Google Cloud** con facturación habilitada
2. **Google Cloud SDK** instalado (`gcloud` CLI)
3. **Docker** instalado localmente
4. **Proyecto de Google Cloud** creado

## 🐳 Configuración del Contenedor Docker

### 1. Construir la imagen Docker

```bash
docker build -t solucionaenfermedades .
```

### 2. Probar localmente (opcional)

```bash
docker run -p 8080:80 solucionaenfermedades
```

La aplicación estará disponible en: `http://localhost:8080`

## ☁️ Despliegue en Google Cloud Run

### 1. Autenticarse con Google Cloud

```bash
gcloud auth login
gcloud config set project TU_PROYECTO_ID
```

### 2. Habilitar APIs necesarias

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Construir y subir la imagen a Google Container Registry

```bash
# Etiquetar la imagen para GCR
docker tag solucionaenfermedades gcr.io/TU_PROYECTO_ID/solucionaenfermedades

# Subir la imagen
docker push gcr.io/TU_PROYECTO_ID/solucionaenfermedades
```

### 4. Desplegar en Cloud Run

```bash
gcloud run deploy solucionaenfermedades \
  --image gcr.io/TU_PROYECTO_ID/solucionaenfermedades \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 80
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Si necesitas configurar variables de entorno:

```bash
gcloud run deploy solucionaenfermedades \
  --image gcr.io/TU_PROYECTO_ID/solucionaenfermedades \
  --update-env-vars VAR1=valor1,VAR2=valor2
```

### Escalado Automático

Cloud Run escala automáticamente a cero cuando no hay tráfico y escala según la demanda.

### Dominio Personalizado

1. Configura un dominio en Google Cloud
2. Mapea el dominio a tu servicio Cloud Run

## 📝 Estructura del Proyecto para Google Cloud

```
project-root/
├── Dockerfile          # Configuración del contenedor
├── nginx.conf           # Configuración de Nginx
├── .dockerignore        # Archivos a ignorar en el build
├── backend/             # Backend Python/Streamlit
│   ├── main.py          # Punto de entrada del backend
│   ├── requirements.txt # Dependencias Python
│   └── ...              # Otros archivos del backend
├── frontend/            # Frontend Vite/React
│   ├── src/             # Código fuente
│   ├── package.json     # Configuración del frontend
│   └── ...              # Otros archivos del frontend
└── ...                  # Otros archivos del proyecto
```

## 🔄 Actualizaciones Futuras

1. Haz tus cambios en el código
2. Reconstruye la imagen Docker:
   ```bash
   docker build -t solucionaenfermedades .
   docker tag solucionaenfermedades gcr.io/TU_PROYECTO_ID/solucionaenfermedades
   docker push gcr.io/TU_PROYECTO_ID/solucionaenfermedades
   ```
3. Despliega la nueva versión:
   ```bash
   gcloud run deploy solucionaenfermedades \
     --image gcr.io/TU_PROYECTO_ID/solucionaenfermedades \
     --platform managed \
     --region us-central1
   ```

## 💡 Consejos para Google Cloud

- **Monitoreo:** Usa Cloud Monitoring para supervisar el rendimiento
- **Logs:** Usa Cloud Logging para ver los logs de la aplicación
- **Costos:** Cloud Run tiene un modelo de pago por uso, ideal para aplicaciones con tráfico variable
- **Seguridad:** Configura IAM adecuadamente para controlar el acceso

## 🚨 Solución de Problemas

**Problema:** La aplicación no inicia
- Verifica los logs: `gcloud logging read "resource.type=cloud_run_revision" --limit 50`
- Asegúrate de que todos los puertos estén correctamente configurados

**Problema:** Error de permisos
- Verifica que tu cuenta tenga permisos de `Cloud Run Admin` y `Service Account User`

**Problema:** Tiempo de inicio lento
- Considera usar imágenes Docker más pequeñas (Alpine)
- Optimiza las dependencias en requirements.txt

¡Listo para desplegar en Google Cloud! 🎉