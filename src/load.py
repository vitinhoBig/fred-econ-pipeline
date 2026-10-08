import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    # Abrir a conexão usando a URL do .env
    # dica: psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(DATABASE_URL)


def create_table(conn, columns):
    columns_sql = ", ".join(f'"{col}" DOUBLE PRECISION' for col in columns)
    query = f'CREATE TABLE IF NOT EXISTS indicators (date DATE PRIMARY KEY, {columns_sql})'

    # executar a query usando um cursor
    # dica: with conn.cursor() as cur: cur.execute(query)
    with conn.cursor() as cur:
        cur.execute(query)

    conn.commit()


def upsert_data(conn, df):
    columns = df.columns.tolist()
    columns_sql = ", ".join(f'"{c}"' for c in columns)

    # montar a parte do UPDATE, no formato: "UNRATE" = EXCLUDED."UNRATE", "CPIAUCSL" = EXCLUDED."CPIAUCSL", ...
    # dica: ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in columns)
    update_sql = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in columns)

    query = f"""
        INSERT INTO indicators (date, {columns_sql}) VALUES %s
        ON CONFLICT (date) DO UPDATE SET {update_sql}
    """

    # trocar NaN por None antes de inserir (veja o aviso abaixo)
    # dica: df.astype(object).where(df.notna(), None)
    clean = df.astype(object).where(df.notna(), None)

    rows = [
        (date.date(), *values)
        for date, values in zip(clean.index, clean.itertuples(index=False))
    ]

    # Inserir tudo em lote
    # dica: with conn.cursor() as cur: execute_values(cur, query, rows)
    with conn.cursor() as cur:
        execute_values(cur, query, rows)

    conn.commit()


if __name__ == "__main__":
    from extract import load_series_config, fetch_series
    from transform import clean_series, merge_series, fill_missing

    series_list = load_series_config()
    cleaned = [clean_series(fetch_series(sid), sid) for sid in series_list]
    final_df = merge_series(cleaned)
    final_df = fill_missing(final_df)

    conn = get_connection()
    create_table(conn, final_df.columns)
    upsert_data(conn, final_df)
    conn.close()

    print("Dados salvos no PostgreSQL")