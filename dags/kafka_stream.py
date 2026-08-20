from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import time


default_args = {
    'owner': 'rubenpombo',
    'start_date': datetime(2025, 5, 4, 10, 00),  # 4th May 2025
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

STREAM_DURATION_SECONDS = 120


def get_data():
    import requests
    import logging

    try:
        res = requests.get("https://randomuser.me/api/", timeout=10)
        res.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        res = res.json()

        # Check if 'results' key exists and is not empty
        if 'results' in res and len(res['results']) > 0:
            return res['results'][0]
        else:
            logging.error("API response does not contain 'results' or is empty.")
            logging.error(f"API response: {res}")
            return None
    except Exception as e:
        logging.error(f"Error fetching data from API: {e}")
        return None


def format_data(res):
    """
    Format the API response data into a structured dictionary 
    with only the relevant fields needed for our pipeline.
    """
    data = {
        'id': res['login']['uuid'],
        'first_name': res['name']['first'],
        'last_name': res['name']['last'],
        'gender': res['gender'],
        'address': {
            'street': f"{res['location']['street']['number']} {res['location']['street']['name']}",
            'city': res['location']['city'],
            'state': res['location']['state'],
            'country': res['location']['country'],
            'postcode': str(res['location']['postcode']),
            'coordinates': {
                'latitude': res['location']['coordinates']['latitude'],
                'longitude': res['location']['coordinates']['longitude']
            },
            'timezone': {
                'offset': res['location']['timezone']['offset'],
                'description': res['location']['timezone']['description']
            }
        },
        'email': res['email'],
        'username': res['login']['username'],
        'password': res['login']['sha256'],  
        'dob': res['dob']['date'][:10],  
        'registered_date': res['registered']['date'][:10],  
        'phone': res['phone'],
        'picture': res['picture']['large'],
        'nationality': res['nat']
    }
    
    return data

def stream_data():
    import json
    from kafka import KafkaProducer
    import logging
    import os

    kafka_host = os.getenv('KAFKA_HOST', 'broker:29092')
    # Configure producer with specific settings to handle DNS issues
    producer = KafkaProducer(
        bootstrap_servers=[kafka_host],
        client_id='user-producer',
        security_protocol="PLAINTEXT",
        connections_max_idle_ms=5000
    )

    current_time = time.time()

    try:
        while True:
            if time.time() > current_time + STREAM_DURATION_SECONDS:
                break
            try:
                res = get_data()
                if res is not None:  # Ensure res is not None before formatting
                    res = format_data(res)
                    producer.send('users_created', json.dumps(res).encode('utf-8'))
                    time.sleep(0.5)

            except Exception as e:
                logging.error(f"Error sending message: {e}")
                continue
    finally:
        producer.close()
        logging.info("Kafka producer closed.")

    

dag_doc_md = """
### user_automation

Bounded-streaming ingestion demo: on each run, the DAG fetches random users
from the [RandomUser API](https://randomuser.me/) and produces them to the
Kafka topic `users_created` for a 120-second window (~2 msg/s), then stops.

The daily schedule simply re-triggers this ingestion window; the continuous
part of the pipeline lives in the Spark Structured Streaming job
(`spark_stream.py`), which consumes the topic and writes to Cassandra.
"""

with DAG('user_automation',
         default_args=default_args,
         description='Ingest RandomUser API data into Kafka (bounded streaming demo)',
         schedule='@daily',
         catchup=False,
         tags=['streaming', 'kafka', 'demo'],
         doc_md=dag_doc_md) as dag:

    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data,
        execution_timeout=timedelta(minutes=5)
    )
