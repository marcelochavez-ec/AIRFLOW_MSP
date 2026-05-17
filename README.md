<p align="center">
  <img src="img/LOGO_MSP.png" alt="Ministerio de Salud Publica" width="520">
</p>

# DNEAISNS Airflow Stack

Implementacion de Apache Airflow 3.2.1 para la orquestacion de flujos de datos de la Direccion Nacional de Estadistica y Analisis de la Informacion del Sistema Nacional de Salud.

La solucion usa contenedores Docker, PostgreSQL externo para la metadata de Airflow y una base PostgreSQL adicional para datasets analiticos. Incluye personalizacion visual institucional, un DAG de ejemplo de una sola ejecucion y scripts de preparacion para despliegue en AlmaLinux.

## Resumen funcional

- Orquestador: Apache Airflow 3.2.1 sobre imagen `apache/airflow:3.2.1-python3.14`
- Ejecutor: `LocalExecutor`
- Puerto web publicado: `8088`
- Zona horaria: `America/Guayaquil`
- Metadata de Airflow:
  - base: `productos_bm`
  - schema: `airflow_db`
- Datasets analiticos:
  - base: `dbstats`
  - schema: `datasets`
- Login inicial:
  - usuario: `admin`
  - contrasena: `marce`
- DAG incluido:
  - `pca_country_dataset_once`
  - ejecucion unica con `schedule="@once"`
  - carga `country_data` y `country_data_dictionary`

## Arquitectura

Servicios principales definidos en `docker-compose.yml`:

- `airflow-permissions-init`
  - prepara permisos de los volumenes montados
- `airflow-init`
  - crea el schema remoto de metadata si no existe
  - genera el archivo de contrasenas del Simple auth manager
  - ejecuta migraciones de Airflow
- `airflow-api-server`
  - expone la interfaz web y la API
- `airflow-scheduler`
  - agenda y despacha tareas
- `airflow-dag-processor`
  - parsea y serializa DAGs
- `airflow-triggerer`
  - procesa triggers asincronos

El `LocalExecutor` necesita que los procesos ejecutores alcancen la API de ejecucion de Airflow 3. Por eso se configura:

```text
AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/
```

Esto permite que las tareas ejecutadas desde el scheduler se comuniquen correctamente con el API server dentro de la red de Docker.

## Estructura del proyecto

```text
docker_files/
|-- .env
|-- docker-compose.yml
|-- Makefile
|-- README.md
|-- config/
|   |-- airflow-ui/
|   |   |-- custom-title.js
|   |   |-- index.html
|   |   `-- i18n/locales/es/dashboard.json
|   |-- simple-auth-login/
|   |   |-- custom-login.js
|   |   `-- index.html
|   `-- simple_auth_manager_passwords.json
|-- dags/
|   |-- pca_country_dataset_once.py
|   `-- testing/
|       |-- __init__.py
|       |-- test_pca_01.py
|       `-- data/
|           |-- Country-data.csv
|           `-- data-dictionary.csv
|-- img/
|   `-- LOGO_MSP.png
|-- logs/
|-- plugins/
|-- scripts/
|   |-- 00_prepare_host.sh
|   |-- 10_install_docker.sh
|   |-- 20_generate_fernet_key.sh
|   |-- 30_init_airflow.sh
|   |-- 40_validate_airflow.sh
|   `-- 50_install_systemd.sh
`-- systemd/
    `-- airflow-compose.service
```

## Variables de entorno

Archivo principal: `.env`

### Airflow

```text
AIRFLOW_IMAGE_NAME=apache/airflow:3.2.1-python3.14
AIRFLOW_HOME=/home/marcelo.chavez/airflow
AIRFLOW_UID=50000
AIRFLOW_API_PORT=8088
TZ=America/Guayaquil
```

### Volumenes locales de desarrollo

```text
AIRFLOW_DAGS_DIR=./dags
AIRFLOW_LOGS_DIR=./logs
AIRFLOW_PLUGINS_DIR=./plugins
AIRFLOW_CONFIG_DIR=./config
```

En esta estacion de trabajo se usan rutas relativas para que Docker monte las carpetas reales del repositorio. Para un despliegue en AlmaLinux se pueden reemplazar por rutas absolutas del host, por ejemplo:

```text
/home/marcelo.chavez/airflow/dags
/home/marcelo.chavez/airflow/logs
/home/marcelo.chavez/airflow/plugins
/home/marcelo.chavez/airflow/config
```

### PostgreSQL de metadata de Airflow

```text
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=productos_bm
POSTGRES_SCHEMA=airflow_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=marce
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:marce@host.docker.internal:5432/productos_bm?options=-csearch_path%3Dairflow_db
```

La metadata de Airflow queda en:

```text
productos_bm.airflow_db
```

Durante `airflow-init` se crea `airflow_db` si no existe y luego se ejecutan las migraciones.

### PostgreSQL de datasets analiticos

```text
DBSTATS_HOST=host.docker.internal
DBSTATS_PORT=5432
DBSTATS_DB=dbstats
DBSTATS_USER=postgres
DBSTATS_PASSWORD=marce
```

El DAG de ejemplo escribe en:

```text
dbstats.datasets
```

### Autenticacion inicial

```text
AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS=admin:admin
AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE=/home/marcelo.chavez/airflow/config/simple_auth_manager_passwords.json
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=marce
```

Airflow 3 usa por defecto el Simple auth manager en despliegues de tipo desarrollo/prueba. El archivo de contrasenas se genera automaticamente durante `airflow-init`.

## Diferencia entre desarrollo local y despliegue real

### Desarrollo local con Docker Desktop

En esta maquina los contenedores alcanzan PostgreSQL del host mediante:

```text
host.docker.internal
```

### Servidor AlmaLinux

En el servidor final se debe reemplazar `host.docker.internal` por la IP o nombre DNS real del servidor PostgreSQL accesible desde Docker.

Tambien se deben revisar:

- puertos abiertos
- reglas de `pg_hba.conf`
- `listen_addresses` de PostgreSQL
- firewall del servidor de base de datos
- permisos del usuario `postgres`

## Instalacion en AlmaLinux

1. Copiar este repositorio a:

```bash
/home/marcelo.chavez/airflow/deploy
```

2. Dar permisos de ejecucion a los scripts:

```bash
chmod +x scripts/*.sh
```

3. Preparar el host:

```bash
./scripts/00_prepare_host.sh
```

4. Instalar Docker:

```bash
./scripts/10_install_docker.sh
```

5. Si se desea rotar la clave Fernet antes del primer arranque:

```bash
./scripts/20_generate_fernet_key.sh
```

6. Instalar y habilitar el servicio `systemd`:

```bash
./scripts/50_install_systemd.sh
```

7. Inicializar y levantar Airflow:

```bash
./scripts/30_init_airflow.sh
```

8. Validar el despliegue:

```bash
./scripts/40_validate_airflow.sh
```

9. Abrir la interfaz:

```text
http://SERVER_IP:8088
```

## Acceso SSH preparado por los scripts

Los scripts de preparacion crean acceso SSH para:

```text
usuario: admin
contrasena: marce
```

Ejemplo:

```bash
ssh admin@SERVER_IP
```

El servicio SSH corre en el host AlmaLinux, no dentro de los contenedores.

## Personalizacion visual de la interfaz

### Login institucional

Archivos:

- `config/simple-auth-login/index.html`
- `config/simple-auth-login/custom-login.js`
- `img/LOGO_MSP.png`

Cambios aplicados:

- titulo de pestana: `DNEAISNS`
- ocultamiento del aviso del Simple auth manager
- incorporacion del logo institucional MSP
- texto institucional:

```text
Direccion Nacional de Estadistica y
Analisis de la Informacion del
Sistema Nacional de Salud
```

- texto secundario:

```text
Sign into Airflow
```

### UI principal

Archivos:

- `config/airflow-ui/index.html`
- `config/airflow-ui/custom-title.js`
- `config/airflow-ui/i18n/locales/es/dashboard.json`

Cambios aplicados:

- titulo persistente de la pestana: `DNEAISNS`
- reemplazo del encabezado visible del dashboard por:

```text
Bienvenido al orquestador de flujos de datos de la DNEAISNS
```

## DAG de carga de datasets PCA

### Archivos

- DAG:
  - `dags/pca_country_dataset_once.py`
- Logica ETL:
  - `dags/testing/test_pca_01.py`
- Datos fuente:
  - `dags/testing/data/Country-data.csv`
  - `dags/testing/data/data-dictionary.csv`

### Funcionamiento

El DAG:

1. lee los CSV locales versionados en el proyecto;
2. normaliza nombres de columnas;
3. valida que las columnas recibidas coincidan con el esquema esperado;
4. crea el schema `datasets` si no existe;
5. reemplaza y carga:
   - `datasets.country_data`
   - `datasets.country_data_dictionary`
6. devuelve el conteo de filas cargadas.

### Mapeo de columnas

`datasets.country_data`

| Columna | Tipo PostgreSQL |
| --- | --- |
| `country` | `text` |
| `child_mort` | `double precision` |
| `exports` | `double precision` |
| `health` | `double precision` |
| `imports` | `double precision` |
| `income` | `bigint` |
| `inflation` | `double precision` |
| `life_expec` | `double precision` |
| `total_fer` | `double precision` |
| `gdpp` | `bigint` |

`datasets.country_data_dictionary`

| Columna | Tipo PostgreSQL |
| --- | --- |
| `column_name` | `text` |
| `description` | `text` |

### Validacion realizada

La prueba final ejecutada dejo:

```text
datasets.country_data: 167 filas
datasets.country_data_dictionary: 10 filas
```

La ejecucion manual valida del DAG termino en `success`.

Ejemplos comprobados:

```text
Afghanistan, 1610, 553
Albania, 9930, 4090
Algeria, 12900, 4460
```

## Comandos operativos utiles

### Estado del stack

```bash
docker compose ps
```

### Logs

```bash
docker compose logs -f airflow-api-server
docker compose logs -f airflow-scheduler
docker compose logs -f airflow-dag-processor
docker compose logs -f airflow-triggerer
```

### Reinicio

```bash
docker compose restart
```

### Validacion de salud

```bash
curl --fail http://127.0.0.1:8088/api/v2/monitor/health
docker compose exec airflow-api-server airflow db check
```

### DAGs

```bash
docker compose exec airflow-api-server airflow dags list
docker compose exec airflow-api-server airflow dags list-import-errors
docker compose exec airflow-api-server airflow dags trigger pca_country_dataset_once
```

### Servicio systemd

```bash
sudo systemctl restart airflow-compose.service
sudo systemctl status airflow-compose.service
```

## Recomendaciones de seguridad

- Rotar antes de produccion:
  - `admin / marce`
  - `root / marce`
  - contrasena de PostgreSQL
  - clave Fernet
- No exponer la interfaz de Airflow directamente a Internet sin autenticacion, proxy inverso y TLS.
- Mantener SELinux habilitado.
- Revisar permisos de los volumenes montados.
- Restringir el acceso a PostgreSQL por red y por `pg_hba.conf`.
- Para un despliegue productivo mayor, evaluar una arquitectura mas robusta que un unico host con `LocalExecutor`.

## Notas tecnicas

- Los bind mounts usan sufijo `:z` para compatibilidad con SELinux.
- `airflow-permissions-init` ejecuta como `root` solo para preparar permisos; los servicios normales corren como UID `50000`.
- `airflow-init` usa `psycopg2`, porque la imagen actual trae ese driver disponible.
- El esquema de metadata se controla mediante `search_path=airflow_db`.
- La UI principal y el login se personalizan mediante archivos montados sobre los assets estaticos de la imagen.
- Si se cambia la UI y el navegador no refleja el resultado, usar recarga fuerte:

```text
Ctrl + F5
```

## Derechos de autor

```text
Derechos de autor: Marcelo Chávez
Consultor Estadístico
Email: marcelo_chavez_ec@outlook.com
```
