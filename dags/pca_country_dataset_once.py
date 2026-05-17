from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, task

from testing.test_pca_01 import load_country_datasets


@dag(
    dag_id="pca_country_dataset_once",
    schedule="@once",
    start_date=datetime(2026, 5, 16),
    catchup=False,
    tags=["datasets", "pca", "one_time"],
)
def pca_country_dataset_once():
    @task
    def load_dataset():
        return load_country_datasets()

    load_dataset()


pca_country_dataset_once()
