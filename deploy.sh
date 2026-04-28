#!/bin/bash

# --- 1. VALIDACIÓN DE VARIABLES ---
: "${DATABASE_URL:?Error: Falta DATABASE_URL}"
: "${SECRET_KEY:?Error: Falta SECRET_KEY}"
: "${ACCESS_TOKEN_EXPIRE_MINUTES:?Error: Falta ACCESS_TOKEN_EXPIRE_MINUTES}"
: "${ALGORITHM:?Error: Falta ALGORITHM}"

# --- 2. CONFIGURACIÓN DE RUTAS Y NOMBRES ---
FRONTEND_PATH="$HOME/roadside-assistance/frontend"
BACKEND_PATH="$HOME/roadside-assistance/backend"
BUCKET_NAME="gs://roadside-assistance-app"
SERVICE_NAME="roadside-assistance-api"
REGION="us-east1"

echo "🚀 Iniciando despliegue total..."

# --- 3. DESPLIEGUE DEL FRONTEND ---
echo "📦 Paso 1: Compilando Frontend Angular..."
cd "$FRONTEND_PATH" || exit
npm install && npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build exitoso. Sincronizando con Google Cloud Storage..."
    # Usamos rsync para que el bucket sea espejo exacto de la carpeta dist
    gsutil -m rsync -r -d dist/frontend/browser "$BUCKET_NAME"
else
    echo "❌ Error en el build del Frontend. El despliegue se ha detenido."
    exit 1
fi

# --- 4. DESPLIEGUE DEL BACKEND ---
echo "⚙️ Paso 2: Desplegando Backend a Cloud Run..."
cd "$BACKEND_PATH" || exit

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --set-env-vars DATABASE_URL="$DATABASE_URL",SECRET_KEY="$SECRET_KEY",ACCESS_TOKEN_EXPIRE_MINUTES="$ACCESS_TOKEN_EXPIRE_MINUTES",ALGORITHM="$ALGORITHM" \
  --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Backend desplegado con éxito en Cloud Run."
else
    echo "❌ Error en el despliegue del Backend."
    exit 1
fi

echo "🎉 ¡Todo listo! Frontend y Backend actualizados."