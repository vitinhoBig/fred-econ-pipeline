import pandas as pd
from src.analyze import to_quarterly


def make_monthly_df():
    # 9 months = 3 quarters: (1,2,3), (4,5,6), (7,8,9)
    return pd.DataFrame(
        {"X": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]},
        index=pd.date_range("2020-01-01", periods=9, freq="MS"),
    )


def test_to_quarterly_averages_each_quarter():
    quarterly = to_quarterly(make_monthly_df())

    # Verificar que sobraram 2 linhas (o último trimestre é removido)
    assert len(quarterly) == 2

    # Verificar que a média do primeiro trimestre (1, 2, 3) é 2.0
    assert quarterly.iloc[0]["X"] == 2.0


def test_to_quarterly_drops_last_quarter():
    quarterly = to_quarterly(make_monthly_df())

    # Verificar que o trimestre que começa em 2020-07-01 não está no índice
    # dica: pd.Timestamp("2020-07-01") not in quarterly.index
    assert pd.Timestamp("2020-07-01") not in quarterly.index