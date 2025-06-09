from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
# from airflow.operators.bash_operator import BashOperator


default_args = {
    'owner': 'airscholar',
    'start_date': datetime(2025, 5, 4, 10, 00), # 4th May 2025
}


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
    import time
    import logging

    # Configure producer with specific settings to handle DNS issues
    producer = KafkaProducer(
        bootstrap_servers=['broker:29092'], # localhost because the script is executed locally
        client_id='user-producer',
        security_protocol="PLAINTEXT",
        connections_max_idle_ms=5000
    )

    current_time = time.time()

    while True:
        if time.time() > current_time + 60: # Stop after 60 seconds
            break
        try:
            res = get_data()
            if res is not None:  # Ensure res is not None before formatting
                res = format_data(res)
                producer.send('users_created', json.dumps(res).encode('utf-8'))

        except Exception as e:
            logging.error(f"Error sending message: {e}")
            continue
    

with DAG('user_automation',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False,) as dag:
    
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

    # spark_stream_task = BashOperator(
    #     task_id='run_spark_stream',
    #     bash_command='python3 /home/ruben/Documentos/side_projects/dataeng-project/spark_stream.py'
    # )

    # Set task dependencies
    # streaming_task >> spark_stream_task

