# End-to-End Data Streaming Lifecycle

📄 Versión en español disponible en [README.es.md](README.es.md)

## **Summary**
This project demonstrates the complete lifecycle of data streaming, from data ingestion to visualization. It captures user data from an external API, processes it in real-time using **Apache Kafka** and **Apache Spark**, stores it in a **Cassandra** database, and visualizes it through an interactive dashboard built with **Flask** and **Plotly**. The pipeline is orchestrated using **Apache Airflow**, ensuring automation and reliability.

The goal of this project is to showcase my ability to design, develop, and maintain robust data pipelines while providing clear and impactful visualizations for decision-making.

## **Technologies Used**

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/docker/docker-original.svg" width="25" height="25" /> **Docker Compose**: Manages the deployment of all services in isolated containers for easy setup and scalability.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apacheairflow/apacheairflow-original.svg" width="25" height="25" /> **Apache Airflow**: Orchestrates the entire pipeline, automating the execution of tasks.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachekafka/apachekafka-original.svg" width="25" height="25" /> **Apache Kafka**: Used for real-time data ingestion and streaming.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/apachespark/apachespark-original.svg" width="25" height="25" /> **Apache Spark**: Processes the data in real-time, transforming and structuring it for storage.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/cassandra/cassandra-original.svg" width="25" height="25" /> **Cassandra**: Serves as the storage layer for processed data, leveraging its distributed NoSQL capabilities.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/flask/flask-original.svg" width="25" height="25" /> **Flask**: Provides a lightweight web framework for building the dashboard and API endpoints.

- <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/plotly/plotly-original.svg" width="25" height="25" /> **Plotly**: Used for creating interactive and visually appealing data visualizations.



## Execution

1. **Start the required services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Run unit tests**:
   ```bash
   python3 -m unittest discover -s tests
   ```

3. **Activate the Airflow DAG**:
   - Access the Airflow interface at [http://localhost:8080](http://localhost:8080).
   - Look for the DAG named `kafka_stream` and activate it so Kafka starts receiving data.
   - Check the messages arriving at the topic from the Confluent Control Center at [http://localhost:9021](http://localhost:9021).

4. **Start real-time data processing with Spark**:
   ```bash
   python3 spark_stream.py
   ```

5. **Connect to Cassandra**:
   ```bash
   docker exec -it cassandra cqlsh
   ```

   Useful commands inside `cqlsh`:
   ```sql
   DESCRIBE KEYSPACES;
   USE spark_streams;
   DESCRIBE TABLES;
   SELECT * FROM created_users LIMIT 10;
   ```

6. **Start the dashboard locally**:
   ```bash
   python3 dashboard.py
   ```

   Then open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000).


## Structure
   ```bash
dataeng-project/
├── dags/                      # Airflow DAGs
│   └── kafka_stream.py        
├── script/                   # Utility scripts
│   └── entrypoint.sh         
├── templates/                # HTML templates for Flask
│   └── index.html             
├── tests/                    # Unit tests for the project
│   ├── test_api_health.py     
│   ├── test_cassandra.py      
│   ├── test_dashboard.py      
│   └── test_spark_stream.py   
├── venv/                     # Virtual environment
├── dashboard.py              # Flask application for data visualization
├── docker-compose.yml        # Docker Compose configuration for services
├── Dockerfile-spark          # Dockerfile for Spark setup
├── README.es.md              # Project documentation in Spanish
├── README.md                 # Project documentation in English
├── requirements.txt          # Python dependencies
└── spark_stream.py           # Spark streaming logic
```