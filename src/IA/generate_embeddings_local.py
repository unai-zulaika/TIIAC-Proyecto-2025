import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
from sentence_transformers import SentenceTransformer
import numpy as np
import sys
import traceback

# ------------------------------
# Configuración PostgreSQL
# ------------------------------
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "HM"
DB_USER = "usuario"
DB_PASSWORD = "contraseña"

EMB_MODEL_NAME = "all-MiniLM-L6-v2"
EMB_DIM = 384  # dimensión conocida para el modelo anterior

def connect():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def ensure_pgvector_and_tables(cur):
    """
    Crea solo la tabla customer_embeddings. Intentará usar pgvector
    y, si no está disponible, usará double precision[] como fallback.
    """
    use_pgvector = True
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    except (psycopg2.errors.FeatureNotSupported, psycopg2.errors.UndefinedFile):
        cur.connection.rollback()
        use_pgvector = False
        print("[WARN] pgvector no disponible en el servidor. Usando double precision[] como fallback.")
    except Exception:
        cur.connection.rollback()
        use_pgvector = False
        print("[WARN] Error comprobando pgvector; usando double precision[] como fallback.")

    if use_pgvector:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_embeddings (
            customer_id TEXT PRIMARY KEY,
            embedding vector(%s)
        );
        """, (EMB_DIM,))
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_embeddings (
            customer_id TEXT PRIMARY KEY,
            embedding double precision[]
        );
        """)

def fetch_customers_with_purchases(cur):
    """
    Devuelve lista de customer_id que aparecen en transactions o interactions.
    Ignora tablas que no existan.
    """
    customers = set()
    for table in ("transactions", "interactions"):
        try:
            cur.execute(f"SELECT DISTINCT customer_id FROM {table}")
            rows = cur.fetchall()
            for r in rows:
                customers.add(r.get("customer_id"))
        except psycopg2.errors.UndefinedTable:
            cur.connection.rollback()
            print(f"[WARN] Tabla '{table}' no existe. Se omite.")
            continue
    return list(customers)

def fetch_article_texts_for_customer(cur, customer_id):
    """
    Recupera los textos (prod_name + detail_desc) de los artículos
    asociados a customer_id. Evita errores de tipos en JOIN recogiendo
    article_id en Python y consultando la tabla articles con casts seguros.
    """
    article_ids = []
    for table in ("transactions", "interactions"):
        try:
            cur.execute(f"SELECT article_id FROM {table} WHERE customer_id = %s", (customer_id,))
            rows = cur.fetchall()
            for r in rows:
                aid = r.get("article_id")
                if aid is not None:
                    article_ids.append(aid)
        except psycopg2.errors.UndefinedTable:
            cur.connection.rollback()
            continue

    # mantener orden y eliminar duplicados
    seen_ids = set()
    uniq_ids = []
    for aid in article_ids:
        if aid not in seen_ids:
            seen_ids.add(aid)
            uniq_ids.append(aid)
    if not uniq_ids:
        return []

    # separar ids numéricos de no numéricos para consultas seguras
    int_ids = []
    str_ids = []
    for aid in uniq_ids:
        try:
            int_ids.append(int(aid))
        except Exception:
            str_ids.append(str(aid))

    texts = []

    if int_ids:
        try:
            cur.execute("SELECT prod_name, detail_desc FROM articles WHERE article_id = ANY(%s)", (int_ids,))
            rows = cur.fetchall()
            for r in rows:
                name = r.get("prod_name") or ""
                desc = r.get("detail_desc") or ""
                text = f"{name}. {desc}" if desc else name
                if text.strip():
                    texts.append(text)
        except Exception:
            cur.connection.rollback()

    if str_ids:
        try:
            # casteamos article_id a text para comparar con strings
            cur.execute("SELECT prod_name, detail_desc FROM articles WHERE article_id::text = ANY(%s)", (str_ids,))
            rows = cur.fetchall()
            for r in rows:
                name = r.get("prod_name") or ""
                desc = r.get("detail_desc") or ""
                text = f"{name}. {desc}" if desc else name
                if text.strip():
                    texts.append(text)
        except Exception:
            cur.connection.rollback()

    # eliminar duplicados manteniendo orden
    seen = set()
    uniq_texts = []
    for t in texts:
        if t not in seen:
            seen.add(t)
            uniq_texts.append(t)
    return uniq_texts

def upsert_customer_embedding(cur, customer_id, vector):
    cur.execute(
        """
        INSERT INTO customer_embeddings (customer_id, embedding)
        VALUES (%s, %s)
        ON CONFLICT (customer_id) DO UPDATE SET embedding = EXCLUDED.embedding
        """,
        (customer_id, vector)
    )

def main():
    model = SentenceTransformer(EMB_MODEL_NAME)
    conn = None
    try:
        conn = connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        ensure_pgvector_and_tables(cur)
        conn.commit()

        customers = fetch_customers_with_purchases(cur)
        print(f"Generando embeddings para {len(customers)} clientes (solo con artículos comprados/interactuados)...")

        for customer_id in customers:
            try:
                texts = fetch_article_texts_for_customer(cur, customer_id)
                if not texts:
                    print(f"[SKIP] cliente {customer_id} sin artículos asociados.")
                    continue

                # Codificar en batch y promediar
                vecs = model.encode(texts, convert_to_numpy=True)
                vecs = np.asarray(vecs, dtype=float)
                if vecs.ndim == 1:
                    mean_vec = vecs
                else:
                    mean_vec = vecs.mean(axis=0)

                mean_vec = np.asarray(mean_vec, dtype=float)
                if mean_vec.shape[0] != EMB_DIM:
                    raise ValueError(f"Dimensión embedding incorrecta: {mean_vec.shape[0]} != {EMB_DIM}")

                upsert_customer_embedding(cur, str(customer_id), mean_vec.tolist())
                conn.commit()
                print(f"✅ Embedding cliente {customer_id} (basado en {len(texts)} artículos)")
            except Exception:
                conn.rollback()
                print(f"❌ Error creando embedding cliente {customer_id}:")
                traceback.print_exc(file=sys.stdout)

        cur.close()
        print("✅ Embeddings de clientes generados.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()