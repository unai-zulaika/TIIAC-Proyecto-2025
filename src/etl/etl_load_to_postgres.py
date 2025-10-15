import os
import logging
import pandas as pd
from sqlalchemy import create_engine
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger()


# ---------------------------------------
# Conexión a PostgreSQL
# ---------------------------------------
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


# ---------------------------------------
# Conexión a MinIO (S3)
# ---------------------------------------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1"
)


# ---------------------------------------
# Cargar CSVs
# ---------------------------------------
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "./data"))
CSV_DIR = os.path.join(DATA_DIR, "csv")
articles_path = os.path.join(CSV_DIR, "articles.csv")
customers_path = os.path.join(CSV_DIR, "customers.csv")

logger.info("Cargando archivos CSV...")
articles_df = pd.read_csv(articles_path, dtype={'article_id': str, 'product_code': str})
customers_df = pd.read_csv(customers_path)


# ---------------------------------------
# Limpieza básica
# ---------------------------------------
logger.info("Limpiando datos...")
articles_df.drop_duplicates(subset=["article_id"], inplace=True)
customers_df.drop_duplicates(subset=["customer_id"], inplace=True)

customers_df["FN"] = customers_df["FN"].fillna(0).astype(bool)
customers_df["Active"] = customers_df["Active"].fillna(0).astype(bool)


# ---------------------------------------
# Cargar metadatos en PostgreSQL
# ---------------------------------------
logger.info("Cargando datos a PostgreSQL...")
articles_df.to_sql("articles", engine, if_exists="append", index=False)
customers_df.to_sql("customers", engine, if_exists="append", index=False)
logger.info("Metadatos cargados correctamente en PostgreSQL.")


# ---------------------------------------
# Subir imágenes a MinIO
# ---------------------------------------
IMAGES_DIR = os.path.join(DATA_DIR, "img")
images_list = os.listdir(IMAGES_DIR) if os.path.exists(IMAGES_DIR) else []

if not os.path.exists(IMAGES_DIR):
    logger.warning(f"No se encontró la carpeta de imágenes en {IMAGES_DIR}")
else:
    uploaded_count = 0
    logger.info("Subiendo imágenes a MinIO...")
    for image_filename in images_list:
        image_path = os.path.join(IMAGES_DIR, image_filename)
        product_name = articles_df['prod_name'].loc[articles_df['article_id'].astype(str) == image_filename.split('.')[0]].values[0]
        if os.path.exists(image_path):
            try:
                s3_client.upload_file(image_path, MINIO_BUCKET, f"productos/{image_filename}")
                uploaded_count += 1
            except (NoCredentialsError, ClientError) as e:
                logger.error(f"Error al subir {image_filename}: {e}")

    logger.info(f"Imágenes subidas a MinIO correctamente: {uploaded_count}/{len(articles_df)}")

logger.info("Proceso ETL completado correctamente.")