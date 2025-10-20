Estos son los valores que hay que tener en el .env dentro de la carpeta docker

# PostgreSQL
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password
POSTGRES_DB=productos_db
POSTGRES_PORT=5432
POSTGRES_HOST=postgres


# MinIO (S3 local)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_BUCKET_NAME=productos
MINIO_ENDPOINT=http://minio:9000


# Ejecutar Docker
Entrar en la carpeta docker y ejecutar el comando "docker-compose up --build"

# Acceso a MinIO
Acceder a http://127.0.0.1:9001/
- Usuario: minioadmin
- Contraseña: minioadmin123