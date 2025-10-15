import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
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

def _sql_type_for_dtype(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"
    if pd.api.types.is_float_dtype(dtype):
        return "DOUBLE PRECISION"
    if pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    # fallback for object/strings and any unknown types
    return "TEXT"

def ensure_table_exists(df: pd.DataFrame, table_name: str):
    """
    Comprueba si la tabla existe en el esquema public. Si no existe, la crea
    con columnas basadas en los dtypes del DataFrame.
    """
    cursor.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s)",
        (table_name,)
    )
    exists = cursor.fetchone()[0]
    if exists:
        return

    column_defs = []
    for col, dtype in df.dtypes.items():
        sql_type = _sql_type_for_dtype(dtype)
        column_defs.append(
            sql.SQL("{} {}").format(sql.Identifier(col), sql.SQL(sql_type))
        )

    create_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(column_defs)
    )
    cursor.execute(create_query)
    conn.commit()
    print(f"[INFO] Tabla '{table_name}' creada con columnas: {', '.join(df.columns)}")

# ------------------------------
# Función para insertar un DataFrame
# ------------------------------
def insert_dataframe(df, table_name):
    if df.empty:
        print(f"[INFO] El DataFrame para {table_name} está vacío. Se omite inserción.")
        return

    # Asegurar que la tabla existe y, si no, crearla
    ensure_table_exists(df, table_name)

    # construir lista de columnas con comillas seguras
    columns = ','.join([f'"{c.replace(chr(34),"\"\"")}"' for c in df.columns])
    values = [tuple(x) for x in df.to_numpy()]
    query = f'INSERT INTO "{table_name}" ({columns}) VALUES %s'
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

def drop_table(table_name: str, cascade: bool = False):
    """
    Elimina la tabla `table_name` si existe. Si cascade=True, añade CASCADE.
    """
    drop_sql = sql.SQL("DROP TABLE IF EXISTS {} {}").format(
        sql.Identifier(table_name),
        sql.SQL("CASCADE") if cascade else sql.SQL("")
    )
    cursor.execute(drop_sql)
    conn.commit()
    print(f"[INFO] Tabla '{table_name}' eliminada{' con CASCADE' if cascade else ''}.")

drop_table('customers', cascade=True)
drop_table('articles', cascade=True)
drop_table('article_images', cascade=True)
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
