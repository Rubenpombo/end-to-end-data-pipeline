# Ciclo de Vida de Streaming de Datos End-to-End (Edición 2026)

📄 English version available in [README.md](README.md)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Rubenpombo_end-to-end-data-pipeline&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Rubenpombo_end-to-end-data-pipeline)
[![CI Pipeline](https://github.com/Rubenpombo/end-to-end-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Rubenpombo/end-to-end-data-pipeline/actions/workflows/ci.yml)

## **Resumen**
Este proyecto demuestra una arquitectura profesional de pipeline de datos en tiempo real actualizada a los **estándares de 2026**. Captura datos de usuarios de una API externa, los transmite a través de **Apache Kafka**, los procesa con **Apache Spark Streaming** y almacena los resultados en **Apache Cassandra**.

Todo el stack está contenedorizado con **Docker**, orquestado por **Apache Airflow 3.x**, y cuenta con una capa moderna de observabilidad con **Kafka UI**, **Prometheus** y **Grafana**.

<p align="center">
  <img src="visuals/dashboard-preview.gif" alt="Vista previa del Dashboard" width="600">
</p>

## **Arquitectura y Tecnologías**

### **Core Data Stack**
- **Apache Airflow 3.1.7**: Orquestación del pipeline e ingesta de datos desde la API RandomUser.
- **Apache Kafka 7.9 (Confluent)**: Sistema de mensajería distribuida de alto rendimiento.
- **Apache Spark 4.0.2**: Procesamiento de streaming y transformación de datos en tiempo real.
- **Apache Cassandra 5.0**: Base de datos NoSQL distribuida para el almacenamiento final.

### **Observabilidad y Calidad**
- **Kafka UI**: Gestión visual de tópicos, consumidores y mensajes ([localhost:8000](http://localhost:8000)).
- **Prometheus y Grafana**: Recolección de métricas del sistema y dashboards visuales ([localhost:3000](http://localhost:3000)).
- **SonarCloud**: Análisis continuo de calidad de código y seguridad.
- **GitHub Actions**: Pipeline de CI/CD automatizado con linting (Ruff) y Pytest.

## **Guía de Ejecución**

1. **Iniciar la Infraestructura**:
   ```bash
   docker-compose up -d
   ```

2. **Verificar el Estado de los Servicios**:
   Espera unos segundos a que todos los servicios estén saludables. Puedes comprobarlo con:
   ```bash
   docker-compose ps
   ```

3. **Ejecutar Tests Automatizados**:
   ```bash
   python3 -m unittest discover -s tests
   ```

4. **Activar la Ingesta de Datos (Airflow)**:
   - Accede a Airflow en [http://localhost:8080](http://localhost:8080).
   - Activa el DAG `user_automation`.
   - Monitoriza los mensajes entrantes en **Kafka UI**: [http://localhost:8000](http://localhost:8000).

5. **Iniciar Spark Streaming**:
   ```bash
   # Asegúrate de tener las dependencias instaladas
   pip install -r requirements.txt
   export CASSANDRA_HOST=localhost
   export KAFKA_HOST=localhost:9092
   python3 spark_stream.py
   ```

6. **Visualizar Datos**:
   - **Métricas de Sistema (Grafana)**: Visita [http://localhost:3000](http://localhost:3000) (Usuario: `admin` / Clave: `admin`).

## **Estructura del Proyecto**
   ```bash
.
├── .github/workflows/         # Pipeline de CI/CD (GitHub Actions)
├── dags/                      # DAGs de Airflow (Lógica de ingesta)
├── script/                    # Entrypoints de Docker
├── tests/                     # Tests unitarios y de integración
├── docker-compose.yml         # Orquestación de contenedores (Full Stack)
├── Dockerfile-spark           # Imagen personalizada de Spark 4.x
├── prometheus.yml             # Configuración de recolección de métricas
├── grafana_datasource.yml     # Configuración automática de Grafana
├── requirements.txt           # Dependencias consolidadas
└── spark_stream.py            # Lógica de streaming Spark 4.x
```
