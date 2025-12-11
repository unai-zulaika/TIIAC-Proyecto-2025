"""
ETL script connecting to a local PostgreSQL container.

Environment (docker run example):
        -e POSTGRES_USER=mi_usuario
        -e POSTGRES_PASSWORD=mi_contraseña
        -e POSTGRES_DB=mi_basedatos

Install dependency:
        pip install psycopg2-binary
"""

import os
import sys
import logging
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, Json, execute_values
import pandas as pd


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
)
logger = logging.getLogger("etl")

# Read credentials from environment (fallback to provided defaults)
def _safe_env(name: str, default: str):
    raw = os.getenv(name)
    if raw is None:
        return default
    # replace invalid bytes so psycopg2 won't raise UnicodeDecodeError
    safe = raw.encode("utf-8", errors="replace").decode("utf-8")
    if safe != raw:
        logger.warning("Environment variable %s contained invalid UTF-8 bytes; replaced.", name)
    return safe

DB_USER = _safe_env("POSTGRES_USER", "usuario")
DB_PASSWORD = _safe_env("POSTGRES_PASSWORD", "contraseña")
DB_NAME = _safe_env("POSTGRES_DB", "HM")
DB_HOST = _safe_env("POSTGRES_HOST", "localhost")
try:
    DB_PORT = int(_safe_env("POSTGRES_PORT", "5432"))
except ValueError:
    DB_PORT = 5432
logger.info("Connecting to DB %s at %s:%s as user %s", DB_NAME, DB_HOST, DB_PORT, DB_USER)

def get_connection():
        
        return psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host="localhost",
                port=5432,
                connect_timeout=50,
        )

@contextmanager
def db_cursor(dict_rows: bool = True):
        conn = None
        cur = None
        try:
                conn = get_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor if dict_rows else None)
                yield cur
                conn.commit()
        except psycopg2.Error as exc:
                if conn:
                        conn.rollback()
                logger.exception("Database operation failed: %s", exc)
                raise
        finally:
                if cur:
                        cur.close()
                if conn:
                        conn.close()

def extract():
        logger.info("Extract step")
        with db_cursor() as cur:
                cur.execute("SELECT 1 AS ok;")
                return cur.fetchall()

def transform(rows):
        logger.info("Transform step")
        # Example transform: convert dict keys to upper-case
        transformed = [{k.upper(): v for k, v in row.items()} for row in rows]
        return transformed

def load_df(df, table_name="etl_demo"):
        """ Creates a table with DF columns and loads the data """
        logger.info("Load DataFrame step")
        with db_cursor(dict_rows=False) as cur:
                # Create table with columns based on DataFrame
                columns = df.columns
                col_defs = ", ".join(f"{col} TEXT" for col in columns)
                cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs});")
                # Prepare data for insertion
                values = [tuple(row) for row in df.to_numpy()]
                # Batch insert for efficiency
                execute_values(
                        cur,
                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s",
                        values,
                )
        logger.info("Loaded %d rows into %s", len(df), table_name)

def load(rows, table_name="etl_demo"):
        logger.info("Load step (demo)")
        with db_cursor(dict_rows=False) as cur:
                cur.execute(
                        f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, payload JSONB NOT NULL);"
                )
                # Use PostgreSQL JSONB capabilities; wrap Python dicts with Json so psycopg2 can adapt them
                values = [(Json(row),) for row in rows]
                # Batch insert for efficiency
                execute_values(cur, f"INSERT INTO {table_name} (payload) VALUES %s", values)
        logger.info("Loaded %d rows", len(rows))

def health_check():
        try:
                with db_cursor() as cur:
                        cur.execute(
                                "SELECT current_database() db, current_user usr, version() v;"
                        )
                        row = cur.fetchone()
                        if not row:
                                logger.error("Health check query returned no rows")
                                sys.exit(1)
                        info = dict(row)
                        logger.info("Connected: db=%s user=%s", info.get("db"), info.get("usr"))
        except psycopg2.Error:
                logger.error("Health check failed")
                sys.exit(1)

# load file function for csv files
def load_csv(file_path):
        logger.info("Load CSV file: %s", file_path)
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        return df

def run_etl():
        health_check()
        # df = load_csv("../../data/articles.csv")
        # print(df.head())

        # load_df(df, table_name="products")

        df = load_csv("../../data/transactions_train.csv")
        load_df(df, table_name="transactions")
        logger.info("ETL completed")

if __name__ == "__main__":
        run_etl()
        # PGPASSWORD='mi_contraseña' psql -h localhost -p 5432 -U mi_usuario -d mi_basedatos -c "SELECT * FROM etl_demo LIMIT 5;"