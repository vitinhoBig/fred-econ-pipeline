import os
import time
import yaml
import requests
from dotenv import load_dotenv

# carregar as variaveis do .env pro ambiente
load_dotenv()

# pegar o valor do FRED_API_KEY da variavel do ambiente
api_key = os.getenv("FRED_API_KEY")

BSE_URL = "https://api.stlouisfed.org/fred/series/observations"

def load_series_config(config_path="config/series.yaml"):
    # Abrir o arquivo, carregar o YAML e retornar a lista de series
    # yaml.safe_load(arquivo_aberto) retorn um dicit; a lista esta na chave "series"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
        return config["series"]

def fetch_series(series_id):
    # montar o dicionario do parametros
    # precisa de: series_id, api_key, file_type="json"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }

    # fazer a chamada GET usando requests, passando url e params
    response = requests.get(BSE_URL, params=params)

    # Verificar se a requisicao deu certo
    # dica: response.status_code == 200 ou response.raise_for_status()
    if response.status_code == 200:
        print(f"Successfully fetched data for series {series_id}")
    else:
        print(f"Failed to fetch data for series {series_id}. Status code: {response.status_code}")
        response.raise_for_status()

    # retornar o JSON decodificado da resposta
    return response.json()

if __name__ == "__main__":
    series_list = load_series_config()

    for series_id in series_list:
        print(f" Searching for {series_id}...")
        data = fetch_series(series_id)

        # Imprimir quantas observacoes vieram nessa serie
        # dica: len(data["observations"])
        print(f"Number of observations for {series_id}: {len(data['observations'])}")

        # Esperar um pouco antes da proxima chamada, pra respeitar o rate limit
        # dica: time.sleep(...)
        time.sleep(1)