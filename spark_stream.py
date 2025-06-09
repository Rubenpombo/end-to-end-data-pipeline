import logging
import sys
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType
import os

if not os.path.exists('/tmp/checkpoint'):
    try:
        os.makedirs('/tmp/checkpoint')
    except Exception as e:
        logging.error(f"Failed to create checkpoint directory: {e}")
        sys.exit(1)  # Exit with an error code for Airflow to detect failure

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_keyspace(session):
    """
    Creates a Cassandra keyspace if it doesn't already exist.
    The keyspace is used to store data processed by Spark.
    """
    try:
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS spark_streams
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
        """)
        logging.info("Keyspace 'spark_streams' created successfully.")
    except Exception as e:
        logging.error(f"Failed to create keyspace: {e}")




def create_table(session):
    """
    Creates a table in the Cassandra keyspace to store user data.
    The table schema matches the fields extracted from Kafka messages.
    """
    try:
        session.execute("""
            CREATE TABLE IF NOT EXISTS spark_streams.created_users (
                id UUID PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                gender TEXT,
                address TEXT,
                email TEXT,
                username TEXT,
                password TEXT,
                dob TEXT,
                registered_date TEXT,
                phone TEXT,
                picture TEXT,
                nationality TEXT
            )
        """)
        logging.info("Table 'created_users' created successfully!")
    except Exception as e:
        logging.error(f"Failed to create table: {e}")


def insert_data(session, **kwargs):
    """
    Inserts a single user record into the Cassandra table.
    """

    print("Inserting data...")
    
    user_id = kwargs.get('id')
    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    gender = kwargs.get('gender')
    address = kwargs.get('address')
    email = kwargs.get('email')
    username = kwargs.get('username')
    password = kwargs.get('password')
    dob = kwargs.get('dob')
    registered_date = kwargs.get('registered_date')
    phone = kwargs.get('phone')
    picture = kwargs.get('picture')
    nationality = kwargs.get('nationality')

    try:
        session.execute("""
            INSERT INTO spark_streams.created_users(
                id, first_name, last_name, gender, address, email, username, password, 
                dob, registered_date, phone, picture, nationality
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        (user_id, first_name, last_name, gender, address, email, username, password, 
         dob, registered_date, phone, picture, nationality))
        logging.info(f"Data inserted for {first_name} {last_name}")
    except Exception as e:
        logging.error(f"Could not insert data due to {e}")


def create_spark_connection():
    """
    Creates a Spark session configured with the necessary packages for Cassandra and Kafka integration.
    """
    s_conn = None
    try:
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', 
                    "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
                    "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") \
            .config('spark.cassandra.connection.host', 'localhost') \
            .getOrCreate()
        
        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully.")
    except Exception as e:
        logging.error(f"Error creating Spark session: {e}")

    return s_conn


def connect_to_kafka(spark_conn):
    """
    Connects to a Kafka topic and creates a streaming DataFrame.
    The DataFrame contains raw messages from the Kafka topic.
    """

    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'localhost:9092') \
            .option('subscribe', 'users_created') \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("Kafka dataframe created successfully")
    except Exception as e:
        logging.warning(f"Kafka dataframe could not be created because: {e}")
    
    return spark_df


def create_cassandra_connection():
    """
    Establishes a connection to the Cassandra cluster.
    Returns a session object for executing queries.
    """

    try:
        cluster = Cluster(['localhost'], port=9042, load_balancing_policy=RoundRobinPolicy(), protocol_version=5)
        cas_session = cluster.connect() 
        return cas_session
    
    except Exception as e:
        logging.error(f"Error connecting to Cassandra: {e}")
        return None
    

def create_selection_df_from_kafka(spark_df):
    """
    Parses the raw Kafka messages into a structured DataFrame.
    The schema defines the fields to extract from the JSON messages.
    """

    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StructType([
            StructField("street", StringType(), False),
            StructField("city", StringType(), False),
            StructField("state", StringType(), False),
            StructField("country", StringType(), False),
            StructField("postcode", StringType(), False),
            StructField("coordinates", StructType([
                StructField("latitude", StringType(), False),
                StructField("longitude", StringType(), False)
            ])),
            StructField("timezone", StructType([
                StructField("offset", StringType(), False),
                StructField("description", StringType(), False)
            ]))
        ])),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("password", StringType(), False),
        StructField("dob", StringType(), False),  # Solo la fecha
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False),
        StructField("nationality", StringType(), False)
    ])
    
    sel = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select("data.*")

    return sel


if __name__ == "__main__":
    try:
        spark_conn = create_spark_connection()

        if spark_conn is not None:
            spark_df = connect_to_kafka(spark_conn)

            selection_df = create_selection_df_from_kafka(spark_df)

            cassandra_conn = create_cassandra_connection()

            if cassandra_conn is not None:
                create_keyspace(cassandra_conn)
                create_table(cassandra_conn)

                # insert_data(cassandra_conn)

                try:
                    logging.info("Starting streaming query to write data to Cassandra...")
                    streaming_query = (selection_df.writeStream.format("org.apache.spark.sql.cassandra")
                                       .option('checkpointLocation', '/tmp/checkpoint')
                                       .option('keyspace', 'spark_streams')
                                       .option('table', 'created_users')
                                       .start())
                    streaming_query.awaitTermination()

                except Exception as e:
                    logging.error(f"Streaming query failed: {e}")
                    sys.exit(1)  # Exit with an error code for Airflow to detect failure
                finally:
                    cassandra_conn.shutdown()
                    logging.info("Cassandra connection closed.")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        sys.exit(1)  # Exit with an error code for Airflow to detect failure
