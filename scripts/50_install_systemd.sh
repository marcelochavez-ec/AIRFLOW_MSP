#!/usr/bin/env bash
set -euo pipefail

sudo cp systemd/airflow-compose.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now airflow-compose.service
sudo systemctl status airflow-compose.service --no-pager
