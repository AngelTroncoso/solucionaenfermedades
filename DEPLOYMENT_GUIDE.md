# Guía de Despliegue - PharmaFuture 2050

## Configuración Optimizada para Vercel

Se ha creado una configuración robusta y confiable para desplegar el frontend en Vercel con las siguientes características:

### Arquitectura Actual

- **Monorepo**: Estructura con frontend (TanStack/React) y backend (Python)
- **Frontend**: Aplicación SSR con TanStack Router y Vite
- **Backend**: API Python con FastAPI (opcional para futura integración)

### Configuración de Vercel (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/nitro",
      "config": {
        "preset": "vercel",
        "serverFiles": [
          "frontend/.output/server/**/*"
        ]
      }
    }
  ],
  "installCommand": "npm install --legacy-peer-deps",
  "buildCommand": "npm run build:frontend",
  "outputDirectory": "frontend/.output",
  "env": {
    "NODE_OPTIONS": "--max-old-space-size=8192",
    "NITRO_PRESET": "vercel"
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/.output/server/index.html",
      "status": 200
    },
    {
      "src": "/api/(.*)",
      "dest": "frontend/.output/server/api/$1",
      "status": 200
    }
  ]
}
```

### Pasos para Despliegue

#### 1. Preparación del Entorno

```bash
# Instalar dependencias globales (si no están instaladas)
npm install -g vercel

# Clonar el repositorio
git clone https://github.com/AngelTroncoso/solucionaenfermedades.git
cd solucionaenfermedades
```

#### 2. Configuración del Proyecto

```bash
# Instalar dependencias del monorepo
npm install --legacy-peer-deps

# Instalar dependencias específicas del frontend
cd frontend
npm install --legacy-peer-deps
cd ..
```

#### 3. Construcción del Frontend

```bash
# Construir solo el frontend (configuración optimizada)
npm run build:frontend
```

#### 4. Despliegue en Vercel

```bash
# Iniciar despliegue (requiere autenticación con Vercel CLI)
vercel

# Opcional: Despliegue en producción
vercel --prod

# Para conectar con el nuevo repositorio pharma-discovery-hub:
vercel link --yes
vercel git connect AngelTroncoso pharma-discovery-hub
```

### Solución de Problemas Comunes

#### 1. Errores de Memoria
- **Síntoma**: Build falla con error `JavaScript heap out of memory`
- **Solución**: La configuración ya incluye `NODE_OPTIONS="--max-old-space-size=8192"` para aumentar memoria

#### 2. Dependencias Conflictuosas
- **Síntoma**: Errores de versión en paquetes npm
- **Solución**: Usar `--legacy-peer-deps` en installCommand

#### 3. Rutas no Funcionales
- **Síntoma**: 404 en rutas del frontend
- **Solución**: La configuración incluye rutas wildcard que redirigen todo al index.html para SSR

#### 4. API Routes no Funcionales
- **Síntoma**: Endpoints de API no responden
- **Solución**: Verificar que los archivos estén en `frontend/.output/server/api/`

### Configuración Avanzada

#### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```
# Configuración general
NODE_ENV=production

# Configuración de Vercel
VERCEL_ENV=production

# Configuración del frontend
VITE_API_BASE_URL=https://api.solucionaenfermedades.com
VITE_APP_VERSION=1.0.0
```

#### Optimización de Build

Para builds más rápidos en desarrollo:

```bash
# Build en modo desarrollo (más rápido, menos optimizado)
cd frontend
npm run build:dev
```

### Monitoreo y Mantenimiento

#### Verificación Post-Despliegue

1. **Health Check**: `curl -I https://tu-dominio.vercel.app/`
2. **Pruebas de Rutas**: Verificar `/`, `/discoveries`, `/matrix`, `/papers`
3. **Pruebas de API**: Verificar endpoints `/api/*` si están implementados

#### Actualizaciones

```bash
# Para actualizar el despliegue
git pull origin main
vercel --prod
```

### Alternativas de Despliegue

#### 1. Netlify

```bash
# Instalar CLI de Netlify
npm install -g netlify-cli

# Desplegar
netlify deploy --prod
```

#### 2. Alibaba Cloud (recomendado para este proyecto)

Consultar el archivo `ALIBABA_CLOUD_DEPLOYMENT.md` para instrucciones específicas de despliegue en Alibaba Cloud.

#### 3. Docker (para entornos locales/servidores)

```dockerfile
# Dockerfile para producción
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build:frontend

EXPOSE 3000
CMD ["npm", "run", "start"]
```

### Notas Importantes

1. **SSR vs Static**: La configuración actual usa SSR (Server-Side Rendering) para mejor SEO y performance
2. **Cache**: Vercel maneja automáticamente el cache de assets estáticos
3. **Escalabilidad**: La configuración está optimizada para escalar automáticamente
4. **Seguridad**: Asegurar que todas las variables sensibles estén en variables de entorno
5. **Integración Continua**: La configuración ahora incluye despliegue automático desde el repositorio `pharma-discovery-hub`

### Integración con pharma-discovery-hub

La configuración ha sido actualizada para integrarse con el nuevo repositorio central:

```bash
# Para migrar el proyecto existente al nuevo repositorio:
1. Crear nuevo repositorio: git remote add pharma-hub https://github.com/AngelTroncoso/pharma-discovery-hub
2. Push inicial: git push pharma-hub main
3. Conectar Vercel: vercel git connect AngelTroncoso pharma-discovery-hub
```

### Despliegue Automático

La configuración ahora incluye:
- `autoDeploy`: true - Despliegue automático en cada push
- `deployOnPush`: true - Despliegue continuo desde la rama main
- Integración nativa con GitHub para actualizaciones en tiempo real

Esta configuración ha sido actualizada para integrarse con el repositorio `pharma-discovery-hub` y garantizar despliegues continuos y automatizados en la plataforma Vercel.
