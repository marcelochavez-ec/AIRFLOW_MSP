from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text, types

DATA_DIR = Path(__file__).parent / "data"
COUNTRY_DATA_PATH = Path(os.getenv("PCA_COUNTRY_DATA_PATH", DATA_DIR / "Country-data.csv"))
DICTIONARY_DATA_PATH = Path(
    os.getenv("PCA_DICTIONARY_DATA_PATH", DATA_DIR / "data-dictionary.csv")
)

POSTGRES_HOST = os.getenv("DBSTATS_HOST", "host.docker.internal")
POSTGRES_PORT = int(os.getenv("DBSTATS_PORT", "5432"))
POSTGRES_DB = os.getenv("DBSTATS_DB", "dbstats")
POSTGRES_USER = os.getenv("DBSTATS_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("DBSTATS_PASSWORD", "marce")

SCHEMA_NAME = "datasets"
TABLE_COUNTRY = "country_data"
TABLE_DICTIONARY = "country_data_dictionary"

# Mapeo de tablas con las estructuras:

COUNTRY_DTYPES = {
    "country": types.TEXT(),
    "child_mort": types.FLOAT(),
    "exports": types.FLOAT(),
    "health": types.FLOAT(),
    "imports": types.FLOAT(),
    "income": types.BIGINT(),
    "inflation": types.FLOAT(),
    "life_expec": types.FLOAT(),
    "total_fer": types.FLOAT(),
    "gdpp": types.BIGINT(),
}

DICTIONARY_DTYPES = {
    "column_name": types.TEXT(),
    "description": types.TEXT(),
}


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = (
        frame.columns.str.strip().str.lower().str.replace("-", "_").str.replace(" ", "_")
    )
    return frame


def _build_engine():
    return create_engine(
        "postgresql+psycopg2://"
        f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


def _validate_columns(frame: pd.DataFrame, expected: dict[str, types.TypeEngine], table_name: str) -> None:
    actual = list(frame.columns)
    expected_columns = list(expected)
    if actual != expected_columns:
        raise ValueError(
            f"Unexpected columns for {table_name}. Expected {expected_columns}, received {actual}."
        )


def load_country_datasets() -> dict[str, int]:
    df_country = _normalize_columns(pd.read_csv(COUNTRY_DATA_PATH))
    df_dictionary = _normalize_columns(pd.read_csv(DICTIONARY_DATA_PATH))

    _validate_columns(df_country, COUNTRY_DTYPES, TABLE_COUNTRY)
    _validate_columns(df_dictionary, DICTIONARY_DTYPES, TABLE_DICTIONARY)

    engine = _build_engine()

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};"))

    df_country.to_sql(
        name=TABLE_COUNTRY,
        con=engine,
        schema=SCHEMA_NAME,
        if_exists="replace",
        index=False,
        dtype=COUNTRY_DTYPES,
        method="multi",
        chunksize=1000,
    )

    df_dictionary.to_sql(
        name=TABLE_DICTIONARY,
        con=engine,
        schema=SCHEMA_NAME,
        if_exists="replace",
        index=False,
        dtype=DICTIONARY_DTYPES,
        method="multi",
        chunksize=1000,
    )

    with engine.connect() as conn:
        country_count = conn.execute(
            text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.{TABLE_COUNTRY};")
        ).scalar_one()
        dictionary_count = conn.execute(
            text(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.{TABLE_DICTIONARY};")
        ).scalar_one()

    return {
        TABLE_COUNTRY: country_count,
        TABLE_DICTIONARY: dictionary_count,
    }
