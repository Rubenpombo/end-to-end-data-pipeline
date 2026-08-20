# Roadmap de Mejoras — End-to-End Data Pipeline

Documento de referencia con las mejoras **pendientes** del proyecto.
Los cambios ya completados se han movido a [`CHANGELOG.md`](CHANGELOG.md).

## Contexto del proyecto

Side project orientado a demostrar habilidades de **Data Engineer graduado**. Arquitectura de streaming en tiempo real:

```
RandomUser API → Apache Airflow → Apache Kafka → Apache Spark Streaming → Apache Cassandra
```

Capas auxiliares: Kafka UI, Prometheus, Grafana.
Stack containerizado con Docker Compose, CI en GitHub Actions (Ruff, yamllint, pytest, SonarCloud), README bilingüe (EN/ES).

**Criterio de permanencia en este documento:** mejoras de bajo esfuerzo y valor claro para un side project. Lo que implica over-engineering está en el registro de descartados más abajo.

---

## Pendientes

### 1. Documentar semántica de entrega

**Contexto actual**

- Productor Kafka sin configuración explícita de idempotencia/acks; consumidor Spark con `startingOffsets='earliest'` y checkpoint.
- Sin deduplicación por `id` UUID.

**Recomendación**

- Documentar en el README la semántica asumida (at-least-once implícita) y por qué es suficiente para el demo. Sin DLQ ni exactly-once: fuera de alcance para un side project.

---

### 2. Consistencia SonarCloud / cobertura

**Contexto actual**

- `sonar.exclusions` en `sonar-project.properties` vs argumentos del workflow CI pueden diferir.
- `sonar.qualitygate.wait=false` — Sonar no actúa como gatekeeper.

**Recomendación**

- Unificar configuración Sonar entre `sonar-project.properties` y el workflow CI.
- Asegurar que coverage se genera en CI y no se commitea (ya resuelto en `.gitignore`).

---

## Descartado por over-engineering (registro)

Para evitar re-proponerlos, se listan los ítems evaluados y descartados por no aportar valor proporcional a un side project de portfolio:

- **Schema Registry con Avro/JSON Schema** — el contrato JSON documentado + tests de schema cubren la necesidad.
- **Job de CI con smoke test de integración** levantando Docker Compose — coste de minutos de CI y flakiness altos para el valor que aporta aquí.
- **Observabilidad ampliada** (exporters de Spark/Airflow, alertas, trazas) — la capa actual (Kafka UI + Prometheus + Grafana con dashboard provisionado) es suficiente para la demo.
- **DLQ, deduplicación y exactly-once** — se documenta la semántica asumida (ítem 1) en lugar de implementar mecanismos.
- **Eliminar el campo `password` del contrato** — son hashes ficticios de una API pública de datos sintéticos; no hay riesgo real que mitigar.
- **Licencia, CONTRIBUTING, templates de issues/PR** — burocracia sin sentido para un side project personal.

---

## Inventario de activos existentes (referencia)

| Recurso | Estado |
|---------|--------|
| `dags/kafka_stream.py` | Ingesta API → Kafka |
| `spark_stream.py` | Consumo Kafka → Cassandra |
| `docker-compose.yml` | 11 servicios, red `confluent` |
| `tests/` | 5 módulos de test (unitarios + integración) |
| `.github/workflows/ci.yml` | Lint + tests unitarios + Sonar |
| `grafana/` | Dashboards provisionados |
| `sonar-project.properties` | Análisis estático configurado |

---

*Actualizado en agosto 2026: los cambios completados se movieron a `CHANGELOG.md`.*
