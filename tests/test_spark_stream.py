import json
import unittest

import pytest
from pyspark.sql import SparkSession
from spark_stream import create_selection_df_from_kafka

EXPECTED_COLUMNS = {
    "id", "first_name", "last_name", "gender", "address", "email",
    "username", "password", "dob", "registered_date", "phone",
    "picture", "nationality", "ingested_at",
}

SAMPLE_MESSAGE = {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "first_name": "John",
    "last_name": "Doe",
    "gender": "male",
    "address": {
        "street": "42 Main St",
        "city": "Springfield",
        "state": "Illinois",
        "country": "United States",
        "postcode": "62701",
        "coordinates": {"latitude": "39.7817", "longitude": "-89.6501"},
        "timezone": {"offset": "-6:00",
                     "description": "Central Time (US & Canada)"},
    },
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "deadbeef",
    "dob": "1990-05-15",
    "registered_date": "2015-03-10",
    "phone": "555-1234",
    "picture": "https://randomuser.me/api/portraits/men/1.jpg",
    "nationality": "US",
}


@pytest.mark.unit
class TestSparkStream(unittest.TestCase):
    def setUp(self):
        """
        Set up a Spark session for testing.
        """
        self.spark = SparkSession.builder \
            .appName("TestSpark") \
            .master("local[1]") \
            .getOrCreate()

    def tearDown(self):
        """
        Stop the Spark session after tests.
        """
        self.spark.stop()

    def parse(self, message):
        df = self.spark.createDataFrame([{"value": json.dumps(message)}],
                                        schema=["value"])
        return create_selection_df_from_kafka(df)

    def test_create_selection_df_from_kafka(self):
        """
        Test that the function parses Kafka messages into a structured DataFrame.
        """
        result_df = self.parse(SAMPLE_MESSAGE)
        self.assertEqual(result_df.count(), 1)  # Ensure one record is parsed
        self.assertIn("id", result_df.columns)  # Ensure 'id' column exists

    def test_full_schema_is_parsed(self):
        """
        Every field of the data contract must be present after parsing.
        """
        result_df = self.parse(SAMPLE_MESSAGE)
        self.assertEqual(set(result_df.columns), EXPECTED_COLUMNS)

        row = result_df.first()
        self.assertEqual(row["id"], SAMPLE_MESSAGE["id"])
        self.assertEqual(row["first_name"], "John")
        self.assertEqual(row["email"], "john.doe@example.com")
        self.assertEqual(row["nationality"], "US")

    def test_address_is_serialized_as_json_string(self):
        """
        The nested address struct must be serialized to a JSON string so it
        matches the `address TEXT` column in Cassandra.
        """
        result_df = self.parse(SAMPLE_MESSAGE)
        self.assertEqual(dict(result_df.dtypes)["address"], "string")

        address = json.loads(result_df.first()["address"])
        self.assertEqual(address["city"], "Springfield")
        self.assertEqual(address["postcode"], "62701")
        self.assertEqual(address["coordinates"]["latitude"], "39.7817")
        self.assertEqual(address["timezone"]["offset"], "-6:00")

    def test_ingested_at_is_set_at_processing_time(self):
        """
        Lineage metadata is added by Spark, not by the Kafka producer.
        """
        result_df = self.parse(SAMPLE_MESSAGE)
        self.assertIsNotNone(result_df.first()["ingested_at"])


if __name__ == '__main__':
    unittest.main()
