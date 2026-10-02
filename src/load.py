import os
import sqlite3

DB_PATH = "data/processed/fred_data.db"

# Path to the SQLite database file. A relative path keeps this portable
# across machines, as long as the script always runs from the project root.
def get_connection(db_path=DB_PATH):
    # Make sure the destination folder exists before SQLite tries to create
    # the .db file inside it - sqlite3.connect() will NOT create missing
    # directories on its own, only the file itself.
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # sqlite3.connect() opens the database file if it already exists, or
    # creates a brand-new empty one if it doesn't. The returned Connection
    # object is how we send SQL commands to the database.
    return sqlite3.connect(db_path)

def create_table(conn, columns):
    # Build the column definitions dynamically, since the number/names of 
    # economic series can change depending on config/series.yaml.
    # Result looks like: "UNRATE" REAL, "CPIAUCSL" REAL, "FEDFUNDS" REAL, "GDP" REAL
    columns_sql = ", ".join(f'"{col}" REAL' for col in columns)

    # "date" is the PRIMARY KEY: SQLite guarantees no two rows can share the 
    # same date. That constraint is exactly what makes INSERT OR REPLACE
    # behave as an upsert later on, instead of silently creating duplicates. 
    # IF NOT EXISTS makes this safe to run every time the pipeline runs - 
    # it won't wipe or error out if the table is already there.
    query = f'CREATE TABLE IF NOT EXISTS indicators (date TEXT PRIMARY KEY, {columns_sql})'

    # execute() runs a single SQL statement - no repeated parameter here.
    conn.execute(query)

    # Changes made through sqlite3 aren't written to disk until you commit - 
    # think of it as "confirmiting the transaction"
    conn.commit()

def upsert_data(conn, df):
    columns = df.columns.tolist()
    columns_sql = ", ".join(f'"{c}"' for c in columns)

    # One "?" placeholder per value being inserte: date + one per series.
    # Using placeholders (insted of f-sting-in values directly into the 
    # SQL) protects against SQL injection and handles type converssion for 
    # us - standar pracitce any time real data is being inserted.
    placeholders = ", ".join(["?"] * (len(columns)+ 1))

    # INSERT OR REPLACE is SQLite's upsert: if a row with that date (the 
    # PRIMARY KEY) already exists, it gets overwritten: otherwise a new row 
    # is inserted. This is what makes re-runnining the pipeline safe - no
    # duplicate rows, no manual "check if it exists first" logic needed.
    query = f'INSERT OR REPLACE INTO indicators (date, {columns_sql}) VALUES ({placeholders})'

    # df.index holds the dates as datetime objects - convert each to a
    # plain "YYYY-MM-DD" string, matching the TEXT type used in the schema.
    # df.intertuples(index=False) walks through the DataFrame row by row,
    # yielding each row's values already in column order - much faster
    # than df.interrows() for this kind of bulk operation.
    rows = [
        (date.strftime("%Y-%m-%d"), *values) 
        for date, values in zip(df.index, df.itertuples(index=False))
    ]

    # executemany() rund the same query once per tuple in 'rows', as a 
    # single batch - far more efficient than looping and calling execute()
    # hundreads of time individually.
    conn.executemany(query, rows)
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

    print(f"Dados salvos em {DB_PATH}")