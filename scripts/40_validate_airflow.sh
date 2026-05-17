#!/usr/bin/env bash
set -euo pipefail

cd /home/marcelo.chavez/airflow/deploy
docker compose ps
curl --fail http://127.0.0.1:8088/api/v2/monitor/health
docker compose exec airflow-api-server airflow db check
