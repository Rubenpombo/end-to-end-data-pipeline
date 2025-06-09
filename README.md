# End-to-End Data Streaming Lifecycle

📄 Versión en español disponible en [README.es.md](README.es.md)

## **Summary**
This project demonstrates the complete lifecycle of data streaming, from data ingestion to visualization. It captures user data from an external API, processes it in real-time using **Apache Kafka** and **Apache Spark**, stores it in a **Cassandra** database, and visualizes it through an interactive dashboard built with **Flask** and **Plotly**. The pipeline is orchestrated using **Apache Airflow**, ensuring automation and reliability.

The goal of this project is to showcase my ability to design, develop, and maintain robust data pipelines while providing clear and impactful visualizations for decision-making.

## **Technologies Used**
- **Apache Kafka**: Used for real-time data ingestion and streaming.
- **Apache Spark**: Processes the data in real-time, transforming and structuring it for storage.
- **Cassandra**: Serves as the storage layer for processed data, leveraging its distributed NoSQL capabilities.
- **Flask**: Provides a lightweight web framework for building the dashboard and API endpoints.
- **Plotly**: Used for creating interactive and visually appealing data visualizations.
- **Apache Airflow**: Orchestrates the entire pipeline, automating the execution of tasks.
- **Docker Compose**: Manages the deployment of all services in isolated containers for easy setup and scalability.

## Execution

1. Start the required services:
   ```bash
   docker-compose up -d
   ```

2. Run unit tests:
   ```bash
   python -m unittest discover -s tests
   ```

   You can access:
   - Airflow at [http://localhost:8080](http://localhost:8080) 
   - Control Center at [http://localhost:9021](http://localhost:9021)

3. Connect to Cassandra:
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

4. Start the dashboard:
   ```bash
   python3 dashboard.py
   ```
   Then open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)


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