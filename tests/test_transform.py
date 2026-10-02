import pandas as pd
from src.transform import clean_series, merge_series, fill_missing


def make_fake_raw_json(dates_values):
    """Monta um JSON falso, no formato que a FRED retornaria, a partir de (data, valor)."""
    return {
        "observations": [
            {"date": date, "value": value} for date, value in dates_values
        ]
    }


def test_clean_series_converts_missing_value_to_nan():
    raw = make_fake_raw_json([
        ("2020-01-01", "5.0"),
        ("2020-02-01", "."),      # missing value, should become NaN
    ])

    df = clean_series(raw, "TEST")

    assert pd.isna(df.loc["2020-02-01", "TEST"])


def test_clean_series_renames_column_to_series_id():
    raw = make_fake_raw_json([("2020-01-01", "5.0")])
    df = clean_series(raw, "UNRATE")

    assert "UNRATE" in df.columns


def test_merge_series_aligns_by_date():
    df_a = clean_series(make_fake_raw_json([("2020-01-01", "1.0"), ("2020-02-01", "2.0")]), "A")
    df_b = clean_series(make_fake_raw_json([("2020-01-01", "10.0")]), "B")

    merged = merge_series([df_a, df_b])

    assert merged.shape[0] == 2
    assert pd.isna(merged.loc["2020-02-01", "B"])


def test_fill_missing_propagates_last_known_value():
    df = pd.DataFrame(
        {"X": [1.0, None, None, 4.0]},
        index=pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"]),
    )

    filled = fill_missing(df)

    assert filled.iloc[1]["X"] == 1.0


def test_fill_missing_propagates_across_multiple_columns():
    df = pd.DataFrame(
        {"X": [1.0, None, None, 4.0]},
        index=pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"]),
    )
    filled = fill_missing(df)

    assert filled.iloc[2]["X"] == 1.0


def test_fill_missing_keeps_leading_nan():
    df = pd.DataFrame(
        {"X": [None, 2.0, None]},
        index=pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01"]),
    )

    filled = fill_missing(df)

    # verify that position 0 is still NaN (no value to propagete forward)
    assert pd.isna(filled.iloc[0]["X"])

