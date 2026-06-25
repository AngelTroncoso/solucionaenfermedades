# 🚀 Configuración de Producción - SolucionaEnfermedades

## 📋 Estado Actual

✅ **Frontend (Vercel)** - **Listo para producción**
- Configuración optimizada en `vercel.json`
- Usa `npm ci` para instalación limpia
- Memoria configurada con `NODE_OPTIONS=--max-old-space-size=4096`
- Sin variables de entorno requeridas

✅ **Backend (Python)** - **Configurado para producción**
- Archivo `.env` creado con API keys reales
- Todas las dependencias en `requirements.txt`
- Configuración optimizada para producción

## 🔑 Variables de Entorno (backend/.env)

**🔒 IMPORTANTE:** El archivo `backend/.env` contiene claves sensibles y está en `.gitignore`

```env
# Proveedor principal
LLM_PROVIDER=dashscope

# Claves de API (reales) - COPIAR DESDE backend/.env
DASHSCOPE_API_KEY=sk-ws-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Modelos configurados
MODEL_REASONING=qwen3-235b-a22b
MODEL_EVALUATION=qwen3-32b
MODEL_REFINER=qwen2.5-72b-instruct
MODEL_LIGHT=qwen2.5-7b-instruct
MODEL_EMBEDDINGS=text-embedding-v3

# Parámetros optimizados
MAX_ITERATIONS=10
FITNESS_THRESHOLD=0.85
POPULATION_SIZE=15
MUTATION_RATE=0.25
EARLY_STOP_ROUNDS=3
```

## 🎯 Pasos para Despliegue

### 1. Frontend (Vercel)
```bash
# Ya configurado - solo desplegar
git push origin main
```

### 2. Backend (Python)
**Opciones de despliegue:**

#### Opción A: Vercel (si es compatible con Python)
1. Crear `vercel.json` para backend (ejemplo):
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    }
  ],
  "env": {
    "LLM_PROVIDER": "dashscope",
    "DASHSCOPE_API_KEY": "@dashscope_api_key",
    "OPENROUTER_API_KEY": "@openrouter_api_key"
  }
}
```

#### Opción B: Servicios recomendados para Python
1. **AWS Elastic Beanstalk**
2. **Google Cloud Run**
3. **Azure App Service**
4. **Render.com** (gratis para proyectos pequeños)

**Configuración básica para cualquier servicio:**
- Runtime: Python 3.10+
- Command: `python main.py --dashboard`
- Variables de entorno: Copiar todas del `.env` file
- Dependencias: `requirements.txt`

## 🔧 Comandos Útiles

```bash
# Instalar dependencias de backend
cd backend
pip install -r requirements.txt

# Ejecutar backend localmente
python main.py --dashboard

# Ejecutar frontend localmente
cd frontend
npm run dev

# Build para producción
cd frontend
npm run build
```

## ⚠️ Notas Importantes

1. **Nunca commits .env files** - Ya están en `.gitignore`
2. **Rotación de claves** - Cambiar API keys periódicamente
3. **Monitoreo** - Configurar logs y alertas en producción
4. **Escalabilidad** - Considerar servicios serverless para el backend

## 📊 Recursos Adicionales

- [Documentación Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
- [Documentación OpenRouter](https://openrouter.ai/docs)
- [Guía de Despliegue Vercel](https://vercel.com/docs)