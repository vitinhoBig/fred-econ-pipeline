import os
import logging
import time
import schedule

from src.extract import load_series_config, fetch_series
from src.transform import clean_series, merge_series, fill_missing
from src.load import get_connection, create_table, upsert_data


#     configurar o loggin 
# dica: os.makedirs("logs", exist_ok=True) primeiro, pra garantir que a pasta existe
# dica: logging.basicConfig(
#           level=logging.INFO,
#           format="%(asctime)s [%(levelname)s] %(message)s",
#           handlers=[logging.FileHandler("logs/pipeline.log"), logging.StreamHandler()]
#       )
# (FileHandler grava no arquivo; StreamHandler tambem mostra no terminal, os dois ao mesmo tempo)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/pipeline.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Iniciando pipeline FRED...")

    # Envolver a logica do pipeline num try/except, logando erro se algo quebrar
    # dica: except Exception as e: logger.error(f"Pipeline falhou: {e}")
    try: 
        series_list = load_series_config()
        cleaned = [clean_series(fetch_series(sid), sid) for sid in series_list]
        final_df = merge_series(cleaned)
        final_df = fill_missing(final_df)

        conn = get_connection()
        create_table(conn, final_df.columns)
        upsert_data(conn, final_df)
        conn.close()

        logger.info(f"Pipeline concluido com sucesso. {final_df.shape[0]} linhas processadas.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


if __name__ == "__main__":
    # Agendar run_pipeline pra rodar periodicamente
    # PRA TESTAR AGORA (rapido, pra voce ver funcionado): schedule.every(10).seconds.do(run_pipeline)
    # PRA USO REAL (depois do confirmar que funciona): schedule.every().day.at("08:00").do(run_pipeline)
    schedule.every().day.at("08:00").do(run_pipeline)

    run_pipeline()  # roda uma vez imediatamente, sem esperar o primeiro agendamento

    # Loop que fica checando se alguma tarefa agendada esta pra rodar
    # dica: while: True: schedule.run_pending(); time.sleep(1)
    logger.info(f"Scheduler started. Wait for next scheduled runs...")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Scheduler interrupted by user. Shutting down")



        
    
    