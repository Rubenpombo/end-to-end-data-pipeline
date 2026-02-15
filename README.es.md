# Ciclo de Vida Completo de Streaming de Datos

## **Resumen**
Este proyecto demuestra el ciclo de vida completo del streaming de datos, desde la ingesta hasta la visualización. Captura datos de usuario desde una API externa, los procesa en tiempo real utilizando **Apache Kafka** y **Apache Spark**, los almacena en una base de datos **Cassandra** y los visualiza a través de un dashboard interactivo construido con **Flask** y **Plotly**. El pipeline está orquestado con **Apache Airflow**, garantizando automatización y confiabilidad.

<p align="center">
  <img src="visuals/dashboard-preview.gif" alt="Dashboard Preview" width="600">
</p>

El objetivo de este proyecto es mostrar mi capacidad para diseñar, desarrollar y mantener pipelines de datos, al mismo tiempo que proporciono visualizaciones claras e impactantes para la toma de decisiones.

## **Tecnologías Usadas**
- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/docker/docker-original.svg" width="25" height="25" /> **Docker Compose**: Gestiona el despliegue de todos los servicios en contenedores aislados para una configuración y escalabilidad sencillas.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apacheairflow/apacheairflow-original.svg" width="25" height="25" /> **Apache Airflow**: Orquesta todo el pipeline, automatizando la ejecución de tareas.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachekafka/apachekafka-original.svg" width="25" height="25" /> **Apache Kafka**: Utilizado para la ingesta y transmisión de datos en tiempo real.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachespark/apachespark-original.svg" width="25" height="25" /> **Apache Spark**: Procesa los datos en tiempo real, transformándolos y estructurándolos para su almacenamiento.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/cassandra/cassandra-original.svg" width="25" height="25" /> **Cassandra**: Sirve como capa de almacenamiento para los datos procesados, aprovechando sus capacidades NoSQL distribuidas.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/grafana/grafana-original.svg" width="25" height="25" /> **Grafana**: Proporciona un dashboard potente e interactivo para visualizar datos en tiempo real almacenados en Cassandra.



## Automatización con Make

Para simplificar el proceso de ejecución, puedes usar el `Makefile` incluido en el proyecto:

- **Configuración e Inicio**: Configura el entorno, inicia los contenedores, ejecuta las pruebas y activa el DAG de Airflow.
  ```bash
  make all
  ```

- **Ejecutar Trabajo de Streaming**: Inicia el proceso de streaming de Spark (ejecutar en una terminal separada).
  ```bash
  make stream
  ```

- **Detener Servicios**:
  ```bash
  make down
  ```

Ejecuta `make help` para ver todos los comandos disponibles.

## Ejecución

1. **Arranca los servicios con Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Configura el entorno local**:
   Crea y activa el entorno virtual, luego instala las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecuta las pruebas unitarias**:
   ```bash
   python3 -m unittest discover -s tests
   ```
   ![tests](visuals/tests.png)

4. **Activa el DAG de Airflow**:
   - Accede a la interfaz de Airflow en [http://localhost:8080](http://localhost:8080).
   - Busca el DAG llamado `user_automation` y actívalo para que Kafka comience a recibir datos.
   - Revisa los mensajes que llegan al topic desde el Confluent Control Center en [http://localhost:9021](http://localhost:9021)
      ![control_center](visuals/control_center.png)

5. **Inicia el procesamiento de datos en tiempo real con Spark**:
   Abre una nueva terminal, activa el entorno y ejecuta el script:
   ```bash
   source venv/bin/activate
   python3 spark_stream.py
   ```

6. **Conéctate a Cassandra**:
   ```bash
   docker exec -it cassandra cqlsh
   ```

   Comandos útiles dentro de `cqlsh`:
   ```sql
   DESCRIBE KEYSPACES;
   USE spark_streams;
   DESCRIBE TABLES;
   SELECT * FROM created_users LIMIT 10;
   ```

7. **Accede al Dashboard de Grafana**:
   Abre tu navegador y ve a: [http://localhost:3000](http://localhost:3000).
   
   - **Usuario**: `admin`
   - **Contraseña**: `admin`

   El dashboard "User Registration Dashboard" debería estar disponible en la carpeta por defecto.


## Estructura
   ```bash
dataeng-project/
├── dags/                      # DAGs de Airflow
│   └── kafka_stream.py        
├── grafana/                   # Configuración de Grafana
│   ├── dashboards/            # Definiciones JSON de Dashboards
│   └── provisioning/          # Aprovisionamiento para dashboards y datasources
├── script/                   # Scripts de utilidad
│   └── entrypoint.sh         
├── tests/                    # Tests unitarios del proyecto
│   ├── test_api_health.py     
│   ├── test_cassandra.py      
│   ├── test_spark_stream.py   
├── venv/                     # Entorno virtual
├── docker-compose.yml        # Configuración de Docker Compose para los servicios
├── Dockerfile-spark          # Dockerfile para configuración de Spark
├── README.es.md              # Documentación del proyecto en español
├── README.md                 # Documentación del proyecto en inglés
├── requirements.txt          # Dependencias de Python
└── spark_stream.py           # Lógica de Spark Streaming
   ```
