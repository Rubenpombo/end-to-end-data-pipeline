# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [Unreleased] — 2026-08

### Añadido

- **Tests unitarios del DAG con mocks**: `tests/test_kafka_stream.py` cubre `get_data()` y `format_data()` sin llamadas HTTP reales ni Airflow instalado (módulos stubbed).
- **Tests Spark ampliados al schema completo**: verifican todas las columnas del contrato, la serialización de `address` como string JSON y la columna de linaje `ingested_at`.
- **Marcadores de pytest** (`unit` / `integration`) en `pytest.ini`; CI ejecuta solo el subset unitario (`pytest -m "not integration"`).
- **`.env.example`** con `KAFKA_HOST`, `CASSANDRA_HOST`, `SPARK_MASTER_URL`, `CHECKPOINT_DIR` y credenciales demo documentadas.
- **`Makefile`** como punto de entrada único: `up`, `down`, `build`, `ps`, `logs`, `test`, `test-integration`, `lint`, `stream-local`.
- **Diagrama de arquitectura Mermaid** en README (EN/ES): API → Airflow → Kafka → Spark → Cassandra + capa de observabilidad.
- **Dashboard Grafana provisionado** (*Pipeline Overview*: targets `up`, latencia de scrapeo) con provider en `grafana/` y `uid` estable para el datasource Prometheus.
- **Servicio `spark-streaming` en Docker Compose**: el job corre con `spark-submit` contra `spark-master`, con `KAFKA_HOST`/`CASSANDRA_HOST`/`SPARK_MASTER_URL`/`CHECKPOINT_DIR` por entorno. La ejecución en host sigue disponible vía `make stream-local`.
- **Sección "Demo rápida (5 minutos)"** al inicio del README (EN/ES) con requisitos, comandos y verificación en Airflow, Kafka UI y Grafana.
- **Columna `ingested_at TIMESTAMP`** en Cassandra, establecida por Spark en tiempo de procesamiento (linaje).
- **Sección de modelado Cassandra** en README (EN/ES): PK, particionado, linaje y patrones de acceso soportados vs fuera de alcance.
- **Resiliencia del DAG**: `retries`, `retry_delay`, `execution_timeout` y `doc_md` que documenta el modelo de streaming acotado (ventana de 120 s por ejecución) y su relación con el schedule diario.
- **`kafka-exporter`**: Prometheus raspa `prometheus`, Grafana (`/metrics`) y `kafka-exporter:9308` (`danielqsj/kafka-exporter:v1.9.0`). El puerto JMX `:9101` queda solo para Kafka UI — rasparlo dejaba `up=0` en el dashboard.

### Cambiado

- **Dependencias de los contenedores Airflow reducidas al mínimo**: nuevo `requirements-airflow.txt` (`requests`, `kafka-python-ng`) montado en `webserver` y `scheduler` en lugar del `requirements.txt` completo — se acabó instalar `pyspark`, `pytest`, `ruff`, etc. en cada arranque.
- **Entrypoint de Airflow corregido**: eliminada la comprobación de `airflow.db` (SQLite) que no aplicaba al usar Postgres y reejecutaba `db init` + `users create` en cada arranque; ahora `db migrate` + `users create` idempotente.
- **Contrato de datos unificado para `address`**: viaja anidado en Kafka, Spark lo parsea con el struct completo y lo serializa con `to_json()` para la columna `address TEXT` de Cassandra. Documentado en README (EN/ES).
- **Imágenes Docker pinneadas** (ninguna usa `:latest`): `prom/prometheus:v3.13.2` (LTS), `grafana/grafana:13.0.6`, `provectuslabs/kafka-ui:v0.7.2`, `apache/spark:4.0.2-scala2.13-java17-python3-r-ubuntu` (alineado con `pyspark==4.0.2`).
- **Comando canónico de tests**: pytest en README (EN/ES), CI y Makefile.
- **Metadatos del DAG**: owner actualizado a `rubenpombo`, con descripción y tags.
- **Dependencias Python pinneadas**: `requirements.txt` y `requirements-airflow.txt` fijan versiones exactas (misma política que las imágenes Docker).
- **Fail-fast en `spark_stream.py`**: si la sesión de Spark, el stream de Kafka o la conexión a Cassandra fallan, el proceso sale con código 1 en lugar de terminar silenciosamente con éxito (permite que `restart: on-failure` actúe).
- **Límites de logs en todos los servicios**: anchor YAML `x-logging` (`max-size: 10m`, `max-file: 3`) aplicado a los 11 servicios; antes solo `webserver` y `postgres` lo tenían.
- **Volumen `spark_checkpoints`** movido al servicio `spark-streaming` (el que escribe checkpoints).
- **`.gitignore` ampliado**: bytecode, caches de pytest/ruff/mypy, coverage, `.env`, ruido de SO/editor.

### Eliminado

- **Servicio Schema Registry**: desplegado pero nunca integrado (mensajes JSON plano, esquema validado por tests); eliminado del stack junto a sus referencias en broker y Kafka UI. Ahorra ~0,5–1 GB de RAM en el arranque.
- **Dependencias sin uso** en `requirements.txt`: `statsmodels`, `pandas`, `numpy`.
- **Código muerto**: función `insert_data()` (~35 líneas no invocadas) en `spark_stream.py` y `BashOperator` comentado con ruta absoluta ajena al repo en el DAG.
- **Artefactos versionados que no deberían estarlo**: `__pycache__/`, `.coverage`, `coverage.xml` (ahora se genera en CI, no se commitea).
- Clave obsoleta `version: '3.8'` de `docker-compose.yml`.
- **Capturas de UIs y stacks antiguos** (`visuals/`): dashboard Flask, Confluent Control Center y `docker-compose ps` con Zookeeper/Schema Registry.

## [2026-08] — Limpieza arquitectónica

### Cambiado

- **Migración a Kafka KRaft**: Zookeeper eliminado del stack.
- **Actualización de imágenes a versiones 2026** con compatibilidad para Airflow 3.x y Spark 4.x.

### Eliminado

- **Flask y dashboard custom**: referencias purgadas de código y documentación; la visualización queda cubierta por Kafka UI + Grafana.
