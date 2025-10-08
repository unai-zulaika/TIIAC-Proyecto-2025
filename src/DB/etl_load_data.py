import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os

# ------------------------------
# Configuración de conexión a PostgreSQL
# ------------------------------
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'HM'
DB_USER = 'usuario'
DB_PASSWORD = 'contraseña'

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# ------------------------------
# Función para insertar un DataFrame
# ------------------------------
def insert_dataframe(df, table_name):
    if df.empty:
        print(f"[INFO] El DataFrame para {table_name} está vacío. Se omite inserción.")
        return
    columns = ','.join(df.columns)
    values = [tuple(x) for x in df.to_numpy()]
    query = f"INSERT INTO {table_name} ({columns}) VALUES %s"
    execute_values(cursor, query, values)
    conn.commit()
    print(f"[OK] Insertadas {len(df)} filas en {table_name}.")

# ------------------------------
# 1️⃣ Cargar CSVs
# ------------------------------
default_csv_dir = 'descargas'

try:
    customers_df = pd.read_csv(os.path.join(default_csv_dir, 'customers.csv'))
except FileNotFoundError:
    customers_path = input("customers.csv no encontrado. Indica la ruta completa: ")
    customers_df = pd.read_csv(customers_path)

try:
    articles_df = pd.read_csv(os.path.join(default_csv_dir, 'articles.csv'))
except FileNotFoundError:
    articles_path = input("articles.csv no encontrado. Indica la ruta completa: ")
    articles_df = pd.read_csv(articles_path)

# ------------------------------
# 2️⃣ Insertar en la base de datos
# ------------------------------
insert_dataframe(customers_df, 'customers')
insert_dataframe(articles_df, 'articles')

# ------------------------------
# 3️⃣ Registrar imágenes
# ------------------------------
default_image_dir = 'descargas/images'

if not os.path.exists(default_image_dir):
    image_dir = input("Carpeta de imágenes no encontrada. Indica la ruta completa: ")
else:
    image_dir = default_image_dir

image_rows = []
for root, _, files in os.walk(image_dir):
    for file_name in files:
        if file_name.endswith('.jpg'):
            try:
                article_id = int(file_name.replace('.jpg',''))
                image_path = os.path.join(root, file_name).replace("\\","/")
                image_rows.append((article_id, image_path))
            except ValueError:
                print(f"[WARN] Nombre de archivo no válido para article_id: {file_name}")

if image_rows:
    execute_values(cursor,
        "INSERT INTO article_images (article_id, image_path) VALUES %s",
        image_rows
    )
    conn.commit()
    print(f"[OK] Insertadas {len(image_rows)} rutas de imágenes.")

# ------------------------------
# 4️⃣ Cerrar conexión
# ------------------------------
cursor.close()
conn.close()
print("ETL finalizada correctamente ✅")
