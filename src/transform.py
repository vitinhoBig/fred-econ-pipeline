import pandas as pd


def clean_series(raw_json, series_id):
    # extrair a lista de observacoes do JSON bruto
    observations = raw_json["observations"]

    # criar um DataFrame a partir da lista, mantendo so as colunas "date" e "value"
    # dica: pd.DataFrame(observations)[["date", "value"]]
    df = pd.DataFrame(observations)[["date", "value"]]

    # converter a coluna "date" pra datetime
    # dica: pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"])

    # os valores ausentes vem como string "." - trocar por NaN e converter a coluna pra float
    # dica: df["value"].replace(".", pd.NA) ... depois .astype(float)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # renomer "value" pro nome de serie, e usar "date" como indice
    df = df.rename(columns={"value": series_id})
    df = df.set_index("date")

    return df[[series_id]]

def merge_series(series_list):
    # dataframes: lista de DataFrames ja limpos (um por serie), todos indexados por date
    # juntar tudo numa unica tabela, alinhado pela data
    # dica: pd.concat(dataframes, axis=1, join="outer")
    merged = pd.concat(series_list, axis=1, join="outer")
    return merged

def fill_missing(merged_df):
    # TODO: propagar o ultimo valor conhecido pra frente, preenchendo os gaps
    # dica: existe um metodo do pandas que faz exatamente isso, chamado "forward fill"
    filled = merged_df.ffill()
    return filled

if __name__ == "__main__":
    from extract import load_series_config, fetch_series

    series_list = load_series_config()
    cleaned = [clean_series(fetch_series(sid), sid) for sid in series_list]

    final_df = merge_series(cleaned)
    final_df = fill_missing(final_df)
    print(final_df.head())
    print(final_df.tail())
    print(f"Shape: {final_df.shape}")

