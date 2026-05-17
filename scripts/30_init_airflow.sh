#!/usr/bin/env bash
set -euo pipefail

cd /home/marcelo.chavez/airflow/deploy
docker compose pull
docker compose up airflow-init
docker compose up -d
docker compose ps
