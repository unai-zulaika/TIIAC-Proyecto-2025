# Backend (FastAPI)

Backend asíncrono sin Docker. Usa PostgreSQL (async) y opcionalmente S3 para imágenes.

## Requisitos
- Python 3.10+
- PostgreSQL accesible (host/puerto/DB/usuario/clave)
- Credenciales AWS opcionales si necesitas URLs firmadas (S3)

## Configuración
1. Copia `src/backend/.env.example` a `.env` (en la raíz del repo o en `src/backend/`).
2. Ajusta variables: `POSTGRES_*`, `S3_*`, `CORS_ALLOW_ORIGINS`, `ENV`.

## Instalación
- Crea un entorno virtual e instala dependencias con:
  - `pip install -r src/backend/requirements.txt`

## Ejecutar
- Inicia el server: `uvicorn app.main:app --reload --app-dir src/backend --port 8080`

## Endpoints
- `GET /health`
- `GET /get_product_data?id=<item_id>`
- `GET /get_product_image?id=<item_id>`

## Notas
- Las tablas se crean automáticamente al iniciar (útil para dev/POC).
- El modelo principal es `Product` (tabla `items`).
