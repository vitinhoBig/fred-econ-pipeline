import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def load_data():
    # Criar o engine a partir da URL do .env
    # dica: create_engine(os.getenv("DATABASE_URL"))
    # SQLAlchemy precisa do driver explicito no formato dialeto+driver://
    db_url = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(db_url)

    # Ler a tabela "indicators" ORDENADA POR DATA, com "date" como índice
    # dica: pd.read_sql("SELECT * FROM indicators ORDER BY date", engine, parse_dates=["date"], index_col="date")
    df = pd.read_sql("SELECT * FROM indicators ORDER BY date", engine, parse_dates=["date"], index_col="date")

    return df

def compute_pct_change(df, periods=1):
    # Calcular a variacao percentual de cada coluna em relacao ao periodo anterior
    # dica: existe um metodo de pandas faz isso direto no DataFram inteiro
    return df.pct_change(periods=periods)

def compute_rolling_average(df, window=12):
    # Calcular a media movel de 'window' periods
    # dica: eh o mesmo metodo que vc ja usou no treino-tracker
    return df.rolling(window=window).mean()

def compute_correlation(df):
    # Calcular a matriz de correlacao entre todas as series
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