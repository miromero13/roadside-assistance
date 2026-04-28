#!/bin/bash

# --- CONFIGURACIÓN ---
PROJECT_ID=$(gcloud config get-value project)
FRONTEND_PATH="$HOME/roadside-assistance/frontend"
BACKEND_PATH="$HOME/roadside-assistance/backend"
BUCKET_NAME="gs://roadside-assistance-app"
SERVICE_NAME="roadside-assistance-api"
REGION="us-east1"

echo "🚀 Iniciando despliegue total en el proyecto: $PROJECT_ID"

# 1. Despliegue del Frontend
echo "📦 Compilando Frontend..."
cd $FRONTEND_PATH
npm install && npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build de Frontend exitoso. Sincronizando con Storage..."
    # Ajusta la ruta dist/ si tu build sale en otra carpeta
    gsutil -m rsync -r -d dist/frontend/browser $BUCKET_NAME
else
    echo "❌ Error en el build del Frontend. Abortando."
    exit 1
fi

# 2. Despliegue del Backend
echo "⚙️ Desplegando Backend a Cloud Run..."
cd $BACKEND_PATH
gcloud run deploy $SERVICE_NAME --source . --region $REGION --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Backend desplegado con éxito."
else
    echo "❌ Error en el despliegue del Backend."
    exit 1
fi

echo "🎉 ¡Despliegue completado con éxito!"