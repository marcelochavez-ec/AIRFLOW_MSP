# Airflow 3.2.1 on AlmaLinux 10.1

This deployment targets AlmaLinux OS 10.1, Airflow 3.2.1, Python 3.14 images, Docker Engine, Docker Compose Plugin, and an external PostgreSQL database.

## Architecture

Primary stack:

- `airflow-api-server`
- `airflow-scheduler`
- `airflow-dag-processor`
- `airflow-triggerer`
- `airflow-permissions-init`
- `airflow-init`

The stack uses `LocalExecutor`, which is the simpler single-server architecture for getting started with Airflow.

## Folder layout on AlmaLinux

```text
/home/marcelo.chavez/airflow/
|-- config/
|-- dags/
|-- logs/
|-- plugins/
`-- deploy/
    |-- .env
    |-- docker-compose.yml
    |-- scripts/
    `-- systemd/
```

## Install sequence

1. Copy this repository into `/home/marcelo.chavez/airflow/deploy`.
2. Run:

```bash
chmod +x scripts/*.sh
./scripts/00_prepare_host.sh
./scripts/10_install_docker.sh
```

3. A Fernet key is already present in `.env`. To rotate it before first deployment, generate a new one with:

```bash
./scripts/20_generate_fernet_key.sh
```

4. Install and enable the systemd unit:

```bash
./scripts/50_install_systemd.sh
```

5. Initialize and start Airflow:

```bash
./scripts/30_init_airflow.sh
./scripts/40_validate_airflow.sh
```

6. Open the UI:

```text
http://SERVER_IP:8088
```

Initial login:

```text
username: admin
password: marce
```

Airflow 3 uses the Simple auth manager by default for development-style deployments, so the `admin / marce` login is configured through `AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS` and `config/simple_auth_manager_passwords.json`.

## SSH access

The AlmaLinux host enables `sshd`, opens `22/tcp` in `firewalld`, and allows password login for:

```text
username: admin
password: marce
```

Example:

```bash
ssh admin@SERVER_IP
```

SSH is configured on the AlmaLinux host, not inside the Airflow containers.

## External PostgreSQL

Configured target:

```text
host: host.docker.internal
port: 5432
database: productos_bm
schema: airflow_db
user: postgres
password: marce
```

Airflow connects directly to the external PostgreSQL server. During `airflow-init`, the Airflow container creates the remote schema `productos_bm.airflow_db` if it does not already exist, and then runs the Airflow migrations there. The SQLAlchemy URL also forces `search_path=airflow_db`.

For local Docker Desktop testing on this machine, `host.docker.internal` is the reachable address from the containers. On the AlmaLinux server, replace it with the real PostgreSQL host address before deploying there.

Airflow 3.2.1 is officially tested with PostgreSQL 13 through 17. If the external server is PostgreSQL 18, treat that as outside the tested support matrix and prefer PostgreSQL 17 for a production deployment.

## Operational commands

```bash
docker compose ps
docker compose logs -f airflow-api-server
docker compose restart
docker compose pull
docker compose up -d
sudo systemctl restart airflow-compose.service
sudo systemctl status airflow-compose.service
```

## Notes

- Keep SELinux enabled. Bind mounts use `:z`, and the host preparation script labels `/home/marcelo.chavez/airflow` with `container_file_t`.
- `airflow-api-server`, `airflow-scheduler`, `airflow-dag-processor`, and `airflow-triggerer` are kept persistent by two layers: container-level `restart: unless-stopped` and host-level `airflow-compose.service` enabled at boot through `systemd`.
- `admin / marce` and `root / marce` are implemented because they were requested, but they are weak production credentials and should be rotated before exposing the server.
- The compose stack is suitable for light production use, but the Airflow project recommends Kubernetes with the official Helm chart for larger production deployments.
