Estos son los valores que hay que tener en el .env dentro de la carpeta docker

# PostgreSQL
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password
POSTGRES_DB=productos_db
POSTGRES_PORT=5432
POSTGRES_NAME=productos_db


# MinIO (S3 local)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_BUCKET_NAME=productos
