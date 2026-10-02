import sqlite3
import pandas as pd

DB_PATH = "data/processed/fred_data.db"


def load_data(db_path=DB_PATH):
    # TODO 1: conectar no banco e ler a tabela "indicators" pra um DataFrame.
    # com "date" virando o indice, ja convertido pra datetime
    # dica: pd.read_sql("SELECT * FROM indicators", conn, parse_dates=["date"], index_col="date")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM indicators", conn, parse_dates=["date"], index_col="date")
    conn.close()
    return df 

def compute_pct_change(df, periods=1):
    # TODO 2: calcular a variacao percentual de cada coluna em relacao ao periodo anterior
    # dica: existe um metodo de pandas faz isso direto no DataFram inteiro
    return df.pct_change(periods=periods)

def compute_rolling_average(df, window=12):
    # TODO 3: calcular a media movel de 'window' periods
    # dica: eh o mesmo metodo que vc ja usou no treino-tracker
    return df.rolling(window=window).mean()

def compute_correlation(df):
    # TODO 4: calcular a matriz de correlacao entre todas as series
    # dica: tambem existe um metodo direto de pandas pra isso
    return df.corr()


if __name__ == "__main__":
    df = load_data()

    pct_change = compute_pct_change(df)
    rolling_avg = compute_rolling_average(df, window=12)
    corr = compute_correlation(df)

    print("Percentage variation (last 5 lines):")
    print(pct_change.tail())

    print("\n12-month moving average")
    print(rolling_avg.tail())

    print("\nCorrelation matrix")
    print(corr)